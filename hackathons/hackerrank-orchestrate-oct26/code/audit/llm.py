"""Resilient multi-provider LLM caller shared by media transcription and intent classification.

Each call walks a chain of (provider, model) pairs:
  1. Gemini models (GEMINI_MODELS, comma-separated, or DEFAULT_MODELS) when GEMINI_API_KEY is set;
  2. then any OpenAI-compatible provider whose key is set: Mistral (MISTRAL_API_KEY), Groq (GROQ_API_KEY),
     NVIDIA NIM (NVIDIA_API_KEY). Model names are overridable via <PROVIDER>_TEXT_MODEL / _VISION_MODEL.
Errors: 503 / 429 / 500 / timeouts -> retry the same model with short exponential backoff, then move on;
400 / 401 / 403 / 404 (model retired, not enabled for the key) -> that model is dropped for the run.
Callers cache every success immediately, so a run that loses its LLMs part-way keeps its progress.
The run only stops asking when every model is dead, or after MAX_STRIKES consecutive items on which
the whole chain failed.
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request

from . import usage

DEFAULT_MODELS = ["gemini-flash-latest", "gemini-3.8-flash", "gemini-3.5-flash",
                  "gemini-3-flash-preview", "gemini-flash-lite-latest", "gemini-2.5-flash"]
# provider -> (base url, key env var, default text model, default vision model)
OPENAI_COMPAT = {
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL_API_KEY", "mistral-small-latest", "mistral-small-latest"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "llama-3.3-70b-versatile",
             "meta-llama/llama-4-scout-17b-16e-instruct"),
    "nvidia": ("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", "nvidia/nemotron-3-ultra-550b-a55b",
               "meta/llama-3.2-90b-vision-instruct"),
}
RETRIES_PER_MODEL = 3
BACKOFF_S = 2.0
TIMEOUT_S = 90
MAX_STRIKES = 3


def any_key() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY")) or any(os.environ.get(k) for _, k, _, _ in OPENAI_COMPAT.values())


def model_chain(preferred: str | None = None, vision: bool = False) -> list[tuple[str, str]]:
    chain = []
    if os.environ.get("GEMINI_API_KEY"):
        env = [m.strip() for m in os.environ.get("GEMINI_MODELS", "").split(",") if m.strip()]
        chain += [("gemini", m) for m in ([preferred] if preferred else []) + (env or DEFAULT_MODELS)]
    for name, (_, key_var, text_model, vision_model) in OPENAI_COMPAT.items():
        if os.environ.get(key_var):
            var = f"{name.upper()}_{'VISION' if vision else 'TEXT'}_MODEL"
            chain.append((name, os.environ.get(var) or (vision_model if vision else text_model)))
    return list(dict.fromkeys(chain))


class HTTPStatusError(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(f"{code}: {msg}")
        self.code = code


def _status(exc: Exception) -> int:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code if isinstance(code, int) else 0


class LLMChain:
    def __init__(self, preferred: str | None = None, tag: str = "llm", vision: bool = False):
        self.models = model_chain(preferred, vision)
        self.dead: set[tuple[str, str]] = set()
        self.strikes = 0
        self.tag = tag
        self._gemini = None

    @property
    def available(self) -> bool:
        return self.strikes < MAX_STRIKES and any(m not in self.dead for m in self.models)

    def generate(self, prompt: str, purpose: str, image: bytes | None = None, json_mode: bool = False):
        """Returns (text, "provider:model") or raises RuntimeError once the whole chain failed for this item."""
        last = None
        for provider, model in self.models:
            if (provider, model) in self.dead:
                continue
            for attempt in range(RETRIES_PER_MODEL):
                try:
                    call = self._call_gemini if provider == "gemini" else self._call_openai_compat
                    text, tin, tout = call(provider, model, prompt, image, json_mode)
                    usage.record(provider, model, purpose, tin, tout)
                    self.strikes = 0
                    return text, f"{provider}:{model}"
                except Exception as exc:
                    last = exc
                    code = _status(exc)
                    if code in (400, 401, 403, 404, 422):
                        print(f"[{self.tag}] {provider}:{model} rejected ({code}); dropping it for this run")
                        self.dead.add((provider, model))
                        break
                    if attempt + 1 < RETRIES_PER_MODEL:
                        time.sleep(BACKOFF_S * 2 ** attempt)
            else:
                print(f"[{self.tag}] {provider}:{model} still failing ({_status(last) or type(last).__name__}); trying next model")
        self.strikes += 1
        if not self.available:
            print(f"[{self.tag}] LLM chain exhausted ({type(last).__name__}: {str(last)[:90]}); "
                  f"falling back for the rest of this run")
        raise RuntimeError(f"all models failed: {str(last)[:120]}")

    def _call_gemini(self, provider, model, prompt, image, json_mode):
        from google import genai
        from google.genai import types

        if self._gemini is None:
            self._gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        contents = [types.Part.from_bytes(data=image, mime_type="image/png"), prompt] if image else prompt
        config = types.GenerateContentConfig(temperature=0, **({"response_mime_type": "application/json"} if json_mode else {}))
        resp = self._gemini.models.generate_content(model=model, contents=contents, config=config)
        um = getattr(resp, "usage_metadata", None)
        return (resp.text or "", getattr(um, "prompt_token_count", 0) or 0,
                getattr(um, "candidates_token_count", 0) or 0)

    def _call_openai_compat(self, provider, model, prompt, image, json_mode):
        base, key_var, _, _ = OPENAI_COMPAT[provider]
        content = prompt
        if image:
            content = [{"type": "text", "text": prompt},
                       {"type": "image_url",
                        "image_url": {"url": "data:image/png;base64," + base64.b64encode(image).decode()}}]
        body = {"model": model, "temperature": 0, "messages": [{"role": "user", "content": content}]}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
            body["messages"][0]["content"] = (content if image else prompt + "\n\nRespond with JSON only.")
        req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {os.environ[key_var]}",
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise HTTPStatusError(e.code, e.read()[:200].decode(errors="replace")) from None
        text = data["choices"][0]["message"].get("content") or ""
        u = data.get("usage") or {}
        return _strip_fence(text) if json_mode else text, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def _strip_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t[3:]
        t = t.rsplit("```", 1)[0]
    return t.strip()
