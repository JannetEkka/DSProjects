"""Tests for reply validation and the decision rule. No network."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import validate as v  # noqa: E402
from decide import decide, numbers_in_text, quote_in_headlines  # noqa: E402

HEADLINES = {
    "H001": "Apple cut its fiscal first quarter revenue forecast from $89-$93 billion to $84 billion due to weaker demand in China.",
    "H002": "Yields on long-dated U.S. Treasury securities hit their lowest levels in nearly a year.",
}
FIGS = {"week_open": 41.74, "week_close": 36.98, "week_high": 42.24, "week_low": 35.5,
        "week_change_pct": -11.4}
OK = {"verdict": "supported", "quote": "Apple cut its fiscal first quarter revenue forecast", "reason": ""}


def claim(**kw):
    base = {"text": "Apple cut its revenue forecast to $84 billion.", "kind": "news",
            "headline_ids": ["H001"], "numbers": []}
    base.update(kw)
    return base


# ---- reply validation ----------------------------------------------------
@pytest.mark.parametrize("text,label", [('{"label": -1}', -1), ('{"label":0}', 0),
                                        ('```json\n{"label": 1}\n```', 1),
                                        ('Sure. {"label": 1} Hope that helps', 1)])
def test_label_accepts_allowed_values(text, label):
    assert v.parse_label(text) == label


@pytest.mark.parametrize("text", ["", "positive", '{"label": 2}', '{"label": "1"}',
                                  '{"label": true}', '{"label": 0.5}', '{"sentiment": 1}',
                                  '{"label": 1'])
def test_label_rejects_everything_else(text):
    with pytest.raises(v.BadReply):
        v.parse_label(text)


def test_claims_shape():
    out = v.parse_claims('{"claims":[{"text":"Shares fell 11.4% on the week.","kind":"price",'
                         '"headline_ids":[],"numbers":[{"metric":"week_change_pct","value":-11.4}]},'
                         '{"text":"Apple cut guidance.","kind":"news","headline_ids":["h001"]}]}')
    assert out[0]["numbers"] == [{"metric": "week_change_pct", "value": -11.4}]
    assert out[1]["headline_ids"] == ["H001"] and out[1]["numbers"] == []


@pytest.mark.parametrize("text", [
    '{"claims": []}',
    '{"claims": "none"}',
    '{"claims":[{"text":"","kind":"news","headline_ids":["H001"]}]}',
    '{"claims":[{"text":"x","kind":"opinion","headline_ids":["H001"]}]}',
    '{"claims":[{"text":"x","kind":"news","headline_ids":"H001"}]}',
    '{"claims":[{"text":"x","kind":"price","numbers":[{"metric":"pe_ratio","value":3}]}]}',
    '{"claims":[{"text":"x","kind":"price","numbers":[{"metric":"week_high","value":"42"}]}]}',
    '{"claims":[' + ",".join(['{"text":"x","kind":"news","headline_ids":["H001"]}'] * 9) + ']}',
])
def test_claims_rejects_bad_shapes(text):
    with pytest.raises(v.BadReply):
        v.parse_claims(text)


def test_verdict():
    assert v.parse_verdict('{"verdict":"supported","quote":"abc","reason":""}')["verdict"] == "supported"
    for bad in ['{"verdict":"yes"}', '{"verdict":"not_supported","reason":""}',
                '{"verdict":"supported","quote":5}', "supported"]:
        with pytest.raises(v.BadReply):
            v.parse_verdict(bad)


def test_sandbox_output_must_cover_every_week():
    good = '{"2019-01-06": {"week_open":1,"week_close":2,"week_high":3,"week_low":0.5,"week_change_pct":100}}'
    assert v.parse_sandbox(good, ["2019-01-06"])["2019-01-06"]["week_high"] == 3.0
    with pytest.raises(v.BadReply):
        v.parse_sandbox(good, ["2019-01-06", "2019-01-13"])
    with pytest.raises(v.BadReply):
        v.parse_sandbox('{"2019-01-06": {"week_open":1}}', ["2019-01-06"])
    with pytest.raises(v.BadReply):
        v.parse_sandbox("Traceback (most recent call last)", ["2019-01-06"])


# ---- the decision rule ---------------------------------------------------
def test_kept_when_all_three_hold():
    assert decide(claim(), HEADLINES, FIGS, OK)["keep"] is True


def test_checker_alone_cannot_keep_a_claim_with_an_invented_headline():
    d = decide(claim(headline_ids=["H001", "H999"]), HEADLINES, FIGS, OK)
    assert d == {"keep": False, "reason": "unknown_headline",
                 "detail": "No such headline this week: H999"}


def test_checker_alone_cannot_keep_a_wrong_number():
    c = claim(text="Shares fell 9.1% on the week.", kind="price", headline_ids=[],
              numbers=[{"metric": "week_change_pct", "value": -9.1}])
    d = decide(c, HEADLINES, FIGS, OK)
    assert d["keep"] is False and d["reason"] == "number_mismatch"


def test_right_number_is_kept_with_rounding():
    c = claim(text="Shares fell 11.4% to close at $36.98.", kind="price", headline_ids=[],
              numbers=[{"metric": "week_change_pct", "value": -11.4},
                       {"metric": "week_close", "value": 36.98}])
    assert decide(c, HEADLINES, FIGS, OK)["keep"] is True
    c["numbers"][1]["value"] = 37.5
    assert decide(c, HEADLINES, FIGS, OK)["reason"] == "number_mismatch"


def test_price_figure_in_text_but_not_declared_is_removed():
    c = claim(text="Shares fell 11.4%, touching $30.00 on Thursday.", kind="price", headline_ids=[],
              numbers=[{"metric": "week_change_pct", "value": -11.4}])
    assert decide(c, HEADLINES, FIGS, OK)["reason"] == "unverified_number"


def test_not_supported_removes():
    bad = {"verdict": "not_supported", "quote": "", "reason": "The headline says $84 billion, not $74 billion."}
    d = decide(claim(), HEADLINES, FIGS, bad)
    assert d["keep"] is False and d["reason"] == "not_supported" and "84" in d["detail"]


def test_supported_with_a_quote_that_is_not_in_the_headline_removes():
    fake = {"verdict": "supported", "quote": "Apple raised its forecast to a record", "reason": ""}
    assert decide(claim(), HEADLINES, FIGS, fake)["reason"] == "quote_not_found"


def test_no_verdict_removes():
    assert decide(claim(), HEADLINES, FIGS, None)["reason"] == "no_verdict"


def test_cites_nothing_removes():
    assert decide(claim(headline_ids=[]), HEADLINES, FIGS, OK)["reason"] == "cites_nothing"


def test_numbers_need_the_sandbox():
    c = claim(text="Shares fell 11.4%.", kind="price", headline_ids=[],
              numbers=[{"metric": "week_change_pct", "value": -11.4}])
    assert decide(c, HEADLINES, None, OK)["reason"] == "sandbox_unavailable"


def test_guardrail_removes_even_a_confirmed_claim():
    assert decide(claim(), HEADLINES, FIGS, OK, guardrail_flagged=True)["reason"] == "guardrail"


def test_helpers():
    assert numbers_in_text("fell 11.4% to $36.98, then 2 percent") == [11.4, 36.98, 2.0]
    assert quote_in_headlines("apple CUT its fiscal first quarter revenue forecast.", list(HEADLINES.values()))
    assert not quote_in_headlines("Apple", list(HEADLINES.values()))
    assert quote_in_headlines("Apple cut its fiscal first quarter revenue forecast... due to weaker demand in China",
                              list(HEADLINES.values()))
    assert not quote_in_headlines("Apple cut its fiscal first quarter revenue forecast... and raised its dividend",
                                  list(HEADLINES.values()))
