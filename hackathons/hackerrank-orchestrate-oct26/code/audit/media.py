"""Media text extraction for screenshots (and scanned documents).

Order of preference:
  1. A vision LLM - transcribes every visible field. Walks a model chain with retries (audit.llm):
     Gemini first, then Mistral / Groq / NVIDIA when their keys are set, so one bad model doesn't end the run.
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
from .llm import LLMChain, any_key

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
        self.chain = LLMChain(model or os.environ.get("GEMINI_VISION_MODEL"), tag="media", vision=True)
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
        if self.prefer in ("auto", "vlm"):
            # a cached VLM transcription is reused with or without a key, so a re-run anywhere
            # reproduces the run that produced output.csv; preference order is deterministic
            cached = sorted(n for n in engines if n != "rapidocr")
            if cached:
                usage.record_cache_hit("media")
                return engines[cached[0]]
        if self.prefer in ("auto", "vlm") and any_key():
            if self.chain.available:
                try:
                    text, engine = self.chain.generate(VLM_PROMPT, "media_transcription", image=data)
                    engines[engine] = text
                    self._save()
                    return text
                except RuntimeError:  # whole model chain failed for this file -> local OCR for this one
                    pass
        if "rapidocr" in engines:
            usage.record_cache_hit("media")
            return engines["rapidocr"]
        engines["rapidocr"] = self._rapidocr(path)
        self._save()
        return engines["rapidocr"]

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
