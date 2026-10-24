"""Convert a Claude Code session JSONL into a readable Markdown transcript.

    python3 build_transcript.py <session.jsonl> <out.md> [--title "..."]

Keeps: the user's own messages, the assistant's visible replies, and a one-line summary of each
tool call. Drops: internal reasoning, system reminders/notifications, tool outputs, images.
Redacts: API-key-like strings and email addresses that are not part of the dataset discussion.
Skips the mock-interview rehearsal exchange (the participant asked for it to be left out).

Curation (--curation file.json, optional): the participant asked for the transcript to keep only what
built the project. {"drop_user": [timestamps], "user_override": {timestamp: text}} drops a user turn
and the assistant's direct reply to it (up to its next tool call), or replaces a turn with its
project-relevant part. Paragraphs and list lines about interview preparation, rehearsal or personal
logistics are removed from assistant replies.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

KEY_RE = re.compile(r"(AIza[0-9A-Za-z_-]{20,}|gsk_[0-9A-Za-z]{20,}|nvapi-[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z]{20,})")
TAG_BLOCK_RE = re.compile(r"<(system-reminder|task-notification|local-command-stdout|command-name|command-message|"
                          r"command-args|other-session|cross-session-message)[^>]*>.*?</\1>", re.S)
PRIVATE_EMAILS = [r"dharshreya03@gmail\.com"]
MOCK_START = "start the mock interview"
OFF_TOPIC = re.compile(r"(?i)interview|rehears|\bmock\b|camera|screen.?share|\bsleep\b|leaderboard|top.?5|"
                       r"hidden tests? I'd|you've hit your session limit")
LIST_LINE = re.compile(r"^\s*([-*]|\d+\.|\|)\s")
MOCK_LINE = re.compile(r"(?i)mock interview question|^#+\s*mock interview|^>\s*\*\*\"give me a quick overview")


def clean(text: str) -> str:
    text = TAG_BLOCK_RE.sub("", text)
    text = KEY_RE.sub("[REDACTED-KEY]", text)
    for e in PRIVATE_EMAILS:
        text = re.sub(e, "[REDACTED-EMAIL]", text)
    return text.strip()


def strip_mock(text: str) -> str:
    """Remove trailing rehearsal prompts that were appended to status replies."""
    out = []
    for line in text.splitlines():
        if MOCK_LINE.search(line.strip()):
            break
        out.append(line)
    return "\n".join(out).rstrip()


def drop_off_topic(text: str) -> str:
    """Remove off-topic paragraphs; inside lists and tables remove only the matching lines.
    A matching bold-headed paragraph also removes the paragraphs under it, up to the next bold heading."""
    out, skipping_section = [], False
    for para in re.split(r"\n\s*\n", text):
        lines = para.splitlines()
        bold = para.lstrip().startswith("**")
        if bold:
            skipping_section = False
        if skipping_section:
            continue
        if not OFF_TOPIC.search(para):
            out.append(para)
            continue
        if all(LIST_LINE.match(l) or not l.strip() for l in lines[1:]) and len(lines) > 1:
            kept = [l for l in lines if not OFF_TOPIC.search(l)]
            if kept and any(LIST_LINE.match(l) for l in kept):
                out.append("\n".join(kept))
                continue
        if bold:
            skipping_section = True
    return "\n\n".join(out).strip()


def tool_line(block: dict) -> str:
    name = block.get("name", "tool")
    inp = block.get("input") or {}
    desc = inp.get("description") or inp.get("title") or inp.get("subject") or inp.get("name") or ""
    if not desc and "file_path" in inp:
        desc = inp["file_path"]
    if not desc and "session_id" in inp:
        desc = f"session {inp['session_id']}"
    desc = clean(str(desc))[:160]
    return f"- `{name}`{': ' + desc if desc else ''}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("out")
    ap.add_argument("--title", default="Session transcript")
    ap.add_argument("--curation", default=None)
    a = ap.parse_args()
    cur = json.loads(Path(a.curation).read_text(encoding="utf-8")) if a.curation else {}
    drop_user, override = set(cur.get("drop_user", [])), cur.get("user_override", {})
    curated = bool(cur)
    lines = Path(a.jsonl).read_text(encoding="utf-8", errors="replace").splitlines()
    md = [f"# {a.title}\n", "_Readable export: user messages, assistant replies and one-line tool summaries. "
          "Internal reasoning, system notices and tool outputs are omitted; keys and private emails redacted._\n"]
    skipping_reply = False
    pending_tools: list[str] = []

    def flush_tools():
        if pending_tools:
            md.append("<details><summary>Tool calls (" + str(len(pending_tools)) + ")</summary>\n\n"
                      + "\n".join(pending_tools) + "\n\n</details>\n")
            pending_tools.clear()

    for raw in lines:
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message") or {}
        role = msg.get("role") or ev.get("type")
        content = msg.get("content")
        ts = (ev.get("timestamp") or "")[:19].replace("T", " ")
        if role == "user":
            texts = []
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "text":
                        texts.append(b.get("text", ""))
            text = clean("\n".join(texts))
            if not text or ev.get("isMeta") or ev.get("isSynthetic"):
                continue
            if text.startswith("[Request interrupted") or text.startswith("Caveat:"):
                continue
            if MOCK_START in text.lower() or ts in drop_user:
                skipping_reply = True
                continue
            skipping_reply = False
            text = override.get(ts, text)
            flush_tools()
            md.append(f"\n---\n\n### User ({ts} UTC)\n\n{text}\n")
        elif role == "assistant" and isinstance(content, list):
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    skipping_reply = False
                if skipping_reply:
                    continue
                if b.get("type") == "text":
                    t = strip_mock(clean(b.get("text", "")))
                    if curated:
                        t = drop_off_topic(t)
                    if t:
                        flush_tools()
                        md.append(f"\n**Assistant:**\n\n{t}\n")
                elif b.get("type") == "tool_use":
                    line = tool_line(b)
                    if not (curated and OFF_TOPIC.search(line)):
                        pending_tools.append(line)
    flush_tools()
    out = "\n".join(md)
    assert not KEY_RE.search(out), "key-like string survived redaction"
    Path(a.out).write_text(out, encoding="utf-8")
    print(f"{a.out}: {len(out) / 1e6:.2f} MB, {out.count('### User')} user turns")


if __name__ == "__main__":
    main()
