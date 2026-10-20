# Notes for Claude sessions in this repo

## Jannet's machine

This laptop is Jannet's only setup. Check every project and hackathon requirement against it before planning around local installs. Recorded 2026-10-20 from Jannet's screenshots.

- **Windows** laptop, **16 GB RAM**.
- **Graphics: AMD Radeon 610M, integrated.** No dedicated GPU has been seen. If Task Manager → Performance lists a second GPU, update this line.
- **CPU:** not recorded yet (Task Manager → Performance → CPU shows name, cores and logical processors).
- **C: (Windows-SSD), 274 GB, about 10 GB free.** C: is nearly full. Put large installs, Docker's disk image, WSL distros, datasets and models on D:.
- **D: (New Volume), 199 GB, about 137 GB free.**

What this means when planning:

- Anything that needs a dedicated or NVIDIA GPU on the laptop is out: CUDA, local LLMs beyond tiny ones, and tools whose requirements say "dedicated graphics card" (for example Meterless Nightshift's Windows edition). Prefer free cloud endpoints.
- Docker runs through WSL 2. A container stack that wants 8 GB leaves little room for an editor, a browser and screen recording at the same time.
- Claude works in cloud sessions and cannot reach the laptop's `localhost`. Anything that must run locally is a step Jannet does, so say exactly what to run and what output to send back, and never ask for keys in chat.

## Hackathon rules and status

Decisions and Jannet's standing rules (no hackathon that needs our own money, and the rest) are in [hackathons/october-2026.md](../hackathons/october-2026.md). Progress for each entry is in its GitHub issue (label `hackathon`).
