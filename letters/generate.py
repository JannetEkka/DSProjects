"""Make synthetic Indian official letters, with the truth about each one.

Every letter here is invented: the senders are fictional, the names are made up,
and each page carries "SYNTHETIC SAMPLE". No real person's letter is used.

For each letter this writes, under letters/out/:
  <id>.png        the page, as a clean scan
  <id>.photo.jpg  the same page as a phone photo (tilted, shaded, on a table)
  <id>.json       the truth: the page's full text and every date and amount on it

Run:  python letters/generate.py --n 40
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "out"
FONTS = HERE / "fonts"

FIRST = ["Rina", "Sujata", "Amit", "Prakash", "Moumita", "Rahul", "Sunita", "Dipankar", "Farida", "Joseph", "Anjali", "Biswajit"]
LAST = ["Mondal", "Das", "Sharma", "Kumari", "Hansda", "Ghosh", "Yadav", "Khatun", "Tirkey", "Roy", "Paul", "Singh"]
PLACES = [("Sonarpur", "West Bengal", "700150"), ("Barasat", "West Bengal", "700124"), ("Ranchi", "Jharkhand", "834001"),
          ("Gaya", "Bihar", "823001"), ("Siliguri", "West Bengal", "734001"), ("Dhanbad", "Jharkhand", "826001")]

MONTHS_HI = ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


def fmt_date(d: date, style: str) -> str:
    return {
        "slash": d.strftime("%d/%m/%Y"),
        "dash": d.strftime("%d-%m-%Y"),
        "dot": d.strftime("%d.%m.%Y"),
        "mon": d.strftime("%d-%b-%Y").upper(),
        "long": f"{d.day}{'th' if 11 <= d.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d.day % 10, 'th')} {d.strftime('%B %Y')}",
        "hi": f"{d.day} {MONTHS_HI[d.month - 1]} {d.year}",
    }[style]


def indian(n: float, decimals: int = 2) -> str:
    """1,23,456.00 grouping."""
    whole, frac = f"{n:.{decimals}f}".split(".") if decimals else (str(int(round(n))), "")
    head, tail = whole[:-3], whole[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    out = ",".join(groups + [tail]) if groups else tail
    return out + (f".{frac}" if decimals else "")


def fmt_amount(n: float, style: str) -> str:
    return {
        "rs": f"Rs. {indian(n)}",
        "rupee": f"₹ {indian(n)}",
        "slashdash": f"Rs. {indian(n, 0)}/-",
        "inr": f"INR {indian(n)}",
        "hi": f"₹{indian(n)}",
    }[style]


@dataclass
class Letter:
    id: str
    kind: str
    language: str
    html: str
    facts: list[dict] = field(default_factory=list)


def _fact(facts, name, kind, value, shown):
    facts.append({"name": name, "kind": kind, "value": value.isoformat() if kind == "date" else f"{value:.2f}", "shown": shown})
    return shown


def _person(r):
    city, state, pin = r.choice(PLACES)
    name = f"{r.choice(FIRST)} {r.choice(LAST)}"
    addr = f"{r.randint(1, 240)}, {r.choice(['Station Road', 'Netaji Pally', 'Kali Mandir Lane', 'Main Road', 'Gandhi Colony'])}, {city}, {state} - {pin}"
    return name, addr, city


def electricity_bill(r: random.Random, i: int) -> Letter:
    facts: list[dict] = []
    ds, am = r.choice(["slash", "mon", "dash"]), r.choice(["rs", "rupee", "inr"])
    name, addr, city = _person(r)
    bill = date(2026, r.randint(8, 10), r.randint(1, 28))
    due = bill + timedelta(days=r.choice([14, 15, 21]))
    disc = due + timedelta(days=15)
    units = r.randint(90, 640)
    energy = round(units * r.choice([5.37, 6.12, 7.04]), 2)
    fixed = r.choice([45.0, 60.0, 90.0])
    duty = round(energy * 0.05, 2)
    arrears = r.choice([0.0, 0.0, round(r.uniform(200, 1800), 2)])
    total = round(energy + fixed + duty + arrears, 2)
    late = round(total * 0.02, 2)
    after = round(total + late, 2)
    A = lambda nm, v: _fact(facts, nm, "amount", v, fmt_amount(v, am))
    D = lambda nm, v: _fact(facts, nm, "date", v, fmt_date(v, ds))
    html = f"""
<div class="head"><b>SONARPUR VIDYUT VITARAN LIMITED</b><br>(A fictional distribution company) · Customer care 1800-000-0000</div>
<h2>ELECTRICITY BILL</h2>
<table class="kv">
<tr><td>Consumer Name</td><td>{name}</td><td>Bill Date</td><td>{D('bill_date', bill)}</td></tr>
<tr><td>Address</td><td>{addr}</td><td>Consumer No.</td><td>{r.randint(10**9, 10**10 - 1)}</td></tr>
<tr><td>Category</td><td>Domestic (LT)</td><td>Units Consumed</td><td>{units} kWh</td></tr>
</table>
<table class="grid">
<tr><th>Charge</th><th>Amount</th></tr>
<tr><td>Energy Charges ({units} units)</td><td>{A('energy_charges', energy)}</td></tr>
<tr><td>Fixed Charges</td><td>{A('fixed_charges', fixed)}</td></tr>
<tr><td>Electricity Duty</td><td>{A('duty', duty)}</td></tr>
<tr><td>Arrears</td><td>{A('arrears', arrears)}</td></tr>
<tr class="tot"><td>NET AMOUNT PAYABLE</td><td>{A('total', total)}</td></tr>
</table>
<div class="box">Pay by Due Date: <b>{D('due_date', due)}</b><br>Amount payable after due date: <b>{A('after_due', after)}</b> (includes late payment surcharge of {A('late_fee', late)})</div>
<p>If the bill remains unpaid, supply is liable to be disconnected after {D('disconnection', disc)} under the applicable supply code, without further notice. Reconnection charges will apply.</p>
<p class="small">Pay online, at any cash counter, or through authorised collection centres. Ignore if already paid.</p>
"""
    return Letter(f"elec-{i:03d}", "electricity_bill", "en", html, facts)


def bank_emi_notice(r: random.Random, i: int) -> Letter:
    facts: list[dict] = []
    ds, am = r.choice(["long", "slash", "dot"]), r.choice(["rs", "slashdash", "rupee"])
    name, addr, city = _person(r)
    sent = date(2026, 10, r.randint(1, 26))
    emi = r.choice([3250.0, 4875.0, 6120.0, 8999.0, 12450.0])
    missed = r.randint(1, 2)
    overdue = emi * missed
    penal = round(overdue * 0.02 * missed, 0)
    total = round(overdue + penal, 2)
    since = sent - timedelta(days=30 * missed + r.randint(1, 9))
    by = sent + timedelta(days=r.choice([7, 10, 15]))
    npa = since + timedelta(days=90)
    A = lambda nm, v: _fact(facts, nm, "amount", v, fmt_amount(v, am))
    D = lambda nm, v: _fact(facts, nm, "date", v, fmt_date(v, ds))
    html = f"""
<div class="head"><b>PURBASHA GRAMIN BANK</b><br>(A fictional bank) · {city} Branch</div>
<p class="right">Date: {D('letter_date', sent)}</p>
<p>To,<br>{name}<br>{addr}</p>
<p><b>Sub: Reminder for overdue instalments in Loan Account No. {r.randint(10**11, 10**12 - 1)}</b></p>
<p>Dear Customer,</p>
<p>This is to inform you that {missed} EMI(s) of {A('emi', emi)} each in your above loan account are overdue since {D('overdue_since', since)}.
The total overdue amount is {A('overdue', overdue)}, and penal interest of {A('penal', penal)} has been levied as per the sanction terms.</p>
<p>You are requested to pay {A('total', total)} on or before {D('pay_by', by)} to regularise the account.</p>
<p>Please note that if the dues are not cleared, the account will be classified as a Non-Performing Asset (NPA) on {D('npa_date', npa)}, which will affect your credit score, and the Bank may initiate recovery proceedings as per law.</p>
<p>If you have already paid, please ignore this letter.</p>
<p>Yours faithfully,<br>Branch Manager</p>
"""
    return Letter(f"bank-{i:03d}", "bank_notice", "en", html, facts)


def tax_demand(r: random.Random, i: int) -> Letter:
    facts: list[dict] = []
    ds, am = r.choice(["slash", "mon"]), r.choice(["rs", "inr"])
    name, addr, city = _person(r)
    sent = date(2026, r.randint(8, 10), r.randint(1, 28))
    tax = round(r.uniform(2000, 90000), 0)
    interest = round(tax * r.choice([0.03, 0.06, 0.09]), 0)
    total = tax + interest
    by = sent + timedelta(days=30)
    reply = sent + timedelta(days=15)
    ay = r.choice(["2024-25", "2025-26"])
    A = lambda nm, v: _fact(facts, nm, "amount", v, fmt_amount(v, am))
    D = lambda nm, v: _fact(facts, nm, "date", v, fmt_date(v, ds))
    html = f"""
<div class="head"><b>OFFICE OF THE TAX OFFICER, WARD 7 (FICTIONAL)</b><br>Synthetic sample for testing · not issued by any government</div>
<h2>NOTICE OF DEMAND</h2>
<p class="right">Date: {D('notice_date', sent)}</p>
<p>To,<br>{name}<br>{addr}<br>Taxpayer ID: {''.join(r.choice('ABCDEFGHJKLMNPQRSTUVWXYZ') for _ in range(5))}{r.randint(1000, 9999)}{r.choice('ABCDEFGH')}</p>
<p>Assessment Year: {ay}</p>
<p>On processing your return of income for the above assessment year, the following sum has been determined as payable by you:</p>
<table class="grid">
<tr><td>Tax payable</td><td>{A('tax', tax)}</td></tr>
<tr><td>Interest</td><td>{A('interest', interest)}</td></tr>
<tr class="tot"><td>Total sum payable</td><td>{A('total', total)}</td></tr>
</table>
<p>You are required to pay the above sum within 30 days of service of this notice, that is on or before {D('pay_by', by)}. If you disagree with this demand, you may submit your response with documents by {D('reply_by', reply)}.</p>
<p>If the amount is not paid within the period specified, further interest will be charged and steps may be taken to recover it.</p>
<p>Tax Officer, Ward 7</p>
"""
    return Letter(f"tax-{i:03d}", "tax_notice", "en", html, facts)


def property_tax_hi(r: random.Random, i: int) -> Letter:
    facts: list[dict] = []
    ds, am = r.choice(["hi", "slash"]), "hi"
    name, addr, city = _person(r)
    sent = date(2026, r.randint(8, 10), r.randint(1, 28))
    tax = round(r.uniform(800, 14000), 0)
    late = round(tax * 0.1, 0)
    total = tax + late
    by = sent + timedelta(days=r.choice([15, 21, 30]))
    A = lambda nm, v: _fact(facts, nm, "amount", v, fmt_amount(v, am))
    D = lambda nm, v: _fact(facts, nm, "date", v, fmt_date(v, ds))
    html = f"""
<div class="head"><b>नगर परिषद, शांतिपुर (काल्पनिक)</b><br>संपत्ति कर विभाग</div>
<h2>संपत्ति कर बकाया सूचना</h2>
<p class="right">दिनांक: {D('notice_date', sent)}</p>
<p>सेवा में,<br>{name}<br>{addr}<br>संपत्ति संख्या: {r.randint(100, 999)}/{r.randint(10, 99)}</p>
<p>आपको सूचित किया जाता है कि वित्तीय वर्ष 2026-27 के लिए आपकी संपत्ति पर {A('tax', tax)} का संपत्ति कर बकाया है।
देर से भुगतान के कारण {A('late_fee', late)} विलंब शुल्क जोड़ा गया है। कुल देय राशि {A('total', total)} है।</p>
<p>कृपया कुल राशि का भुगतान {D('pay_by', by)} तक नगर परिषद कार्यालय में या ऑनलाइन करें। निर्धारित तिथि तक भुगतान न करने पर नियमानुसार कुर्की की कार्यवाही की जा सकती है।</p>
<p>यदि आपने भुगतान कर दिया है, तो इस सूचना को अनदेखा करें।</p>
<p>कर अधीक्षक</p>
"""
    return Letter(f"ptax-{i:03d}", "property_tax_notice", "hi", html, facts)


KINDS = [electricity_bill, bank_emi_notice, tax_demand, property_tax_hi]

CSS = """
@font-face { font-family: Noto; src: url('{fonts}/NotoSans-400.ttf'); }
@font-face { font-family: Noto; src: url('{fonts}/NotoSans-700.ttf'); font-weight: bold; }
@font-face { font-family: NotoDeva; src: url('{fonts}/NotoSansDevanagari-400.ttf'); }
@font-face { font-family: NotoDeva; src: url('{fonts}/NotoSansDevanagari-700.ttf'); font-weight: bold; }
body { margin: 0; background: white; }
.page { width: 760px; padding: 40px 48px; font: 15px/1.5 Noto, NotoDeva, sans-serif; color: #111; position: relative; }
.head { text-align: center; border-bottom: 2px solid #222; padding-bottom: 8px; font-size: 14px; }
.head b { font-size: 20px; letter-spacing: .5px; }
h2 { text-align: center; font-size: 17px; margin: 14px 0; text-decoration: underline; }
.right { text-align: right; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
.kv td { padding: 3px 6px; vertical-align: top; }
.kv td:nth-child(odd) { color: #444; white-space: nowrap; }
.grid td, .grid th { border: 1px solid #333; padding: 5px 8px; }
.grid td:last-child { text-align: right; white-space: nowrap; }
.tot td { font-weight: bold; background: #eee; }
.box { border: 2px solid #111; padding: 8px 12px; margin: 12px 0; }
.small { font-size: 12px; color: #444; }
.synthetic { margin-top: 18px; border-top: 1px dashed #999; font-size: 11px; color: #777; text-align: center; padding-top: 6px; }
"""


def render(letters: list[Letter]) -> None:
    from playwright.sync_api import sync_playwright

    css = CSS.replace("{fonts}", FONTS.resolve().as_uri())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=1.6, viewport={"width": 856, "height": 600})
        for L in letters:
            page.set_content(f"<html><head><meta charset='utf-8'><style>{css}</style></head><body><div class='page'>{L.html}"
                             f"<div class='synthetic'>SYNTHETIC SAMPLE · made up for testing Chithi · not a real letter</div></div></body></html>")
            page.wait_for_timeout(50)
            el = page.query_selector(".page")
            el.screenshot(path=str(OUT / f"{L.id}.png"))
            text = el.inner_text()
            (OUT / f"{L.id}.json").write_text(json.dumps(
                {"id": L.id, "kind": L.kind, "language": L.language, "text": text, "facts": L.facts},
                ensure_ascii=False, indent=1))
        browser.close()


def photograph(src: Path, dst: Path, r: random.Random) -> None:
    """Make a clean page look like a phone photo of paper on a table."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    page = Image.open(src).convert("RGB")
    w, h = page.size
    # Paper tint and a soft shadow from the phone.
    tint = Image.new("RGB", page.size, r.choice([(250, 246, 235), (245, 245, 240), (252, 249, 240)]))
    page = Image.blend(page, tint, 0.12)
    shade = Image.new("L", page.size, 0)
    d = ImageDraw.Draw(shade)
    d.ellipse([r.randint(-w, 0), r.randint(-h // 2, h // 2), r.randint(w // 2, w), r.randint(h, 2 * h)], fill=r.randint(25, 60))
    shade = shade.filter(ImageFilter.GaussianBlur(120))
    page = Image.composite(Image.new("RGB", page.size, (60, 55, 50)), page, shade)
    # Onto a table, tilted.
    pad = int(0.08 * max(w, h))
    table = Image.new("RGB", (w + 2 * pad, h + 2 * pad), r.choice([(120, 84, 52), (90, 90, 95), (160, 130, 95)]))
    table.paste(page, (pad, pad))
    table = table.rotate(r.uniform(-4, 4), resample=Image.BICUBIC, fillcolor=table.getpixel((5, 5)))
    table = ImageEnhance.Brightness(table).enhance(r.uniform(0.85, 1.05))
    table = table.filter(ImageFilter.GaussianBlur(r.uniform(0.3, 0.9)))
    table.thumbnail((1600, 1600))
    table.save(dst, quality=r.randint(70, 88))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40, help="how many letters")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    r = random.Random(args.seed)
    OUT.mkdir(exist_ok=True)
    letters = [KINDS[i % len(KINDS)](r, i) for i in range(args.n)]
    render(letters)
    for L in letters:
        photograph(OUT / f"{L.id}.png", OUT / f"{L.id}.photo.jpg", r)
    print(f"wrote {len(letters)} letters to {OUT}")


if __name__ == "__main__":
    main()
