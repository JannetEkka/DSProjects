"""The deterministic check every explained point goes through before it is shown.

A point is the model's claim: something said to the reader (in Bengali, Hindi
or English) plus the exact words of the letter it rests on. The check:

1. finds the quoted words in the letter's text (exactly, or nearly, allowing for
   small reading slips), and takes the letter's own words from then on;
2. reads every date and number in what the reader will be told, and requires
   each one to be in those words of the letter;
3. if a second, independent reading of the letter is given (the SAM 3.1 region
   crops, read separately), requires each value to be in that reading too.

A point that passes is "verified". Anything else is "check_yourself" with the
reasons, and is shown apart, never as fact. No model takes part in the check.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from rapidfuzz import fuzz

from . import values

# How close a quote has to be to the letter's text to count as found (0-100).
QUOTE_MATCH = 90


@dataclass
class Point:
    id: str
    say: str  # what the reader is told, in their language
    quote: str  # the letter's words this rests on, as the model copied them


@dataclass
class Check:
    point_id: str
    status: str  # "verified" | "check_yourself"
    reasons: list[str] = field(default_factory=list)
    evidence: str = ""  # the letter's own words the point was checked against
    span: tuple[int, int] | None = None  # position of `evidence` in the letter text
    values: list[dict] = field(default_factory=list)  # each value the reader is told, and whether it held

    def to_dict(self) -> dict:
        return asdict(self)


def _compact(text: str) -> tuple[str, list[int]]:
    """Casefolded text with runs of spaces collapsed, and for each character
    of it the position it came from in `text`."""
    text = values.normalise(text)
    out, where = [], []
    prev_space = True
    for i, ch in enumerate(text):
        if ch.isspace():
            if prev_space:
                continue
            out.append(" ")
            prev_space = True
        else:
            out.append(ch.casefold() if len(ch.casefold()) == 1 else ch)
            prev_space = False
        where.append(i)
    return "".join(out), where


def _widen(text: str, start: int, end: int) -> tuple[int, int]:
    """Grow a span to whole words so it never cuts a number in half."""
    while start > 0 and not text[start - 1].isspace():
        start -= 1
    while end < len(text) and not text[end].isspace():
        end += 1
    return start, end


def locate(quote: str, letter: str) -> tuple[int, int, float] | None:
    """Where `quote` is in `letter`: (start, end, score) in `letter`'s
    positions, or None if it isn't there."""
    q, _ = _compact(quote)
    t, where = _compact(letter)
    q = q.strip()
    if not q or not t:
        return None
    i = t.find(q)
    if i >= 0:
        return where[i], where[i + len(q) - 1] + 1, 100.0
    m = fuzz.partial_ratio_alignment(q, t, score_cutoff=QUOTE_MATCH)
    if m is None or m.dest_end <= m.dest_start:
        return None
    # A near match must cover about as much text as the quote, not a fragment.
    if (m.dest_end - m.dest_start) < 0.8 * len(q):
        return None
    start, end = _widen(values.normalise(letter), where[m.dest_start], where[m.dest_end - 1] + 1)
    return start, end, m.score


def check_point(point: Point, letter: str, second_reading: str | None = None) -> Check:
    check = Check(point.id, "check_yourself")
    told = values.find_values(point.say)

    where = locate(point.quote, letter)
    if where is None:
        check.reasons.append("quote_not_found")
        check.values = [{"kind": f.kind, "text": f.text, "in_letter": False} for f in told]
        return check
    start, end, _ = where
    check.span = (start, end)
    check.evidence = values.normalise(letter)[start:end]

    in_quote = {values.key(f) for f in values.find_values(check.evidence)}
    in_second = None
    if second_reading is not None:
        in_second = {values.key(f) for f in values.find_values(second_reading)}

    for f in told:
        k = values.key(f)
        row = {"kind": f.kind, "text": f.text, "value": k[1], "in_letter": k in in_quote}
        if in_second is not None:
            row["in_second_reading"] = k in in_second
        check.values.append(row)
        if not row["in_letter"]:
            check.reasons.append(f"{f.kind}_not_in_quote:{f.text.strip()}")
        elif in_second is not None and not row["in_second_reading"]:
            check.reasons.append(f"{f.kind}_not_in_second_reading:{f.text.strip()}")

    if not check.reasons:
        check.status = "verified"
    return check


def check_all(points: list[Point], letter: str, second_reading: str | None = None) -> list[Check]:
    return [check_point(p, letter, second_reading) for p in points]


_REASON_TEXT = {
    "quote_not_found": "The words it quotes aren't in the letter.",
    "date_not_in_quote": "The date {x} isn't in the part of the letter it quotes.",
    "number_not_in_quote": "The number {x} isn't in the part of the letter it quotes.",
    "date_not_in_second_reading": "A second reading of the photo didn't find the date {x}.",
    "number_not_in_second_reading": "A second reading of the photo didn't find the number {x}.",
}


def explain_reason(reason: str) -> str:
    code, _, x = reason.partition(":")
    return _REASON_TEXT.get(code, code).format(x=x)

