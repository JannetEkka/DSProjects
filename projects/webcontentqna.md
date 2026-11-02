# WebContentQnA: ask questions about any set of web pages

**Personal project, built Feb 24–25, 2025.** Flask backend + React/Bootstrap frontend.
**Code:** [github.com/JannetEkka/WebContentQnA](https://github.com/JannetEkka/WebContentQnA)

## The 30-second version

Paste one or more URLs and ask questions; answers come only from the extracted page text. It's extractive QA with **five interchangeable models**: TF-IDF + spaCy (lightweight default), NLTK advanced, Sentence Transformers, TensorFlow, and **DistilBERT** (most accurate, heaviest), with a confidence score and per-session question history.

It's the pre-LLM version of RAG: retrieve sentences, then extract a span. Its useful lesson is the **model ladder**: if the requested model isn't loaded, the server **falls back to the default and logs a warning**, which is the same shape as the model fallbacks in my later projects.

## 1. Architectural reasoning
- **Storage:** none; content is extracted per request (BeautifulSoup + html2text) and held in memory. Large model files are tracked with **Git LFS**.
- **Compute:** a Flask server (`/api/extract`, `/api/answer`, `/api/models`). Model choice is per request (`model_type`), so a laptop can run TF-IDF while DistilBERT is optional.
- **Why multiple models:** a resource vs accuracy trade-off the user can see. DistilBERT needs PyTorch/TF and RAM; TF-IDF runs anywhere.

## 2. Data & security pipelines
- **No auth; CORS open to all origins** (`CORS(app)`). Fine for localhost, not for a deployment.
- **Security point to raise myself:** the server fetches arbitrary user-supplied URLs, which is a classic **SSRF** risk (it could be pointed at internal addresses or cloud metadata endpoints). A deployment needs URL scheme and host allow-listing, blocking of private IP ranges, size and time limits on fetches, and rate limiting.
- Errors processing a URL return a 500 with the error text, which could leak internals; I'd sanitise that.

## 3. Reliability & failure operations
- **Explicit model fallback with a warning log** when a requested model isn't available. Logging to `distilbert_debug.log` (committed, which it shouldn't be).
- One failed URL fails the whole extract request; a per-URL partial result would be better.

## 4. Evaluation & optimisation metrics
- **Not measured.** No QA benchmark was run across the five models. If asked: a small labelled set (questions + answer spans from saved pages), exact-match and F1 per model, and latency per model, so the "most accurate" claim for DistilBERT becomes a number.
- **Constraints:** extractive only (answers must be spans in the text); JavaScript-rendered pages aren't handled by BeautifulSoup.

## Sources
`README.md`, `app.py` (routes, fallback), `DualApproachSetupInstructions.md`, git log Feb 24–25, 2025.
