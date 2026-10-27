"""Find dates and rupee amounts in text, in English, Hindi and Bengali.

Everything here is deterministic: no model is involved. The checker uses it to
compare what an explanation says against what the letter says.

Indian letters write dates day-first (05/11/2026 is 5 November), and amounts
with lakh grouping (1,23,456.00), so both are read that way.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

# Devanagari and Bengali digits become ASCII digits.
_DIGITS = {ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")}
_DIGITS.update({ord(c): str(i) for i, c in enumerate("০১২৩৪৫৬৭৮৯")})

MONTHS = {
    # English, full and short
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
    # Hindi
    "जनवरी": 1, "फरवरी": 2, "फ़रवरी": 2, "मार्च": 3, "अप्रैल": 4, "मई": 5,
    "जून": 6, "जुलाई": 7, "अगस्त": 8, "सितंबर": 9, "सितम्बर": 9,
    "अक्टूबर": 10, "अक्तूबर": 10, "नवंबर": 11, "नवम्बर": 11,
    "दिसंबर": 12, "दिसम्बर": 12,
    # Bengali
    "জানুয়ারি": 1, "জানুয়ারী": 1, "ফেব্রুয়ারি": 2, "ফেব্রুয়ারী": 2,
    "মার্চ": 3, "এপ্রিল": 4, "মে": 5, "জুন": 6, "জুলাই": 7, "আগস্ট": 8,
    "সেপ্টেম্বর": 9, "অক্টোবর": 10, "নভেম্বর": 11, "ডিসেম্বর": 12,
}

# Words that multiply the number before them: "1.5 lakh" is 150000.
MULTIPLIERS = {
    "thousand": 1_000, "हज़ार": 1_000, "हजार": 1_000, "হাজার": 1_000,
    "lakh": 100_000, "lakhs": 100_000, "lac": 100_000, "लाख": 100_000, "লাখ": 100_000, "লক্ষ": 100_000,
    "crore": 10_000_000, "crores": 10_000_000, "करोड़": 10_000_000, "करोड": 10_000_000, "কোটি": 10_000_000,
}

# Nukta letters (ड़, ज़) have two Unicode spellings; keep the NFC one.
MONTHS = {unicodedata.normalize("NFC", k): v for k, v in MONTHS.items()}
MULTIPLIERS = {unicodedata.normalize("NFC", k): v for k, v in MULTIPLIERS.items()}

_MONTH_ALT = "|".join(sorted((re.escape(m) for m in MONTHS), key=len, reverse=True))
_MULT_ALT = "|".join(sorted((re.escape(m) for m in MULTIPLIERS), key=len, reverse=True))

# Not \b: Python's \b treats Indic combining marks as non-word characters.
_L = r"(?<![\wऀ-ॿঀ-৿])"
_R = r"(?![\wऀ-ॿঀ-৿])"

_DATE_PATTERNS = [
    # 2026-11-05
    (re.compile(_L + r"(\d{4})-(\d{1,2})-(\d{1,2})" + _R), ("y", "m", "d")),
    # 05/11/2026, 05-11-2026, 05.11.2026, 05/11/26
    (re.compile(_L + r"(\d{1,2})\s?[/.\-]\s?(\d{1,2})\s?[/.\-]\s?(\d{4}|\d{2})" + _R), ("d", "m", "y")),
    # 5 November 2026, 05-Nov-2026, 5th Nov, 2026, ৫ নভেম্বর ২০২৬
    (re.compile(_L + r"(\d{1,2})(?:st|nd|rd|th)?[\s\-.]*(" + _MONTH_ALT + r")\.?[\s\-.,]*(\d{4})" + _R, re.I), ("d", "M", "y")),
    # November 5, 2026
    (re.compile(_L + r"(" + _MONTH_ALT + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})" + _R, re.I), ("M", "d", "y")),
]

# A number with optional grouping and decimals, and an optional multiplier word.
_NUMBER = re.compile(
    r"(?<![\d.,])(\d{1,3}(?:,\d{2,3})+|\d+)(\.\d+)?(?:\s*/-)?(?:\s*(" + _MULT_ALT + r")" + _R + r")?",
    re.I,
)


@dataclass(frozen=True)
class Found:
    kind: str  # "date" or "number"
    value: object  # datetime.date or Decimal
    text: str  # the text it was read from
    start: int
    end: int


def normalise(text: str) -> str:
    """NFC, ASCII digits, one kind of space and dash. Keeps length per character
    as far as possible so positions stay meaningful."""
    text = unicodedata.normalize("NFC", text).translate(_DIGITS)
    text = text.replace(" ", " ").replace(" ", " ").replace(" ", " ")
    text = re.sub("[‐-―−]", "-", text)
    return text


def _year(y: str) -> int:
    n = int(y)
    return n + 2000 if len(y) == 2 else n


def find_dates(text: str) -> list[Found]:
    text = normalise(text)
    found: list[Found] = []
    taken: list[tuple[int, int]] = []
    for pattern, order in _DATE_PATTERNS:
        for m in pattern.finditer(text):
            if any(s < m.end() and m.start() < e for s, e in taken):
                continue
            parts = dict(zip(order, m.groups()))
            try:
                month = MONTHS[parts["M"].lower()] if "M" in parts else int(parts["m"])
                value = date(_year(parts["y"]), month, int(parts["d"]))
            except (ValueError, KeyError):
                continue
            found.append(Found("date", value, m.group(0), m.start(), m.end()))
            taken.append((m.start(), m.end()))
    return sorted(found, key=lambda f: f.start)


def find_numbers(text: str, skip: list[tuple[int, int]] | None = None) -> list[Found]:
    """Every number in the text, with lakh/crore words applied. Spans in `skip`
    (usually the dates) are left out."""
    text = normalise(text)
    skip = skip or []
    found = []
    for m in _NUMBER.finditer(text):
        if any(s < m.end() and m.start() < e for s, e in skip):
            continue
        whole, frac, mult = m.group(1), m.group(2) or "", m.group(3)
        try:
            value = Decimal(whole.replace(",", "") + frac)
        except InvalidOperation:
            continue
        if mult:
            value *= MULTIPLIERS[mult.lower()]
        value = value.quantize(Decimal(1)) if value == value.to_integral() else value.normalize()
        found.append(Found("number", value, m.group(0), m.start(), m.end()))
    return found


def find_values(text: str) -> list[Found]:
    """Dates first, then the numbers that aren't part of a date."""
    dates = find_dates(text)
    numbers = find_numbers(text, skip=[(d.start, d.end) for d in dates])
    return sorted(dates + numbers, key=lambda f: f.start)


def key(f: Found) -> tuple[str, str]:
    """A comparable key: dates by ISO day, numbers by exact value."""
    if f.kind == "date":
        return ("date", f.value.isoformat())
    return ("number", format(f.value, "f"))
