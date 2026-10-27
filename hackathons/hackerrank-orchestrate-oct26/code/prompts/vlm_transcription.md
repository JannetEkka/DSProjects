<!--
prompt: vlm_transcription  version: 1
Used by audit/media.py to transcribe admin-console screenshots (Gemini vision, OCR fallback).
Design choices:
* Transcription only: the model returns plain text, never a judgement. Its output is used solely as
  text in which identifiers are matched exactly - it cannot set a record's state by itself beyond what
  the transcribed screen shows, and it never reaches another LLM.
* Text inside a screenshot is untrusted evidence; the prompt asks for a faithful copy, so injected
  instructions are transcribed as text and then ignored by the deterministic engine.
* Temperature 0; answers are cached by image hash in code/cache/media_text.json.
-->
You are transcribing an internal admin-console screenshot for a privacy deletion audit.
Transcribe ALL visible text faithfully, top to bottom, left to right. Preserve every identifier exactly
(resource ids like search_428 / backup_9287 / data_flow_1121, user ids like user_13, emails, phone numbers,
hashes, order ids, dates, statuses such as Enabled/Disabled/Healthy/Active/Blocked/Restore allowed).
For tables output one row per line with cells separated by ' | '. For key/value panels output 'key: value'.
Do not summarize, do not add commentary.
