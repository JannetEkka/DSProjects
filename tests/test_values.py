from datetime import date
from decimal import Decimal

from chithi.values import find_dates, find_numbers, find_values


def dates(text):
    return [f.value for f in find_dates(text)]


def numbers(text):
    return [f.value for f in find_values(text) if f.kind == "number"]


def test_day_first_dates():
    assert dates("Due Date: 05/11/2026") == [date(2026, 11, 5)]
    assert dates("dated 05-11-26 and 5.11.2026") == [date(2026, 11, 5), date(2026, 11, 5)]


def test_month_name_dates():
    assert dates("pay by 5th November, 2026") == [date(2026, 11, 5)]
    assert dates("BILL DATE 21-OCT-2026") == [date(2026, 10, 21)]
    assert dates("on November 5, 2026") == [date(2026, 11, 5)]
    assert dates("2026-11-05") == [date(2026, 11, 5)]


def test_hindi_and_bengali_dates():
    assert dates("अंतिम तिथि ५ नवंबर २०२६ है") == [date(2026, 11, 5)]
    assert dates("শেষ তারিখ ৫ নভেম্বর ২০২৬") == [date(2026, 11, 5)]
    assert dates("तिथि 05/11/2026") == [date(2026, 11, 5)]


def test_impossible_date_is_not_a_date():
    assert dates("31/02/2026") == []


def test_indian_grouping_and_rupee_marks():
    assert numbers("Amount payable Rs. 1,23,456.50") == [Decimal("123456.5")]
    assert numbers("₹2,450/-") == [Decimal("2450")]
    assert numbers("INR 2450.00") == [Decimal("2450")]


def test_lakh_and_crore_words():
    assert numbers("a penalty of 1.5 lakh") == [Decimal("150000")]
    assert numbers("২ লাখ টাকা") == [Decimal("200000")]
    assert numbers("3 करोड़ रुपये") == [Decimal("30000000")]


def test_native_digits():
    assert numbers("₹২,৪৫০") == [Decimal("2450")]
    assert numbers("₹२,४५०") == [Decimal("2450")]


def test_dates_are_not_counted_as_numbers():
    vals = find_values("Pay ₹2,450 by 05/11/2026")
    assert [(v.kind, str(v.value)) for v in vals] == [("number", "2450"), ("date", "2026-11-05")]


def test_numbers_inside_words_are_numbers_too():
    # Consumer numbers and the like are still numbers; they must match the letter too.
    assert numbers("Consumer No. 0123456789") == [Decimal("123456789")]
