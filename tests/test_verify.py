from chithi.verify import Point, check_point, locate

LETTER = """GANGAPUR POWER DISTRIBUTION LTD
Electricity Bill  Bill Date: 21/10/2026
Consumer No: 4471 2290
Amount Payable: Rs. 2,450.00
Due Date: 05/11/2026
After the due date a late payment surcharge of Rs. 37.00 is payable.
Disconnection notice: supply may be disconnected after 20/11/2026."""


def test_locate_exact_ignores_case_and_spacing():
    start, end, score = locate("amount   payable: rs. 2,450.00", LETTER)
    assert score == 100
    assert LETTER[start:end] == "Amount Payable: Rs. 2,450.00"


def test_locate_tolerates_a_small_reading_slip():
    assert locate("Amount Payab1e: Rs. 2,450.00", LETTER) is not None


def test_locate_rejects_words_not_in_the_letter():
    assert locate("Your account has been frozen", LETTER) is None


def test_verified_when_values_match():
    p = Point("p1", "আপনাকে ₹২,৪৫০ দিতে হবে ০৫/১১/২০২৬ এর মধ্যে।", "Amount Payable: Rs. 2,450.00\nDue Date: 05/11/2026")
    c = check_point(p, LETTER)
    assert c.status == "verified", c.reasons


def test_wrong_amount_is_caught():
    p = Point("p1", "आपको ₹2,540 देने हैं।", "Amount Payable: Rs. 2,450.00")
    c = check_point(p, LETTER)
    assert c.status == "check_yourself"
    assert c.reasons == ["number_not_in_quote:2,540"]


def test_wrong_date_is_caught_even_if_elsewhere_in_letter():
    # 20/11/2026 is in the letter, but not in the words this point quotes.
    p = Point("p1", "Pay by 20/11/2026.", "Due Date: 05/11/2026")
    c = check_point(p, LETTER)
    assert c.status == "check_yourself"
    assert c.reasons == ["date_not_in_quote:20/11/2026"]


def test_misquote_does_not_launder_a_wrong_value():
    # The model "quotes" a slightly wrong amount; the near match finds the real
    # line, and the value is checked against the letter's words, not the quote.
    p = Point("p1", "You must pay Rs 2,540.", "Amount Payable: Rs. 2,540.00")
    c = check_point(p, LETTER)
    assert c.status == "check_yourself"
    assert "2,450.00" in c.evidence


def test_invented_quote_fails():
    p = Point("p1", "Your account is frozen.", "Your account has been frozen")
    assert check_point(p, LETTER).reasons == ["quote_not_found"]


def test_second_reading_must_agree():
    p = Point("p1", "Pay ₹2,450.", "Amount Payable: Rs. 2,450.00")
    assert check_point(p, LETTER, second_reading="Amount Payable Rs 2,450.00").status == "verified"
    c = check_point(p, LETTER, second_reading="Amount Payable Rs 2,456.00")
    assert c.reasons == ["number_not_in_second_reading:2,450"]


def test_point_without_values_needs_only_the_quote():
    p = Point("p1", "Your electricity may be cut off if you don't pay.", "supply may be disconnected")
    assert check_point(p, LETTER).status == "verified"
