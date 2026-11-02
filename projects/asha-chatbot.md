# Asha Chatbot: a career assistant for the JobsForHer Foundation

**Asha AI Hackathon 2025** (JobsForHer Foundation × Hack2skill; certificate of participation 2025H2S03AAIH-P00105). Built Apr 17–27, 2025.
**Code:** [github.com/JannetEkka/asha-chatbot](https://github.com/JannetEkka/asha-chatbot)

## The 30-second version

A chatbot for women returning to or advancing in work: **job search** (by role, location and experience, with contextual refinement), **events and sessions**, **mentorship**, career resources and FAQs about JobsForHer, plus conversation actions on networking and gender bias. Built on **Rasa Open Source** (intent classification and dialogue management) with ~960 lines of custom actions, a web chat widget styled to match HerKey, and job and session data from CSV/JSON.

It's **not an LLM bot**. That's worth saying, because it's a deliberate contrast: Rasa gives deterministic, testable dialogue and never invents a job listing. The cost is that it only understands what it was trained on.

## 1. Architectural reasoning
- **Database:** CSV and JSON files (`job_listing_data.csv`, `Session Details.json`), a hackathon-sized dataset. A real deployment would read the partner's jobs API.
- **Compute:** a Rasa server + an actions server + a static `index.html` chat widget over Rasa's **socket.io channel** (`session_persistence: true`). A long-lived server, because Rasa holds conversation trackers.
- **Framework:** Rasa's default NLU pipeline (DIET classifier, featurizers, `FallbackClassifier`) and default policies (Memoization, Rule, TED), with no custom tuning in `config.yml`.

## 2. Data & security pipelines
- **No user auth.** `credentials.yml` only enables the `rest` and `socketio` channels (no secrets in it).
- **Flow:** user message → NLU intent + entities (role, location, experience) → slots → custom action filters the CSV → response, with **alternatives when nothing matches**.
- **Privacy:** no personal data stored beyond the conversation tracker. A real deployment would need a retention policy for trackers, since career questions can be sensitive.

## 3. Reliability & failure operations
- **Slot persistence fix:** location and experience were being lost when a user changed role (README "Recent updates"). Fixed, so refinements keep context.
- A `FallbackClassifier` for low-confidence intents, and a `test_connection.py` for the widget connection ("Fixed rasa chat widget issue. Connection test passed.", Apr 20).

## 4. Evaluation & optimisation metrics
- **Not measured:** no intent-accuracy report, no conversation success rate. If asked: Rasa's `rasa test` (intent F1 and story success) on a held-out set, and the share of job searches that end in a listing or a useful alternative.
- **Constraints:** a CSV dataset; English-only training data; coverage limited to trained intents.

## Sources
`README.md`, `config.yml`, `credentials.yml`, `data/`, `actions/actions.py`, git log Apr 17–27, 2025; `_portfolio_src/data.py` (certificate).
