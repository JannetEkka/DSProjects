"""Calls to Meta's models: SAM 3.1, Muse Spark, Muse Voice Transcribe, and
Muse Spark Open (on Baseten) as an optional second model.

Written against the Meta Model API docs (dev.meta.ai/docs). The Model API is
OpenAI-compatible; plain httpx keeps the SAM stream and the voice upload simple.
"""

from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass

import httpx

META_BASE = os.environ.get("CHITHI_META_BASE", "https://api.meta.ai/v1")
BASETEN_BASE = os.environ.get("CHITHI_BASETEN_BASE", "https://inference.baseten.co/v1")

SPARK = os.environ.get("CHITHI_SPARK_MODEL", "muse-spark-1.3")
SAM = os.environ.get("CHITHI_SAM_MODEL", "sam-3.1")
VOICE = os.environ.get("CHITHI_VOICE_MODEL", "muse-voice-transcribe-1.0")
SPARK_OPEN = os.environ.get("CHITHI_SPARK_OPEN_MODEL", "meta-models/muse-spark-open-1026")

TIMEOUT = httpx.Timeout(120.0, connect=15.0)


class MetaError(RuntimeError):
    pass


def meta_key() -> str | None:
    return os.environ.get("META_HACK_API_KEY")


def baseten_key() -> str | None:
    return os.environ.get("META_HACK_BASETEN_API_KEY")


def data_url(image: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(image).decode()}"


def _headers(key: str | None) -> dict:
    if not key:
        raise MetaError("No API key: set META_HACK_API_KEY")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _post(path: str, body: dict, key: str | None = None, base: str = META_BASE) -> dict:
    r = httpx.post(f"{base}{path}", headers=_headers(key or meta_key()), json=body, timeout=TIMEOUT)
    if r.status_code >= 400:
        raise MetaError(f"{path} {r.status_code}: {r.text[:500]}")
    return r.json()


def output_text(resp: dict) -> str:
    """The text of a Responses API reply (what the SDK calls output_text)."""
    if isinstance(resp.get("output_text"), str):
        return resp["output_text"]
    parts = []
    for item in resp.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") in ("output_text", "text"):
                    parts.append(c.get("text", ""))
    return "".join(parts)


def usage(resp: dict) -> dict:
    return resp.get("usage") or {}


# --- SAM 3.1 -----------------------------------------------------------------

@dataclass
class Box:
    concept: str
    x1: int
    y1: int
    x2: int
    y2: int
    w: int  # size of the image SAM saw
    h: int
    score: float | None = None

    def as_dict(self) -> dict:
        return self.__dict__.copy()


_BOX = re.compile(r"<\|box;([^|]*)\|>")


def parse_sam(text: str, concept: str) -> list[Box]:
    """Boxes from SAM's token output, e.g.
    <0f>0<|box;x1=181;y1=365;x2=556;y2=486;w=1516;h=1600|><|mask;...|>
    Masks are left out: Chithi only needs the boxes."""
    boxes = []
    for m in _BOX.finditer(text):
        f = dict(kv.split("=", 1) for kv in m.group(1).split(";") if "=" in kv)
        try:
            boxes.append(Box(concept, int(f["x1"]), int(f["y1"]), int(f["x2"]), int(f["y2"]),
                             int(f["w"]), int(f["h"]), float(f["c"]) if "c" in f else None))
        except (KeyError, ValueError):
            continue
    return boxes


def segment(image: bytes, concept: str, mime: str = "image/jpeg") -> list[Box]:
    """SAM 3.1 boxes for one short noun phrase. One concept per request: the
    docs say lists of concepts return nothing."""
    body = {
        "model": SAM,
        "input": [{"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": concept},
            {"type": "input_image", "image_url": data_url(image, mime)},
        ]}],
        "metadata": {"include_confidence": "true", "mask_encoding": "one_bit"},
        "stream": True,
    }
    text = []
    with httpx.stream("POST", f"{META_BASE}/responses", headers=_headers(meta_key()), json=body, timeout=TIMEOUT) as r:
        if r.status_code >= 400:
            raise MetaError(f"sam {r.status_code}: {r.read()[:500]!r}")
        for line in r.iter_lines():
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            ev = json.loads(payload)
            if ev.get("type") == "response.output_text.delta":
                text.append(ev.get("delta", ""))
            elif ev.get("type") == "response.completed" and not text:
                text.append(output_text(ev.get("response", {})))
    return parse_sam("".join(text), concept)


# --- Muse Spark --------------------------------------------------------------

def spark(content: list[dict], *, instructions: str | None = None, schema: dict | None = None,
          model: str | None = None) -> tuple[str, dict]:
    body: dict = {"model": model or SPARK, "input": [{"type": "message", "role": "user", "content": content}]}
    if instructions:
        body["instructions"] = instructions
    if schema:
        body["text"] = {"format": {"type": "json_schema", "name": schema["title"], "schema": schema, "strict": True}}
    resp = _post("/responses", body)
    return output_text(resp), usage(resp)


def spark_open(messages: list[dict], *, schema: dict | None = None) -> tuple[str, dict]:
    """Muse Spark Open on Baseten (OpenAI chat-completions format)."""
    body: dict = {"model": SPARK_OPEN, "messages": messages, "max_tokens": 4096}
    if schema:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": schema["title"], "schema": schema, "strict": True}}
    resp = _post("/chat/completions", body, key=baseten_key(), base=BASETEN_BASE)
    return resp["choices"][0]["message"]["content"], resp.get("usage") or {}


# --- Muse Voice Transcribe ---------------------------------------------------

def transcribe(wav: bytes, language_bias: list[str] | None = None) -> str:
    """A spoken question (16 kHz mono 16-bit WAV, under 10 minutes) to text."""
    settings: dict = {"model": VOICE, "mode": "PUSH_TO_TALK", "audioEncoding": "WAV"}
    if language_bias:
        settings["languageBias"] = language_bias
    key = meta_key()
    if not key:
        raise MetaError("No API key: set META_HACK_API_KEY")
    r = httpx.post(f"{META_BASE}/asr/transcribe", headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
                   files={"request": (None, json.dumps(settings), "application/json"), "audio": ("q.wav", wav, "audio/wav")},
                   timeout=TIMEOUT)
    if r.status_code >= 400:
        raise MetaError(f"transcribe {r.status_code}: {r.text[:500]}")
    return r.json().get("transcript", "")
