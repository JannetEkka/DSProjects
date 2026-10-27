# SQL Noir: text for the HackOS form

Plain text with straight quotes, ready to paste. The description has to be 150–2000 characters.

Demo video (3:43, unlisted): https://youtu.be/oX4KvIMfIbE
Repo: https://github.com/JannetEkka/sql-noir
Deck: https://claude.ai/artifact/XG1T6QdJ2Q2EYVN6sztp7Z (share it or export a PDF before submitting)

## Description

SQL Noir is a detective game that teaches SQL on real data. You get a case, like "list every return reason that mentions damage", and you crack it by writing a query. The query runs on Zetaris, on the TPCDS_DB and NY_TAXI sample databases, and the grader compares your rows with the answer's, value by value. If you're wrong, you see the evidence: the rows you shouldn't have and the rows you're missing. Right or wrong always comes from the data.

Your partner Nemo is a 1940s detective running on NVIDIA Nemotron through Meterless Nightshift. Nemo reads your attempt and the evidence and has a hint ready for 15 points. A critic checks every hint for answer values and pieces of the reference query before you see it. Once your result matches, you explain why your query proves it, and Nemo grades that too.

Before a case reaches you, a validator runs its reference query on Zetaris and checks it: read-only, has an answer, small, the same twice, no tie at the cut-off. It threw out two of my own cases. Nemotron can also write new cases aimed at your weakest skill, and the validator sends the drafts back until one is fair.

Memory is the Meterless H-MEM engine. It records what you got wrong, with a source and a confidence. The next case is picked to practise it, and Nemo reads those notes before helping. H-MEM passes its own conformance suite (13/13) on the engine the game uses, and the game has 50 tests. I'm a team of one: I pull, run, test and play every change in Cursor on my 16 GB Windows laptop, with Zetaris running in Docker and Nightshift alongside.

## Sponsor technology

Zetaris runs locally in Docker (Docker Desktop on WSL 2). It holds the data and runs every query over its REST API: the player's queries, each case's reference query (for the validator), and the DESCRIBE and sample-row reads behind the case files. Every query goes through a read-only guard first. Code: src/zetaris/client.ts, src/game/cases.ts, src/game/engine.ts.

Meterless H-MEM is the Meterless Engine in the game. It is the player's memory: mistakes and solved cases are H-MEM records with a source and a confidence, recalled before each case. A note that helped gets positive feedback, and each note's trust ledger opens with one click. The engine is vendored unmodified in vendor/meterless/hmem and passes its conformance suite, 13/13 (npm run conformance:hmem). Code: src/game/memory.ts.

Meterless Nightshift is the runtime provider for every model call, built to the Power prompt's contract: bearer token, meterless-app and meterless-scope headers, status from GET /v1/models, retries on 429. Code: src/meterless/provider.ts.

NVIDIA Nemotron runs behind Nightshift, on the Nemotron 3.5 Lightning 30B and Nemotron 3 Super 120B lanes. It is Nemo's voice, judges the player's explanations and writes new cases. The trace shows which model answered each call.

Cursor is where the game meets the real stack. On my laptop I pull each change in Cursor, run the tests, the smoke check and the case validator against my local Zetaris and Nightshift, start the game and play it. Claude Code wrote most of the code in cloud sessions, tested against stand-ins.

What's unusual: the model never marks an answer. A comparison of result sets on Zetaris does. Zetaris also checks the game's own content, so a case with a tie or a query too heavy for a laptop never reaches a player.

## Pre-existing components

vendor/meterless/hmem: the H-MEM reference and conformance suite from Meterless/Meterless, copied unmodified (Apache-2.0). Everything else was written during the hackathon window.
