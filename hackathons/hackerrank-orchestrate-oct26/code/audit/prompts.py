"""Versioned LLM prompts live in code/prompts/*.md; the leading <!-- --> header documents the design
choices and is stripped before the prompt is sent."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    text = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
    return re.sub(r"\A\s*<!--.*?-->\s*", "", text, flags=re.S).rstrip("\n")


def as_untrusted(value) -> str:
    """JSON-encode untrusted text for a prompt; '<' and '>' are escaped so the value can never close
    the delimiter tag around it."""
    return json.dumps(value, ensure_ascii=False, indent=1).replace("<", "\\u003c").replace(">", "\\u003e")
