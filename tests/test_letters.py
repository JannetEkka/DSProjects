"""The synthetic letters and the value parser agree: every date and amount the
generator put on a page is read back from that page's text."""

import json
from pathlib import Path

import pytest

from chithi import values

LETTERS = sorted((Path(__file__).parent.parent / "letters" / "out").glob("*.json"))


@pytest.mark.skipif(not LETTERS, reason="run letters/generate.py first")
@pytest.mark.parametrize("path", LETTERS, ids=lambda p: p.stem)
def test_every_fact_is_read_back(path):
    truth = json.loads(path.read_text())
    found = {values.key(f) for f in values.find_values(truth["text"])}
    for fact in truth["facts"]:
        if fact["kind"] == "date":
            assert ("date", fact["value"]) in found, fact
        else:
            v = values.find_numbers(fact["value"])[0]
            assert values.key(v) in found, fact
