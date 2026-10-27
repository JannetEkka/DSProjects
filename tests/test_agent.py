"""The whole pipeline on a sample letter, with the stand-in models."""

import json
from pathlib import Path

import pytest

from chithi import agent
from chithi.mock import MockBackend

OUT = Path(__file__).parent.parent / "letters" / "out"


@pytest.mark.skipif(not (OUT / "elec-000.json").exists(), reason="run letters/generate.py first")
@pytest.mark.parametrize("repair", [False, True])
def test_wrong_values_never_reach_verified(repair):
    truth = json.loads((OUT / "elec-000.json").read_text())
    photo = (OUT / "elec-000.photo.jpg").read_bytes()
    res = agent.run(photo, "bn", MockBackend(truth, error_rate=0.6, seed=3), repair=repair)
    letter = truth["text"]
    assert res.verified or res.check_yourself
    for p in res.verified:
        assert p["status"] == "verified"
        assert p["evidence"] and p["evidence"] in letter
    if not repair:
        assert res.check_yourself, "with a 60% error rate something must be held back"
    steps = [s["step"] for s in res.trace]
    assert steps[0] == "find_page" and "check" in steps
