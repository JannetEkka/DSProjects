"""Chithi's agent: from a photo of a letter to checked points.

    find the page (SAM 3.1)  ->  find the regions that matter (SAM 3.1)
    -> read the page (Muse Spark)  ->  read each region and band again, zoomed in (Muse Spark)
    -> explain in the reader's language, quoting the letter (Muse Spark or Muse Spark Open)
    -> check every point (deterministic, verify.py)
    -> send failed points back once with the reasons, check again
    -> show verified points as fact, and the rest apart as "check this yourself"

Every step is recorded in a trace that the page shows, so a judge (or the
reader's grandson) can see what each model did and why a point was held back.
"""

from __future__ import annotations

import io
import json
import os
import time
from dataclasses import dataclass, field

from PIL import Image, ImageOps

from . import meta, prompts, verify

# Short noun phrases for SAM 3.1: one concept per request.
PAGE_CONCEPT = os.environ.get("CHITHI_PAGE_CONCEPT", "sheet of paper")
REGION_CONCEPTS = [c.strip() for c in os.environ.get("CHITHI_REGION_CONCEPTS", "table,stamp,boxed text").split(",") if c.strip()]
BANDS = 3  # the page is also read again in this many overlapping strips

# USD, from dev.meta.ai/docs/pricing-rate-limits (10-27).
PRICE = {"spark_in": 1.25 / 1e6, "spark_out": 4.25 / 1e6, "sam_image": 2.50 / 1000}


@dataclass
class Region:
    concept: str
    box: tuple[int, int, int, int]  # x1, y1, x2, y2 in the page image
    text: str = ""
    score: float | None = None


@dataclass
class Result:
    language: str
    kind: str = ""
    summary: str = ""
    verified: list[dict] = field(default_factory=list)
    check_yourself: list[dict] = field(default_factory=list)
    letter_text: str = ""
    second_reading: str = ""
    regions: list[dict] = field(default_factory=list)
    page_box: tuple[int, int, int, int] | None = None
    image_size: tuple[int, int] = (0, 0)
    trace: list[dict] = field(default_factory=list)
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return self.__dict__.copy()


class Trace:
    def __init__(self, result: Result, billable: bool = True):
        self.result = result
        self.billable = billable

    def step(self, name: str, model: str, detail: str, started: float, usage: dict | None = None, **extra):
        u = usage or {}
        cost = u.get("input_tokens", 0) * PRICE["spark_in"] + u.get("output_tokens", 0) * PRICE["spark_out"]
        if model.startswith("sam"):
            cost = PRICE["sam_image"]
        if self.billable:
            self.result.cost_usd += cost
        self.result.trace.append({"step": name, "model": model, "detail": detail,
                                  "ms": int((time.time() - started) * 1000), **extra})


# --- backends ----------------------------------------------------------------

class LiveBackend:
    """Meta's models through the Model API (and Muse Spark Open on Baseten)."""
    name = "live"

    def __init__(self, explainer: str = "spark"):
        self.explainer = explainer

    def segment(self, image: bytes, concept: str) -> list[meta.Box]:
        return meta.segment(image, concept)

    def read(self, image: bytes) -> tuple[str, dict]:
        return meta.spark([{"type": "input_text", "text": prompts.READ},
                           {"type": "input_image", "image_url": meta.data_url(image)}])

    def ask(self, instructions: str, letter_text: str, extra: str = "") -> tuple[dict, dict, str]:
        user = f"LETTER TEXT:\n<<<\n{letter_text}\n>>>\n{extra}"
        if self.explainer == "spark-open":
            text, u = meta.spark_open([{"role": "system", "content": instructions}, {"role": "user", "content": user}],
                                      schema=prompts.POINTS_SCHEMA)
            model = meta.SPARK_OPEN
        else:
            text, u = meta.spark([{"type": "input_text", "text": user}], instructions=instructions, schema=prompts.POINTS_SCHEMA)
            model = meta.SPARK
        return json.loads(_strip_fences(text)), u, model


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return text


def jpeg(img: Image.Image, quality: int = 90) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality)
    return buf.getvalue()


def _crop(img: Image.Image, box, pad: float = 0.02) -> Image.Image:
    x1, y1, x2, y2 = box
    px, py = int((x2 - x1) * pad) + 4, int((y2 - y1) * pad) + 4
    return img.crop((max(0, x1 - px), max(0, y1 - py), min(img.width, x2 + px + 1), min(img.height, y2 + py + 1)))


def _zoom(img: Image.Image, min_width: int = 1400) -> Image.Image:
    if img.width >= min_width:
        return img
    s = min_width / img.width
    return img.resize((min_width, int(img.height * s)), Image.LANCZOS)


def run(photo: bytes, language: str, backend, *, repair: bool = True) -> Result:
    res = Result(language=language)
    tr = Trace(res, billable=backend.name != "mock")
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(photo))).convert("RGB")
    img.thumbnail((2000, 2000))
    res.image_size = img.size
    photo = jpeg(img)

    # 1. Find the page in the photo, so the reader sees only the letter.
    t = time.time()
    pages = backend.segment(photo, PAGE_CONCEPT)
    page_img, offset = img, (0, 0)
    if pages:
        best = max(pages, key=lambda b: (b.x2 - b.x1) * (b.y2 - b.y1))
        sx, sy = img.width / best.w, img.height / best.h
        box = (int(best.x1 * sx), int(best.y1 * sy), int(best.x2 * sx), int(best.y2 * sy))
        if (box[2] - box[0]) * (box[3] - box[1]) > 0.25 * img.width * img.height:
            page_img, offset, res.page_box = _crop(img, box, 0.01), box[:2], box
    tr.step("find_page", meta.SAM, f"'{PAGE_CONCEPT}': {len(pages)} found" + (", cropped to it" if res.page_box else ", using the whole photo"), t)
    page_bytes = jpeg(page_img)

    # 2. Find the regions that matter: tables, stamps, boxed amounts.
    regions: list[Region] = []
    for concept in REGION_CONCEPTS:
        t = time.time()
        found = backend.segment(page_bytes, concept)
        for b in found:
            sx, sy = page_img.width / b.w, page_img.height / b.h
            regions.append(Region(concept, (int(b.x1 * sx), int(b.y1 * sy), int(b.x2 * sx), int(b.y2 * sy)), score=b.score))
        tr.step("find_regions", meta.SAM, f"'{concept}': {len(found)} found", t)

    # 3. Read the whole page.
    t = time.time()
    letter_text, u = backend.read(page_bytes)
    res.letter_text = letter_text
    tr.step("read_page", meta.SPARK, f"{len(letter_text)} characters read", t, u)

    # 4. Read it again, independently: each region, and the page in strips, zoomed in.
    h = page_img.height
    strips = [Region("strip", (0, max(0, int(i * h / BANDS - 0.06 * h)), page_img.width - 1, min(h - 1, int((i + 1) * h / BANDS + 0.06 * h))))
              for i in range(BANDS)]
    for reg in regions + strips:
        t = time.time()
        reg.text, u = backend.read(jpeg(_zoom(_crop(page_img, reg.box))))
        tr.step("read_again", meta.SPARK, f"{reg.concept} at {reg.box}: {len(reg.text)} characters", t, u)
    second = "\n".join(r.text for r in regions + strips)
    res.second_reading = second
    res.regions = [{"concept": r.concept, "box": _shift(r.box, offset), "text": r.text, "score": r.score} for r in regions]

    # 5. Explain, quoting the letter.
    language_name = prompts.LANGUAGES[language]
    t = time.time()
    out, u, model = backend.ask(prompts.EXPLAIN.format(language=language_name), letter_text)
    res.kind, res.summary = out.get("kind", ""), out.get("summary", "")
    points = [verify.Point(f"p{i + 1}", p["say"], p["quote"]) for i, p in enumerate(out.get("points", []))]
    topics = {f"p{i + 1}": p.get("topic", "other") for i, p in enumerate(out.get("points", []))}
    tr.step("explain", model, f"{len(points)} points in {language_name}", t, u)

    # 6. Check every point.
    t = time.time()
    checks = verify.check_all(points, letter_text, second)
    failed = [c for c in checks if c.status != "verified"]
    tr.step("check", "deterministic", f"{len(checks) - len(failed)} verified, {len(failed)} failed", t,
            failures=[{"point": c.point_id, "reasons": c.reasons} for c in failed])

    # 7. One repair round: send the failures back with the reasons, check again.
    if repair and failed:
        t = time.time()
        bad = [{"id": c.point_id, "say": p.say, "quote": p.quote, "reasons": [verify.explain_reason(r) for r in c.reasons]}
               for c, p in zip(checks, points) if c.status != "verified"]
        fixed, u, model = backend.ask(prompts.EXPLAIN.format(language=language_name) + "\n\n" + prompts.REPAIR, letter_text,
                                      "FAILED POINTS:\n" + json.dumps(bad, ensure_ascii=False))
        tr.step("repair", model, f"{len(bad)} points sent back, {len(fixed.get('points', []))} returned", t, u)
        t = time.time()
        new_points = [verify.Point(f"r{i + 1}", p["say"], p["quote"]) for i, p in enumerate(fixed.get("points", []))]
        topics.update({f"r{i + 1}": p.get("topic", "other") for i, p in enumerate(fixed.get("points", []))})
        new_checks = verify.check_all(new_points, letter_text, second)
        recovered = [c for c in new_checks if c.status == "verified"]
        tr.step("check", "deterministic", f"after repair: {len(recovered)} of {len(new_checks)} verified", t)
        if recovered:
            # The repaired points replace the ones that failed.
            keep = [(p, c) for p, c in zip(points, checks) if c.status == "verified"]
            points = [p for p, _ in keep] + new_points
            checks = [c for _, c in keep] + new_checks

    for p, c in zip(points, checks):
        row = {"id": p.id, "say": p.say, "quote": p.quote, "topic": topics.get(p.id, "other"), **c.to_dict(),
               "reasons_text": [verify.explain_reason(r) for r in c.reasons]}
        (res.verified if c.status == "verified" else res.check_yourself).append(row)
    res.cost_usd = round(res.cost_usd, 4)
    return res


def _shift(box, offset):
    return (box[0] + offset[0], box[1] + offset[1], box[2] + offset[0], box[3] + offset[1])


def answer(question: str, letter_text: str, second_reading: str | None, language: str, backend) -> dict:
    """A follow-up question about the same letter, answered under the same check."""
    t = time.time()
    out, u, model = backend.ask(prompts.ANSWER.format(language=prompts.LANGUAGES[language], question=question)
                                + "\n\nReturn JSON with \"kind\" and \"summary\" as empty strings and the answer in \"points\".",
                                letter_text)
    points = [verify.Point(f"a{i + 1}", p["say"], p["quote"]) for i, p in enumerate(out.get("points", []))]
    checks = verify.check_all(points, letter_text, second_reading)
    rows = [{"id": p.id, "say": p.say, "quote": p.quote, **c.to_dict(),
             "reasons_text": [verify.explain_reason(r) for r in c.reasons]} for p, c in zip(points, checks)]
    return {"question": question, "verified": [r for r in rows if r["status"] == "verified"],
            "check_yourself": [r for r in rows if r["status"] != "verified"],
            "trace": [{"step": "answer", "model": model, "ms": int((time.time() - t) * 1000),
                       "detail": f"{len(points)} points, {sum(r['status'] == 'verified' for r in rows)} verified"}]}
