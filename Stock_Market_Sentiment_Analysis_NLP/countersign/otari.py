"""The only door to a model in Countersign: Mozilla's Otari gateway.

Every model call, sandbox run, web fetch and guardrail check in this project
goes to https://api.otari.ai/api/v1 with one API key (OTARI_API_KEY). There is
no direct call to any model provider anywhere in the code.

What this module does besides sending the request:
- keeps each request short (one headline or one claim per call, 28 s timeout,
  because the hosted gateway is reported to answer 504 after about 30 s);
- reads Otari's response headers (which provider and model answered, whether a
  fallback fired, the guardrail verdict) and the cost of the call;
- turns Otari's two deliberate refusals into their own exceptions, so the
  pipeline can stop cleanly on a budget refusal and remove a claim on a
  guardrail block instead of treating them as crashes;
- writes every call to a log (no prompt text, no key) that the results page
  and the README numbers are built from.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import requests

BASE_URL = os.environ.get("OTARI_BASE_URL", "https://api.otari.ai/api/v1")

# Open-weight models, picked from the account's model list on 2026-11-11.
# The writer is called through a routing policy, not by its model id.
CLASSIFIER_MODEL = "openai/gpt-oss-120b"  # OpenAI open-weight family
WRITER_POLICY = "countersign-writer"  # gpt-oss-120b, falls back to Mistral Small 3.2
WRITER_MAIN_MODEL = "openai/gpt-oss-120b"
WRITER_FALLBACK_MODEL = "mistralai/mistral-small-3.2-24b-instruct-2506"
CHECKER_MODEL = "alibaba/qwen3-235b-a22b-instruct-2507"  # Qwen family: not the writer's
FALLBACK_DRILL_POLICY = "countersign-fallback-drill"  # main model's provider answers 404

TIMEOUT_S = 28
SANDBOX_PRICE_USD = 0.01  # what one /code/execute run cost on the account's usage page


class OtariError(RuntimeError):
    def __init__(self, status: int, code: str, detail: str):
        super().__init__(f"Otari {status} {code}: {detail}")
        self.status, self.code, self.detail = status, code, detail


class BudgetRefused(OtariError):
    """403 budget_exceeded: the key's spending cap refused the request."""


class GuardrailBlocked(OtariError):
    """403 guardrail_violation: a blocking guardrail flagged the input."""


@dataclass
class Reply:
    text: str
    model_asked: str
    model_served: str
    provider: str
    fallback: bool
    attempts: int
    cost_usd: float
    request_id: str
    guardrails: list[dict] = field(default_factory=list)


class Otari:
    def __init__(self, log_path: str | None = None):
        # In a cloud session the network proxy adds the real key to requests
        # for api.otari.ai, so a placeholder is fine there. On a laptop, set
        # OTARI_API_KEY to the key named `countersign`.
        key = os.environ.get("OTARI_API_KEY", "proxy-injected")
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        )
        self.log_path = log_path
        self._lock = threading.Lock()
        self.calls: list[dict] = []

    # ---- plumbing -------------------------------------------------------
    def _log(self, row: dict) -> None:
        row["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._lock:
            self.calls.append(row)
            if self.log_path:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")

    def _post(self, path: str, body: dict, purpose: str, retries: int = 2) -> requests.Response:
        last: Exception | None = None
        for attempt in range(retries + 1):
            try:
                r = self.session.post(BASE_URL + path, json=body, timeout=TIMEOUT_S)
            except requests.RequestException as e:  # timeout, reset
                last = e
                time.sleep(1.5 * (attempt + 1))
                continue
            if r.status_code == 200:
                return r
            code = r.headers.get("Otari-Error-Code", "")
            try:
                payload = r.json()
            except ValueError:
                payload = {}
            detail = str(payload.get("detail", r.text[:300]))
            code = code or str(payload.get("code", ""))
            if r.status_code == 403 and code == "budget_exceeded":
                self._log({"purpose": purpose, "path": path, "status": 403, "code": code,
                           "detail": detail, "scope": r.headers.get("Otari-Budget-Scope", ""),
                           "request_id": r.headers.get("Otari-Request-Id", "")})
                raise BudgetRefused(403, code, detail)
            if r.status_code == 403 and (code == "guardrail_violation" or "guardrail" in detail.lower()):
                self._log({"purpose": purpose, "path": path, "status": 403,
                           "code": "guardrail_violation", "detail": detail,
                           "request_id": r.headers.get("Otari-Request-Id", "")})
                raise GuardrailBlocked(403, "guardrail_violation", detail)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                last = OtariError(r.status_code, code, detail)
                time.sleep(2.0 * (attempt + 1))
                continue
            self._log({"purpose": purpose, "path": path, "status": r.status_code,
                       "code": code, "detail": detail[:200]})
            raise OtariError(r.status_code, code, detail)
        self._log({"purpose": purpose, "path": path, "status": 0, "code": "network",
                   "detail": str(last)[:200]})
        raise OtariError(0, "network", str(last))

    # ---- the four things Countersign asks Otari for ---------------------
    def chat(self, model: str, system: str, user: str, purpose: str, max_tokens: int = 600,
             guardrails: list[dict] | None = None, temperature: float = 0.0) -> Reply:
        """One chat completion. `model` is a model id or a routing policy name."""
        body: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if guardrails:
            body["guardrails"] = guardrails
        r = self._post("/chat/completions", body, purpose)
        data = r.json()
        try:
            text = data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            text = ""
        usage = data.get("usage") or {}
        try:
            cost = float(usage.get("cost_usd") or 0)
        except (TypeError, ValueError):
            cost = 0.0
        try:
            verdicts = json.loads(r.headers.get("Otari-Guardrails", "[]"))
        except ValueError:
            verdicts = []
        reply = Reply(
            text=text, model_asked=model,
            model_served=r.headers.get("Otari-Model", ""),
            provider=r.headers.get("Otari-Provider", ""),
            fallback=r.headers.get("Otari-Fallback", "false") == "true",
            attempts=int(r.headers.get("Otari-Attempt-Count", "1") or 1),
            cost_usd=cost, request_id=r.headers.get("Otari-Request-Id", ""),
            guardrails=verdicts,
        )
        self._log({"purpose": purpose, "path": "/chat/completions", "status": 200,
                   "model_asked": model, "model_served": reply.model_served,
                   "provider": reply.provider, "fallback": reply.fallback,
                   "attempts": reply.attempts, "cost_usd": cost,
                   "prompt_tokens": usage.get("prompt_tokens"),
                   "completion_tokens": usage.get("completion_tokens"),
                   "guardrails": verdicts, "request_id": reply.request_id})
        return reply

    def run_code(self, code: str, purpose: str, timeout_seconds: int = 20) -> dict:
        """Run Python in Otari's sandbox with no model involved."""
        r = self._post("/code/execute", {"code": code, "timeout_seconds": timeout_seconds}, purpose)
        data = r.json()
        self._log({"purpose": purpose, "path": "/code/execute", "status": 200,
                   "return_code": data.get("return_code"), "cost_usd": SANDBOX_PRICE_USD,
                   "request_id": r.headers.get("Otari-Request-Id", "")})
        return data

    def fetch(self, url: str, purpose: str, max_chars: int = 20000) -> dict:
        """Read one public page through Otari's web fetch."""
        r = self._post("/fetch", {"url": url, "max_chars": max_chars}, purpose)
        data = r.json()
        self._log({"purpose": purpose, "path": "/fetch", "status": 200, "url": url,
                   "chars": len(data.get("text") or ""),
                   "request_id": r.headers.get("Otari-Request-Id", "")})
        return data

    def key_budget(self) -> dict:
        r = self.session.get(BASE_URL + "/key/budget", timeout=TIMEOUT_S)
        return r.json() if r.status_code == 200 else {"error": r.status_code}

    def key_usage(self) -> dict:
        r = self.session.get(BASE_URL + "/key/usage/summary", timeout=TIMEOUT_S)
        return r.json() if r.status_code == 200 else {"error": r.status_code}

    def spent_usd(self) -> float:
        with self._lock:
            return round(sum(float(c.get("cost_usd") or 0) for c in self.calls), 6)


if __name__ == "__main__":
    # Smoke test: one short call to each of the two model families.
    o = Otari()
    for m in (CLASSIFIER_MODEL, CHECKER_MODEL):
        rep = o.chat(m, "Answer with one word.", "Say ok.", purpose="smoke", max_tokens=60)
        print(m, "->", repr(rep.text), "| served by", rep.provider, rep.model_served,
              "| cost $%.6f" % rep.cost_usd)
    print("key budget:", o.key_budget())
