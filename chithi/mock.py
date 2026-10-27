"""A stand-in for Meta's models, for the synthetic letters only.

It lets the app, the check and the evaluation run with no API key: the "reader"
returns the letter's true text, and the "explainer" writes one point per fact,
getting a share of them wrong on purpose (`error_rate`) so the check has
something to catch. Its numbers measure the check, not the models.
"""

from __future__ import annotations

import random
import re
from datetime import date

from . import values

LABELS = {
    "total": ("Amount to pay", "देय राशि", "দিতে হবে"),
    "due_date": ("Pay by", "भुगतान की अंतिम तिथि", "শেষ তারিখ"),
    "pay_by": ("Pay by", "भुगतान की अंतिम तिथि", "শেষ তারিখ"),
    "after_due": ("Amount after the due date", "अंतिम तिथि के बाद राशि", "শেষ তারিখের পরে টাকা"),
    "disconnection": ("Electricity may be cut after", "इसके बाद बिजली कट सकती है", "এর পরে বিদ্যুৎ কাটা যেতে পারে"),
    "late_fee": ("Late fee", "विलंब शुल्क", "দেরির জরিমানা"),
    "npa_date": ("Loan marked as bad debt on", "ऋण एनपीए घोषित होगा", "ঋণ অনাদায়ী ঘোষণা হবে"),
    "reply_by": ("Reply if you disagree by", "असहमति हो तो जवाब दें", "আপত্তি থাকলে জবাব দিন"),
    "emi": ("Monthly instalment", "मासिक किस्त", "মাসিক কিস্তি"),
    "overdue": ("Overdue amount", "बकाया राशि", "বকেয়া টাকা"),
    "penal": ("Penalty interest", "दंड ब्याज", "জরিমানা সুদ"),
    "tax": ("Tax", "कर", "কর"),
    "interest": ("Interest", "ब्याज", "সুদ"),
}
LANG_INDEX = {"en": 0, "hi": 1, "bn": 2}


class MockBackend:
    name = "mock"

    def __init__(self, truth: dict, error_rate: float = 0.25, seed: int = 0):
        self.truth = truth
        self.error_rate = error_rate
        self.rng = random.Random(seed)
        self.lang = "en"

    def segment(self, image, concept):
        return []

    def read(self, image):
        return self.truth["text"], {}

    def _line_with(self, shown: str) -> str:
        for line in self.truth["text"].splitlines():
            if shown in line:
                return line.strip()
        return shown

    def _say(self, fact: dict, wrong: bool) -> str:
        label = LABELS[fact["name"]][LANG_INDEX[self.lang]]
        if fact["kind"] == "date":
            d = date.fromisoformat(fact["value"])
            if wrong:
                d = d.replace(day=d.day % 28 + 1)
            return f"{label}: {d:%d/%m/%Y}"
        amount = values.find_numbers(fact["shown"])[0].text.replace("/-", "")
        if wrong:
            digits = [i for i, ch in enumerate(amount) if ch.isdigit()]
            i = self.rng.choice(digits)
            amount = amount[:i] + str((int(amount[i]) + self.rng.randint(1, 8)) % 10) + amount[i + 1:]
        return f"{label}: ₹{amount}"

    def ask(self, instructions: str, letter_text: str, extra: str = ""):
        self.lang = next((k for k, v in {"hi": "Write in Hindi", "bn": "Write in Bengali"}.items() if v in instructions), "en")
        repairing = "FAILED POINTS" in extra
        facts = [f for f in self.truth["facts"] if f["name"] in LABELS][:6]
        if repairing:
            failed_says = re.findall(r'"say": "([^"]*)"', extra)
            facts = [f for f in facts if any(LABELS[f["name"]][LANG_INDEX[self.lang]] in s for s in failed_says)]
        points = []
        for f in facts:
            wrong = (not repairing) and self.rng.random() < self.error_rate
            points.append({"say": self._say(f, wrong), "quote": self._line_with(f["shown"]),
                           "topic": "deadline" if f["kind"] == "date" else "amount"})
        return {"kind": self.truth["kind"].replace("_", " "), "summary": "(mock explainer: no model was called)",
                "points": points}, {}, "mock"
