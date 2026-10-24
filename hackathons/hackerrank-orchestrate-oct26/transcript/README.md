# Build transcript (all sessions)

The agent was built across six Claude Code cloud sessions: one orchestrator, plus five sessions it
started for parallel or long-running work. Each file below is a readable export of one session.
Each export contains:

* the participant's messages;
* the assistant's visible replies;
* a one-line summary of every tool call.

The exports leave out internal reasoning, system notices and raw tool output. API keys and the
participant's email are redacted. The participant asked for the mock-interview rehearsal to be left
out of the transcript.

The official `chat_transcript` upload is `../submission/log.txt`. These files are the long form.

| # | File | Session | Role |
|---|---|---|---|
| 1 | [01_main_orchestrator_session.md](01_main_orchestrator_session.md) | session_01ABdxWSQm1ctSj6anpiX5aJ | Orchestrator: brief analysis, first engine, organizer questions, planning, final verification |
| 2 | [02_gemini_helper_session.md](02_gemini_helper_session.md) | session_01Nbct7mtFqEizB27672S3Ur | Gemini intent and screenshot pass, model fallback, resumable runs |
| 3 | [03_multi_llm_run_session.md](03_multi_llm_run_session.md) | session_013TtYBt1dK4oPo3KQxWRVwj | Multi-provider run that filled the intent and media caches |
| 4 | [04_independent_review_session.md](04_independent_review_session.md) | session_01Gig6HxFo32t43CWcDJMtkY | Independent AI-judge and QA review |
| 5 | [05_accuracy_and_refactor_session.md](05_accuracy_and_refactor_session.md) | session_01H89kdKrn9aEhmGBzAcFxS6 | Accuracy work (workflow attribution, chains, lattice), refactor, fixes, final build |
| 6 | [06_docs_and_console_session.md](06_docs_and_console_session.md) | session_01LtbcmgYqjJz1ZsCgS1U2pQ | README sections and Ghost Ledger console polish |

To regenerate a file from a session's raw JSONL:

    python3 build_transcript.py <session.jsonl> <out.md> --title "..."
