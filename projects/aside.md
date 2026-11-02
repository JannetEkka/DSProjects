# Aside: a Fire TV companion that never spoils the film

**Build, Ship, Shape: Amazon Developer Hackathon, Fire TV track.** Built Oct 20–22, 2026, submitted Oct 22. Judging Nov 9–20, winners ~Dec 3.
**Live TV app (browser):** [aside-tv.onrender.com/tv/](https://aside-tv.onrender.com/tv/) · **Code:** [github.com/JannetEkka/aside-tv](https://github.com/JannetEkka/aside-tv) (MIT) · video 2:57 [youtu.be/8459XKUURhs](https://youtu.be/8459XKUURhs) · [friction log](https://github.com/JannetEkka/aside-tv/blob/main/docs/FRICTION_LOG.md)

## The 30-second version

Somebody always steps out during a film, and today they pause everyone, ask the person next to them, or search online and get spoiled. Aside is an AI that knows the film only up to the second you've watched. Press **Up** on the Fire TV remote for "What just happened?", "Who's that?", "Describe the scene", "What did I miss?" or "Story so far", or ask anything by voice from your phone through a QR code. It also writes and narrates **audio description** in the gaps between dialogue, because hand-written audio description doesn't exist for most titles.

It runs on a real **Fire TV Stick 4K Select (Vega OS)**, built from Amazon's `vegaWebview` template, and on Fire OS through a Kotlin wrapper.

**Measured spoiler safety** (`eval/spoilers.py`, 24 questions over two films, 16 written to pry the future out, graded by a separate judge model that sees the whole film):

| Setup | Spoiled a future-probing question | Helpful on past questions |
|---|---|---|
| Whole film in the prompt, told not to spoil | 6 of 16 | 7 of 8 |
| Only what you've seen | 1 of 16 | 8 of 8 |
| **Aside: only what you've seen + spoiler check** | **0 of 16** | **8 of 8** |

Telling the model not to spoil isn't enough. Most of the gain comes from never giving it the future.

## 1. Architectural reasoning

### Database / storage
- **No database. Each film's knowledge is a JSON timeline** (`data/films/*/timeline.json`): scenes, characters, and facts each tagged with the second they appear on screen. It's built once per film by Gemini watching the video with the subtitles. A question at 08:12 is answered from a filter over that file (`seen(08:12)`), not from a retrieval index. The data is small, fully known in advance and keyed by time, so a vector DB would add nothing and could leak future facts through similarity.
- **Prepared answers on disk:** the one-button answers are generated every 30 seconds of film ahead of time, spoiler-checked like live ones, and pre-voiced with Kokoro into `data/voice/`. They're served from the latest moment at or before the viewer's position.
- **Phone pairing is in-memory:** `ROOMS` dict keyed by a 4-letter code (alphabet without look-alike letters), expiring after 6 hours. There's no persistence, because pairing is ephemeral by nature.

### Compute & hosting
- **FastAPI on Render's free plan** (`render.yaml` Blueprint). The heavy work (video understanding, audio description, voice rendering) is an **offline pipeline run once per film**, so the live server only does cheap filtering plus one answer and one check call.
- **Why not on-device:** a Fire TV Stick can't run the models, and the TV only ever downloads titles, captions and audio description. **The full timeline never leaves the server**, otherwise the TV app itself would be a spoiler source.
- **Client side:** the TV UI is plain JavaScript (ES2017, no build step) on a fixed 1920×1080 stage with geometric D-pad focus, wrapped by a Vega WebView (React Native for Vega) and by a Kotlin WebView for Fire OS.

### Frameworks & libraries
- **Gemini video understanding** for the timeline (scene edges snapped to real shot cuts found with ffmpeg).
- **Groq-hosted open models** (gpt-oss-120b, Qwen 3.8 27B, gpt-oss-20b) for answers, with Gemini Flash and Gemma as backups. Groq answered in 1–2.5 s; the free tiers are small, hence the ladder.
- **Kokoro-82M** (Apache 2.0) for narration, rendered offline. It replaced Piper after Jannet found Piper hard to understand.
- **Vega's WebView has no speech API** (friction-log FL-5), so `/api/speak` renders speech server-side: pre-recorded Kokoro first, then Groq's Orpheus, then Gemini's speech model.
- WebVTT export (`descriptions.vtt`, `captions.vtt`) so any player can use the audio description.

## 2. Data & security pipelines

### Authentication & access control
- **No user accounts.** The phone joins a TV "room" by scanning a QR holding a 4-letter code. Codes expire after 6 hours of inactivity and are pruned on each new room. If asked: it's guessable in principle (20^4 = 160,000 codes) and protects nothing sensitive, since a stranger could only ask a film question. For production I'd lengthen the code and rate-limit joins.
- **API keys** (Gemini from an AI Studio project named AsideTV, Groq) live only in Render's environment, never in the repo.
- **The spoiler boundary is an access-control problem:** the answer model only gets facts up to the viewer's position, and Aside's knowledge ends at the *furthest point actually watched*, so rewinding doesn't move it forward. The check model is the only component allowed to see the future, and only to judge.

### Data ingestion & flows
- **Offline batch per film:** `analyze.py` → `describe.py` (audio description word-budgeted to each silent gap at 2.5 words a second) → `publish.py` (narration levelled to −16 LUFS and fitted to gaps; WebVTT) → `voice.py` → `prepare.py`.
- **Live, request/response:** question + position → `seen(position)` → answer model → spoiler check (sees what's been seen *and* what's ahead) → clean answer, or a rewrite, or a fallback recap.
- **Phone ↔ TV is polling, not WebSockets:** the phone posts into the room's inbox; the TV polls it (it alone knows where the film is), answers, and posts the answer back. Polling survives a free host's sleeps and proxies without connection management.

### Privacy & compliance
- The questions go to third-party APIs (Groq, Google). There's no personal data beyond the question text, and nothing is stored beyond the in-memory room.
- **Licensing was a submission constraint:** no third-party copyrighted footage. The demo films are Sintel and Tears of Steel (Blender Foundation, CC BY 3.0), credited in the README. Timelines and descriptions derived from them carry the same licence.

## 3. Reliability & failure operations

### State management
- Playback position and the "furthest watched" mark live in the TV client. 10-22 fixes: the player keeps the server awake and **resumes the film after a dropped connection**, plays voice and description audio from memory, and goes back into the film after a reload.

### Error handling & fallbacks
- **Model ladder:** Groq (three models) → Gemini Flash → Gemma, moving on as soon as a model is busy or slow (12 s). The judge tries Groq models in reverse order, so it's rarely the answer's own author. `/api/eval/models` lists recent model failures to see which free tier is out of quota.
- **Spoiler fallbacks:** if a button answer still leaks after a rewrite, Aside answers with a **plain recap stitched from the timeline's own facts up to now, with no model involved**. A free-form question gets "That's still ahead of us, so no spoilers from me". Button questions never come back empty.
- **Voice never fails:** a failed media request blanks the Vega shell with its offline screen, so `/api/speak` returns a short silence (HTTP 200) when every engine is out of free quota, instead of a 503. Rate limits (Groq's 10 requests a minute) are waited out with the same voice rather than switching voices mid-narration.
- **A native "Try again" screen** in the Vega app covers a sleeping server.

### Logging & observability
- **The TV reports its own errors** (video, voice, AD, script) to `/api/client-log`, readable at `/api/eval/client-log`, so a failure on the physical stick can be diagnosed from the server. There's no screen capture on Vega (FL-6), so this was the only window into the device.
- `/health` shows the deployed commit, and prepared answers made before a check fix were dropped (10-20), so stale behaviour couldn't hide.
- `ASIDE_EVAL=1` returns rejected drafts and the check's reasons with each answer, to tune the check.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **Spoiler eval:** 6/16 → 1/16 → 0/16, run through the *deployed* server with a separate judge model. Honest caveat from the README: in that run the check didn't need to rewrite anything, so the gap between the last two rows is within run-to-run variation.
- **The check did catch a real leak on the live server:** asked at 09:00 whether the cave dragon is Scales, an answer model said "No, it's a different dragon", which is false and rules out the twist. The check stopped it, and the prompt rule against asserting or denying unconfirmed identities came from that case.
- **A false-positive fix:** the check first had only the *later* facts, so it couldn't tell "she named him Scales" (shown at 03:48) from a spoiler, and it flagged honest recaps at 04:01. It now sees the seen facts and the names already known. It also stopped treating "we don't know yet" as a hint.
- **Baseline for the product claim:** Prime Video's X-Ray Recaps summarises a season or episode up to your minute for Amazon MGM originals. Aside adds two-way questions, "what did I miss" for a span, generated audio description and a measured spoiler check, on any film it's given. That's a feature comparison, not a measured one.

### Cost & resource efficiency
- ₹0: Render free plan, free Gemini and Groq tiers, Kokoro offline. Pre-computed answers every 30 s keep buttons instant when the free tiers are busy and spend no API calls at view time.
- One constraint shaped the pipeline: the environment's Gemini key was on **20 requests per model per day**, used up by the two timelines on day 1. Groq's Orpheus voice allows only 3,600 tokens a day, which is why narration moved to offline Kokoro.

### System constraints
- Free hosting: the first load can take a minute (hence keep-awake and "Try again").
- Groq's tokens-per-minute limit forced fewer audio-description lines in the prompt notes.
- Two films. Adding one is a pipeline run, but the spoiler quality depends on the timeline Gemini writes.
- Only 6 unit tests (`tests/test_knowledge.py`, the `seen()` boundary). Most verification was the deployed eval and device runs.

## What the history shows (real decisions)
- **Oct 20, rules → plan:** the judges listed "basic streaming UI" as obvious and "AI-enhanced viewing" and "multi-modal UX combining voice + D-pad + visual" as creative. Aside targets both. The AWS Builder mini-challenge was skipped because it needed AWS services and the credit codes had run out (the no-own-money rule).
- **Oct 20, ~22:00 IST:** pipeline, server, TV app, phone remote and Fire OS APK were built in one session; checked in headless Chromium at 1920×1080. Server live at 23:30 IST.
- **Oct 21, 02:30 IST, the device surprise:** Jannet's stick is **Vega OS**, which doesn't run Android APKs. The shell was rebuilt from Amazon's `vegaWebview` template (SDK 0.24) that night. Developer Mode needed the Vega CLI, which is macOS/Linux only, so the cloud session ran `vega devmode login` while Jannet approved in her browser. Install went through Google's plain `adb` (Vega's `vda` is a renamed adb). All eight blockers became the friction log, which can earn up to a 10% bonus.
- **Oct 22:** Kokoro voice, demo video (2:57, screen recording of the TV app because Vega can't screen-record), submitted; then reliability fixes the same evening (keep-awake, resume, never-failing voice endpoint, client error reporting).

## Weak spots to own before they ask
- The 0/16 vs 1/16 difference isn't statistically meaningful on 16 questions; the 6/16 → ~0 difference is the real result.
- The demo video shows the web app in a desktop browser, not the stick itself. That was a Vega limitation, and the README says so.
- Built with Claude Code as the coding assistant, directed and reviewed by me. My part: the product, testing on my own stick, and the voice-quality call.

## Sources
`README.md`, `docs/FRICTION_LOG.md`, `server/app.py` (rooms), git log Oct 20–22 with server commit bodies; [DSProjects#21](https://github.com/JannetEkka/DSProjects/issues/21) comments 10-20, 10-21 and 10-22.
