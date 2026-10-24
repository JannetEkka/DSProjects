"""Media text extraction for screenshots (and scanned documents).

Order of preference:
  1. Gemini vision model (if GEMINI_API_KEY is set) - transcribes every visible field.
  2. Local RapidOCR (onnxruntime) - offline fallback, no key needed.
Results are cached by file SHA-256 in code/cache/media_text.json so reruns are free and
deterministic. Token usage of model calls is recorded via audit.usage.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from . import usage

CACHE = Path(__file__).resolve().parent.parent / "cache" / "media_text.json"

VLM_PROMPT = """You are transcribing an internal admin-console screenshot for a privacy deletion audit.
Transcribe ALL visible text faithfully, top to bottom, left to right. Preserve every identifier exactly
(resource ids like search_428 / backup_9287 / data_flow_1121, user ids like user_13, emails, phone numbers,
hashes, order ids, dates, statuses such as Enabled/Disabled/Healthy/Active/Blocked/Restore allowed).
For tables output one row per line with cells separated by ' | '. For key/value panels output 'key: value'.
Do not summarize, do not add commentary."""


class MediaExtractor:
    def __init__(self, prefer: str = "auto", model: str | None = None):
        self.prefer = prefer
        self.model = model or os.environ.get("GEMINI_VISION_MODEL", "gemini-2.5-flash")
        self.cache = {}
        if CACHE.exists():
            try:
                self.cache = json.loads(CACHE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.cache = {}
        self._ocr = None

    def _save(self):
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(self.cache, indent=1, sort_keys=True), encoding="utf-8")

    def extract(self, path: Path) -> str:
        """Cache layout: sha256 -> {"file": name, "engines": {engine_name: text}}. With a key the VLM
        transcription is used (computed once, then cached); offline runs use the local OCR entry."""
        data = Path(path).read_bytes()
        key = hashlib.sha256(data).hexdigest()
        entry = self.cache.setdefault(key, {"file": Path(path).name, "engines": {}})
        if "text" in entry:  # migrate old single-engine layout
            entry.setdefault("engines", {})[entry.pop("engine", "rapidocr")] = entry.pop("text")
            self._save()
        engines = entry["engines"]
        want_vlm = self.prefer in ("auto", "vlm") and bool(os.environ.get("GEMINI_API_KEY"))
        vlm_name = f"gemini:{self.model}"
        if want_vlm:
            if vlm_name in engines:
                usage.record_cache_hit("media")
                return engines[vlm_name]
            try:
                engines[vlm_name] = self._gemini(data, path)
                self._save()
                return engines[vlm_name]
            except Exception as exc:  # network / quota / auth problems -> fall back to OCR
                print(f"[media] Gemini unavailable ({type(exc).__name__}: {str(exc)[:90]}); using local OCR for the rest of this run")
                self.prefer = "ocr"  # circuit breaker
        if "rapidocr" in engines:
            usage.record_cache_hit("media")
            return engines["rapidocr"]
        engines["rapidocr"] = self._rapidocr(path)
        self._save()
        return engines["rapidocr"]

    def _gemini(self, data: bytes, path) -> str:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        resp = client.models.generate_content(
            model=self.model,
            contents=[types.Part.from_bytes(data=data, mime_type="image/png"), VLM_PROMPT],
            config=types.GenerateContentConfig(temperature=0),
        )
        um = getattr(resp, "usage_metadata", None)
        usage.record("gemini", self.model, "media_transcription",
                     getattr(um, "prompt_token_count", 0) or 0, getattr(um, "candidates_token_count", 0) or 0)
        return resp.text or ""

    def _rapidocr(self, path) -> str:
        if self._ocr is None:
            from rapidocr_onnxruntime import RapidOCR

            self._ocr = RapidOCR()
        result, _ = self._ocr(str(path))
        if not result:
            return ""
        # group boxes into lines by vertical position, then left-to-right
        boxes = sorted(((b[0][0][1], b[0][0][0], b[1]) for b in result))
        lines, cur, cur_y = [], [], None
        for y, x, t in boxes:
            if cur_y is None or abs(y - cur_y) <= 12:
                cur.append((x, t))
                cur_y = y if cur_y is None else cur_y
            else:
                lines.append(" | ".join(t for _, t in sorted(cur)))
                cur, cur_y = [(x, t)], y
        if cur:
            lines.append(" | ".join(t for _, t in sorted(cur)))
        return "\n".join(lines)
