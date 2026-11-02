# VerseCanvas: poem to artwork with Gemini and Imagen

**Personal project, built Jun 5–8, 2025** (Gen AI Academy 2025 era). Streamlit Cloud deployment.
**Live:** [versecanvas.streamlit.app](https://versecanvas.streamlit.app/) (user-confirmed live per `_portfolio_src/data.py`) · **Code:** [github.com/JannetEkka/versecanvas](https://github.com/JannetEkka/versecanvas) (MIT) · ~3,000 lines of Python

## The 30-second version

Paste a poem and VerseCanvas turns it into original artwork. **Gemini 2.0 Flash** (`gemini-2.0-flash-001`) analyses themes, mood and visual elements into a structured analysis, prompt synthesis turns that into image prompts, **Imagen 3.0** (`imagen-3.0-generate-002`) on Vertex AI generates 1–3 interpretations, and an editor adds brightness, contrast, blur and a text overlay of the poem. Six languages, six art styles, a mood-intensity slider (0.1×–2.0×).

What it shows: an early end-to-end GenAI pipeline with two models chained through a structured intermediate (analysis → prompt). **It has no measured quality metric and no users I can quote**, so in an FDE interview it's a "how I'd harden it" project, not a results project.

## 1. Architectural reasoning

### Database / storage
- **None.** State lives in Streamlit's session (generated images, edits, carousel position). Images are downloaded as PNGs and never stored server-side. For a single-session creative tool that's correct: there's nothing to keep, and no user data to protect at rest.

### Compute & hosting
- **Streamlit Community Cloud** (free) runs the app; the heavy compute is managed APIs (Vertex AI for Gemini and Imagen), so the app server only orchestrates.
- Why not serverless functions + a separate frontend: Streamlit gave a full UI in Python in a weekend. The trade-off is limited control of concurrency and layout (the UI had to be changed to vertical, and several fixes were Streamlit image and session quirks).

### Frameworks & libraries
- `google-genai` / Vertex AI SDK (`ImageGenerationModel.from_pretrained`), Streamlit, Pillow for editing and text overlay. Modules split by job: `poem_analyzer.py`, `image_generator.py`, `image_editor.py`, `text_overlay.py`.

## 2. Data & security pipelines

### Authentication & access control
- **No user accounts.** The app authenticates to Vertex AI with a **GCP service account**, read from **Streamlit secrets** (`st.secrets`), supporting both a JSON blob (`GOOGLE_CREDENTIALS`) and a field-by-field TOML table (`google_credentials`). The history shows a day of fixes getting that right (Jun 7: "secrets parsing", "credentials", "toml configuration", "streamlit authentication"), and one commit message says it **removed sensitive files**. Own it: an early project where credentials handling was learned in public. If asked how I'd do it now: Workload Identity or a secret manager, a least-privilege SA (`roles/aiplatform.user` only), and rotate any key that ever touched the repo history.
- A `debug_credentials()` helper in `app.py` displays which secret format was found. It shows key names and project ID, not values. I'd remove it in production.

### Data ingestion & flows
- Synchronous: poem → Gemini analysis (structured JSON) → prompt per style → Imagen (1–3 images) → client-side edits → download.

### Privacy & compliance
- Poems go to Google's APIs; nothing is stored by the app. Imagen runs with `safety_filter_level="block_few"`.

## 3. Reliability & failure operations

### State management
- Streamlit session state keeps the carousel and the cumulative edits, with "reset to original". A browser refresh loses the session, which is acceptable for this use.

### Error handling & fallbacks
- JSON parsing of the analysis is wrapped (`JSONDecodeError`, `KeyError`, `ValueError`), and many broad `except Exception` blocks surface errors in the UI. **Honest weakness:** broad excepts and a bare `except:` can hide the cause. Today I'd apply the rule from SMT: no silent fallback, log the reason, and flag degraded output.

### Logging & observability
- UI progress messages only. There's no structured logging or usage tracking.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **None measured.** No user study, no image-quality metric, no latency numbers recorded. If asked: I'd measure time-to-first-image, the Imagen safety-block rate per style, and a small human preference test (analysis-driven prompt vs the raw poem as prompt), which is the comparison that would justify the two-stage pipeline.

### Cost & resource efficiency
- Free hosting; pay-per-call Vertex AI at the time (Imagen is the expensive call, so 1–3 images per request is user-controlled).

### System constraints
- Streamlit Community Cloud limits (sleeping apps, shared resources), Imagen quotas and safety filtering, and the model versions of mid-2025.

## What the history shows (real decisions)
- Jun 5: initial project with all features. Jun 6: UI to vertical, edit and reset fixes, a dev container, Streamlit secrets support. Jun 7: about 15 commits on secrets and credentials parsing for Streamlit Cloud. Jun 8: the text overlay made always-on, README.

## Weak spots to own before they ask
- Credentials handling learned the hard way; no tests; no metrics. It's the "before" picture for how I build now.

## Sources
`README.md`, `app.py`, `image_generator.py`, `poem_analyzer.py`, git log Jun 5–8, 2025; `_portfolio_src/data.py` link-status note.
