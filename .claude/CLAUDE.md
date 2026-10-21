# Notes for Claude sessions in this repo

## Jannet's machine

This laptop is Jannet's only setup. Check every project and hackathon requirement against it before planning around local installs. Recorded 2026-10-20 from Jannet's screenshots.

- **Windows** laptop, **16 GB RAM, of which 13.8 GB is usable** (the rest is reserved for the integrated GPU). On 10-20, 12.1 GB was already in use after 5 days without a restart, so restart before heavy work.
- **CPU: AMD Ryzen 5 7520U**, 4 cores, 8 logical processors, virtualization enabled.
- **Graphics: AMD Radeon 610M, integrated, 2 GB.** Task Manager shows only GPU 0; there is no dedicated GPU.
- **C: (Windows-SSD), 274 GB.** About 10 GB free on 10-20; on 10-21 Jannet freed 20 GB and moved Downloads to `D:\Downloads`. C: still fills up easily, so put large installs, Docker's disk image, WSL distros, datasets and models on D:.
- **D: (New Volume), 199 GB.** On 10-21, after the moves: C: 33.8 GB free, D: 128 GB free.
- **Installed:** Docker Desktop 4.96.0 (Engine 29.9.1, Compose v5.6.0), updated 10-21. Its disk image was moved to D:, WSL integration is on for Ubuntu, and `hello-world` ran from Ubuntu. `%USERPROFILE%\.wslconfig` caps WSL at 7 GB of memory with 6 GB of swap on `D:\WSL\swap.vhdx`. Ubuntu is the default WSL distro.
- **Installed:** Zetaris (hackathon build 2.4.3.1) in Ubuntu at `~/zetaris-platform`, started 10-21. Its containers are postgres, driver, api and ui, all healthy; init and bootstrap exited 0. There's no ai-datasteward container. `./verify.sh` passed 9/9 on 10-21. Sign in at `localhost:3000` with the admin **email** (the org name fails with "Not Allowed"). Seeded Lightning databases: `NY_TAXI` and `TPCDS_DB` (39 tables). API keys live under Management → API Tokens. Ports: UI on 3000, REST API on 8888, JDBC on 10000. Preflight passed with one warning (WSL has 7 GB, under the recommended 8). Run `docker compose stop` / `docker compose start` from that folder. **Never** run `docker compose down -v` or prune images: the first pull of about 4 GB took about 3.5 hours.
- **Internet is slow:** about 4 GB of images took about 3.5 hours (10-21). Don't plan on big downloads during a deadline; start them early or avoid them.
- **Browser downloads still land in `C:\Users\janne\Downloads`** (10-21), not D:. Chrome's download location hasn't been changed yet.
- **Installed:** WSL 3.0.3 with **Ubuntu at `D:\WSL\Ubuntu`** (10-21), Linux user `planejane`. Jannet has sticky keys, so for passwords prefer pasting from Notepad over typing blind. A forgotten Linux password can be reset from PowerShell with `wsl -d Ubuntu -u root passwd planejane`.
- **Installed:** Cursor (downloaded 10-21). The hackathon's Cursor credit isn't claimed yet; as of 10-21 the organisers were still waiting on the sponsor for how to claim it.
- **Installed:** Meterless Nightshift, Windows edition (10-20). It runs on the 610M and serves the OpenAI-compatible runtime at `http://127.0.0.1:8088/v1`. It downloaded about 3.8 GB of local models (Llama 3.2 3B and others) into `%LOCALAPPDATA%` on C:. Two NVIDIA cloud lanes are set up (Nemotron 3.5 Lightning 30B, Nemotron 3 Super 120B), and a PowerShell request through the runtime was answered by NVIDIA on 10-20. While it ran, the laptop hit cpu 96%, mem 94% and "thermal hot", so quit Nightshift when it isn't needed.

What this means when planning:

- Anything that needs a dedicated or NVIDIA GPU on the laptop is out: CUDA and local LLMs beyond small ones (Nightshift runs Llama 3.2 3B locally). Prefer free cloud endpoints, such as NVIDIA's build.nvidia.com models through Nightshift.
- Docker runs through WSL 2. With 13.8 GB usable, a container stack that wants 8 GB leaves about 6 GB for Windows, an editor, a browser and screen recording. Cap WSL's memory and stop containers when they aren't in use.
- Claude works in cloud sessions and cannot reach the laptop's `localhost`. Anything that must run locally is a step Jannet does, so say exactly what to run and what output to send back, and never ask for keys in chat.

## Hackathon rules and status

Decisions and Jannet's standing rules (no hackathon that needs our own money, and the rest) are in [hackathons/october-2026.md](../hackathons/october-2026.md). Progress for each entry is in its GitHub issue (label `hackathon`).
