# Build transcript

The official `chat_transcript` upload is `../submission/log.txt`. It has one entry for each piece of
work, from all six Claude Code sessions that built the agent.

[01_main_orchestrator_session.md](01_main_orchestrator_session.md) is the long, readable form of the
orchestrator session. That session planned the work and started the other five sessions. It also
asked the organizers about the data, and it verified every build. The work of the other sessions
appears here through their briefs and reported results, and in `log.txt`.

| Session | Role |
|---|---|
| session_01ABdxWSQm1ctSj6anpiX5aJ | Orchestrator: brief analysis, first engine, organizer questions, planning, final verification |
| session_01Nbct7mtFqEizB27672S3Ur | Gemini intent and screenshot pass, model fallback, resumable runs |
| session_013TtYBt1dK4oPo3KQxWRVwj | Multi-provider run that filled the intent and media caches |
| session_01Gig6HxFo32t43CWcDJMtkY | Independent AI-judge style review and QA |
| session_01H89kdKrn9aEhmGBzAcFxS6 | Accuracy work (workflow attribution, chains, lattice), refactor, fixes, final build |
| session_01LtbcmgYqjJz1ZsCgS1U2pQ | README sections and Ghost Ledger console polish |

**Curation.** The participant asked for the transcript to keep only what is relevant to building
and judging the project. The readable export therefore leaves out:

* greetings and logistics;
* the participant's own interview preparation and rehearsal;
* asides that did not shape the project.

It also leaves out internal reasoning, system notices and raw tool output, and redacts API keys and
the participant's email.

`log.txt` is curated the same way: off-topic entries are removed, and the remaining entries are in time order.

To regenerate the export from the session's raw JSONL:

    python3 build_transcript.py <session.jsonl> 01_main_orchestrator_session.md \
        --title "Session 1: Orchestrator (session_01ABdxWSQm1ctSj6anpiX5aJ)" --curation curation_01.json
