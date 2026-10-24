"""Intent rule model, cached-answer reuse without a key, and the LLM circuit breaker."""
import hashlib

import pytest

from audit import llm
from audit.intent import IntentClassifier, rule_classify


@pytest.mark.parametrize("text, authorizes", [
    ("Please delete my account and all personal data.", True),
    ("Je demande la suppression définitive du compte.", True),
    ("Bitte schicken Sie mir eine Kopie meiner Daten.", False),
    ("Do not delete anything, I still use the account.", False),
    ("Please remove me from marketing lists only.", False),
    ("Can you send me a copy of my invoices?", False),
    ("", False),
    ("   \n\t ", False),
])
def test_rule_model(text, authorizes):
    assert rule_classify(text)["authorizes_deletion"] is authorizes


def test_empty_text_never_asks_a_model():
    clf = IntentClassifier(use_llm=True)
    r = clf.classify("  ")
    assert r["authorizes_deletion"] is False and r["engine"] == "rules"


def test_cached_answer_is_reused_without_a_key():
    clf = IntentClassifier(use_llm=True)
    assert not clf.use_llm  # no key in the environment
    text = "unit-test request: please erase my profile"
    clf.cache[hashlib.sha256(text.encode()).hexdigest()] = {
        "authorizes_deletion": True, "request_type": "DELETION", "language": "en", "rationale": "t",
        "model": "gemini:test-model"}
    r = clf.classify(text)
    assert r["engine"] == "gemini:test-model" and r["authorizes_deletion"] is True


def test_no_llm_flag_ignores_the_cache():
    clf = IntentClassifier(use_llm=False)
    text = "unit-test request: please erase my profile"
    clf.cache[hashlib.sha256(text.encode()).hexdigest()] = {"authorizes_deletion": False, "model": "x"}
    assert clf.classify(text)["engine"] == "rules"


def test_circuit_breaker(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-not-a-key")
    monkeypatch.setenv("GEMINI_MODELS", "m1,m2")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    chain = llm.LLMChain(tag="test")
    calls = []

    def fail(provider, model, prompt, image, json_mode):
        calls.append(model)
        raise llm.HTTPStatusError(503, "overloaded")
    monkeypatch.setattr(chain, "_call_gemini", fail)
    for _ in range(llm.MAX_STRIKES):
        assert chain.available
        with pytest.raises(RuntimeError):
            chain.generate("p", "test")
    assert not chain.available  # stops asking after MAX_STRIKES failed items
    assert calls.count("m1") == llm.MAX_STRIKES * llm.RETRIES_PER_MODEL


def test_rejected_model_is_dropped(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-not-a-key")
    monkeypatch.setenv("GEMINI_MODELS", "retired,good")
    chain = llm.LLMChain(tag="test")

    def call(provider, model, prompt, image, json_mode):
        if model == "retired":
            raise llm.HTTPStatusError(404, "not found")
        return '{"ok": true}', 1, 1
    monkeypatch.setattr(chain, "_call_gemini", call)
    assert chain.generate("p", "test") == ('{"ok": true}', "gemini:good")
    assert ("gemini", "retired") in chain.dead
