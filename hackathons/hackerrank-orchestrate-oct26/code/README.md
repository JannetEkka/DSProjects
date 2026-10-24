# Ghost Ledger - deletion audit agent

Northstar Shop's dashboards said "Complete". This agent checks whether that is true. For every
request in `dataset/deletion_requests.csv` it decides whether deletion was asked for, finds every
copy of the person's data across 94 evidence files, reconstructs each record's state at `audit_at`,
applies `deletion_rules.csv`, and writes `COMPLETE` / `INCOMPLETE` / `NOT_APPLICABLE` with an
ordered, evidence-cited plan.

**Results on the 32 public samples** (`python3 code/evaluation/main.py`): status accuracy **100%**,
step F1 **99.2%** (29/32 exact), relative step order **100%**, 12/12 team-authored metamorphic tests pass. The full
518-case run takes about 9 s and passes a contract validator that checks every rule in the problem statement.

---

## Quick start

```bash
# from the repository root (the folder that contains dataset/)
pip install -r code/requirements.txt

# offline, deterministic (rule intent model + local OCR) - no key needed
python3 code/main.py --no-llm

# default: cached LLM/VLM answers in code/cache/ (no key needed, zero calls, reproduces output.csv)
python3 code/main.py

# refresh with live models: Gemini first, then any OpenAI-compatible fallback whose key is set
export GEMINI_API_KEY=...          # optional: GROQ_API_KEY / MISTRAL_API_KEY / NVIDIA_API_KEY
python3 code/main.py               # keys can also live in an uncommitted .env at the repo root
```

Outputs (repository root):

| File | What it is |
|---|---|
| `output.csv` | the submission: `case_id,deletion_status,steps_json`, 518 rows sorted by case id |
| `output.trace.jsonl` | one line per case: intent verdict, resolved identity, every linked resource with *why* it was linked, its state, evidence and policy rule |
| `output.usage.json` | model calls, tokens and cost for the run |

Other entry points:

```bash
python3 code/main.py --requests dataset/sample_deletion_requests.csv --out /tmp/sample.csv   # any request file
python3 code/evaluation/main.py                 # metrics + metamorphic suite + ablations -> evaluation/evaluation_report.md
python3 code/evaluation/build_usage_report.py --cold output.usage.json   # -> evaluation/usage_report.md
python3 code/ui/build_console.py                # -> code/ui/ghost_ledger.html (open in any browser)
```

## How it works

```mermaid
flowchart LR
  R[request_text] --> I{Intent<br/>Gemini JSON + rule model}
  I -- not deletion --> NA[NOT_APPLICABLE, []]
  I -- deletion --> ID[Identity resolution<br/>current + historical emails, phones, hashes]
  E[(94 evidence files<br/>SQL, JSON, 6 log dialects,<br/>text, PDF, screenshots)] --> N[Normalizer<br/>time-stamped observations]
  S[(system_activity.csv)] --> L
  ID --> L[Linking<br/>identifier match, verified catalog links,<br/>connector/restore lineage, workflow jobs]
  N --> L
  L --> ST[State at audit_at<br/>latest observation wins; claims ignored]
  ST --> P[Policy<br/>deletion_rules.csv]
  P --> O[Ordered steps<br/>findings, remediation, verification]
  O --> V[Contract validator]
```

1. **Intent** (`audit/intent.py`). An LLM (Gemini Flash, falling back to Groq `gpt-oss-120b`; 10 texts per batched call) classifies the request into DELETION / ACCESS / PORTABILITY /
   CORRECTION / MARKETING_OPT_OUT / ACCOUNT_SUPPORT with JSON output at temperature 0. A negation-aware
   multilingual rule model votes too and breaks disagreements (on this dataset the two agree on all
   550 request texts). A request is `NOT_APPLICABLE` when it negates deletion (negation tokens in 15
   languages inside the deletion cue's clause: "do not close", "nicht löschen", "削除しないで") or has no
   deletion cue at all. An empty or whitespace-only request states no purpose and is `NOT_APPLICABLE` without asking the LLM.
2. **Identity** (`audit/identity.py: IdentityResolver`). The request email may be current or historical.
   All emails, phones and email hashes ever held by the stable `user_id` come from `user_identities.csv`
   plus `user_audit_log.csv`. Names are never used to link because different customers share names.
   An address that no identity table knows is linked on the literal email only (no workflow
   attribution, no derived account id). If nothing matches it either, no personal data is in scope
   and nothing can be verified; since `COMPLETE` needs evidence-backed checks and `INCOMPLETE` needs
   evidenced findings, the agent writes the only contract-valid row, `NOT_APPLICABLE` with `[]`, and
   records the reason in the trace.
3. **Evidence normalizer** (`audit/evidence.py`). Each file becomes `Observation(evidence_id, time,
   system, resource, fields, lookup keys)`:
   * SQL snapshots are executed in in-memory SQLite. Primary, regional, reporting and failover replica
     tables are all kept, so replication drift shows up as a record that is gone from one table but
     present in another.
   * JSON exports, snapshot bundles and record digests are loaded.
   * Six log dialects (logfmt, RFC5424 syslog, JSON lines, bracketed, pipe-delimited, cloud-runtime
     with an escaped message) are parsed. Lines are grouped by `trace_id` so the lookup key on the
     `*_started` line identifies whose record the `*_completed` line returned.
   * Handover text, PDFs (pdfplumber) and screenshots (Gemini vision, or RapidOCR offline) are read too.
4. **Linking.** A resource belongs to the subject when:
   * an observation carries one of their identifiers (exact value, never a near-miss such as
     `g.silva76.jr@`);
   * a data-catalog link names them **and** the artifact it was registered from does not show someone
     else (the dataset contains a deliberate decoy: `marketing_001`);
   * an active connector or restore job repopulated one of their records (`data_flow_*`, `backup_*`);
   * or it was processed by **this request's own deletion workflow**. A scrubbed record (a 404 profile,
     an all-null analytics row) carries no identifier any more. The workflow's account job runs shortly
     before `reported_at`, and its result mirrors the reported claim (COMPLETE→SUCCESS,
     PARTIALLY_COMPLETE→PARTIAL, NOT_STARTED→FAILED). Jobs are assigned one-to-one across all requests.
   * **Workflow timing (chain linkage + lattice).** Learned from evidence-owned activity only: a
     workflow's policy actions are chained by exact gaps (390 s / 449 s, never seen between two
     different owners), and every workflow event sits at a fixed phase after its account job modulo
     30 s (one band per event template). An identifier-free record chained to someone's owned record
     inherits that owner; ambiguous account jobs and orphan records go only to the request whose
     account job is in phase, and nothing is attributed when two requests fit.
   * Evidence older than the same subject's *previous* request belongs to that request ("eras").
5. **State at `audit_at`.** The latest observation at or before `audit_at` wins. Workflow statuses and
   activity results are claims, so they are never treated as state. Records shown in screenshots and
   PDFs existed at capture time. Citations prefer a file captured by `audit_at`. Log exports are
   captured after their lines, so a line that predates `audit_at` is also accepted.
6. **Policy and ordering.** `deletion_rules.csv` maps each category to DELETE / REDACT / ANONYMIZE /
   RETAIN, with tombstones keeping only the stable user reference. Active flows are disabled and
   restores blocked first, then records are fixed, then the checks are listed. Within a phase, steps
   follow the operation order from the problem statement, then `system_id`, then `resource_id`. The
   account is always verified absent; retained security and legal records are verified present.
7. **Validator** (`audit/validate.py`) checks every `output.csv` against the contract (`main.py` prints every problem and exits with code 1 if there is any; all input CSVs are read as UTF-8 with or without BOM):
   * header, row count, sort order and JSON validity;
   * consecutive step numbers and the phase→operation→state table;
   * COMPLETE rows contain verification only, each with evidence;
   * INCOMPLETE future steps have an empty `evidence_id`;
   * every cited id exists and was observable by `audit_at`.

## Ghost Ledger console

`code/ui/ghost_ledger.html` is a single offline file built from the trace:

* a **claim vs. reality** matrix comparing what the workflow reported with what the evidence shows;
* findings by system;
* a searchable case ledger;
* a per-case dossier with the resolved identity (PII masked by default), an evidence timeline, a
  resource map (solid lines are identifier matches, dashed lines are workflow or catalog
  attributions), and every step expandable to show its evidence file, linkage and policy rule
  (plus a confidence chip and the assumptions behind a link, when the trace carries them).

Privacy and access: the page opens masked on every load (the unmask choice is never stored), and
search only matches what is on screen (case id, resource id, masked email while masked). Deep links
(`ghost_ledger.html#case_63`) work on load and on hash change; an unknown id says "case not found".
The case list is one tab stop (arrow keys move inside it), and a skip link jumps to the dossier.

## Evaluation

See `evaluation/evaluation_report.md` for:

* status, step, field, sequence and citation metrics;
* ablations showing what each component contributes;
* the metamorphic suite: historical email, upper-case email, negated and Hindi requests, time cutoff,
  catalog decoy, similar-email decoy, retention, workflow-chain attribution, unknown email, empty request, and a BOM + CRLF input copy;
* error analysis, including the cases we deliberately do not guess. Two sample gold steps
  (`audit_record_6645` in case_18, `audit_record_5569` in case_20) cite records that appear in no
  participant-visible file, so they cannot be derived. The organizers confirmed that scoring uses
  `deletion_requests.csv` only, so these two sample cases do not affect the score.

See `evaluation/usage_report.md` for tokens and cost.

## Failure handling and safety

Every failure has a detector and a defined degraded mode, and doubt resolves toward not deleting:
a refused or ambiguous decision is kept and flagged for a human rather than guessed.

| Failure | How it is detected | What the agent does |
|---|---|---|
| A model is rejected (bad key, retired alias, 400/401/403/404/422) | HTTP status in `LLMChain.generate` (`audit/llm.py`) | That model is put on a dead list for the run and the next model in the chain is tried (Gemini models, then Groq / Mistral / NVIDIA when their keys are set) |
| A model times out or rate-limits | exception after `TIMEOUT_S = 90` | `RETRIES_PER_MODEL = 3` with exponential backoff (2 s, 4 s), then the next model |
| The whole chain keeps failing | circuit breaker: `MAX_STRIKES = 3` consecutive items with no answer | `available` turns false and the run finishes on the local fallbacks; the log says so once |
| No API key, or `--no-llm` | `any_key()` | Rule intent model and local OCR (RapidOCR); cached answers are reused when present, so a keyless run reproduces `output.csv` |
| LLM returns bad JSON or a malformed batch | `json.loads` / schema check in `audit/intent.py` | The chunk falls back to per-item calls, then to the rule model for that text |
| Screenshot VLM fails | `RuntimeError` from the chain in `audit/media.py` | RapidOCR for that file only |
| An evidence file cannot be parsed | try/except per file in `audit/evidence.py` | The file is skipped and listed; `main.py` prints `parse errors: N` (0 on this dataset) |
| Unknown subject (email in no identity table) | `IdentityResolver` finds no `user_id` | Linked on the literal address only, with no workflow attribution; if nothing matches, the only contract-valid row, `NOT_APPLICABLE` with `[]`, and the reason in the trace (test 10) |
| Empty or whitespace request text | rule model, before any LLM call | `NOT_APPLICABLE` (test 11) |
| CSV with BOM or CRLF line endings | all inputs read as `utf-8-sig` | Identical predictions (test 12) |
| Two requests fit the same orphan record equally well | lattice/chain/window tests in `audit/workflow.py` | Not attributed (precision over recall); every candidate case gets a `needs_review` entry in the trace and a *needs review* chip in the console (14 records / 28 cases on the full run) |
| The LLM and the rule model disagree on intent | `audit/intent.py: classify` | Veto (LLM says deletion, text negates it) and override (LLM refuses a clear, negation-free deletion) both go to the rules; any negation-like token keeps the LLM's refusal with `needs_human_review` |
| Blurred timestamps | chain gaps must be sharp and supported by `MIN_SUPPORT = 10` evidence-owned pairs | Timing model is not learned; the engine falls back to the window rule (±2 s jitter gives output identical to the timing-off ablation) |
| Output breaks the contract | `audit/validate.py` | `main.py` prints every problem and exits with code 1 |

**Untrusted text.** Request texts, screenshot transcriptions, log lines and handover notes are data
(threat model: `code/audit/SAFETY.md`). The LLM sees only the request text, JSON-encoded with `<`/`>`
escaped inside `<untrusted_request>` tags, and the prompt says it is data, never instructions. Forged
role lines and "ignore previous instructions" sentences are stripped before the rule model scores the
text. `_clean` enforces a strict schema (boolean, `request_type` enum, the two consistent) on fresh and
cached answers; anything off-schema is decided by the rule model. Only the yes/no intent reaches the
engine: a text cannot add steps, cite evidence or set a state. Disagreements are decided by the rules
in both directions, asymmetrically toward not deleting (veto of a wrong "yes"; override of a refusal
only when the text carries no negation-like token at all), and recorded in the trace (0 of 550 on this
dataset). Screenshot text only feeds identifier
extraction; it never reaches a prompt that makes a decision. Claims (`reported_status`, activity
results) are never used as state. Secrets come from the environment or an uncommitted `.env` and are
never logged.

## Production monitoring

This is a design for running the agent daily. It is **not built yet**; today `main.py` writes
`output.usage.json` (calls, tokens, cost, cache hits), the per-case trace and the validator result,
which are the raw inputs for most of the signals below.

| Signal | Source | Alert when |
|---|---|---|
| Latency per request and per run | wall clock around `engine.audit` | p95 per request > 2x its 7-day median, or a run > 5 min |
| Model calls and cost per request | `output.usage.json` | cost per request > 3x baseline (today about $0.00004), or any call on a warm run |
| Cache hit rate | `usage.cache_hits` | intent hit rate < 90% on a re-run (prompt or model drift) |
| Fallback rate | chain log: dead models, breaker trips, OCR fallbacks | breaker trips on 2 runs in a row; any model newly marked dead |
| LLM vs. rule intent disagreement | trace `intent.agreement` | > 2% of texts (0% today); every disagreement goes to a review queue |
| Rows relying on inference | trace `linked_by` (workflow, chain, lattice, tie-break) | share of rows with a timing or tie-break link moves > 5 points (138 and 29 of 518 rows today) |
| Contract validator failures | `validate.py` exit code | any failure blocks publishing the run |
| Evidence parse errors by format | `EvidenceStore.parse_errors` | any new error, broken down by format (SQL, JSON, each log dialect, PDF, image) |
| Learned timing parameters | `_learn_workflow_timing` output (period, phase bands, chain gaps, support) | period or a chain gap changes, support < 2x `MIN_SUPPORT`, or the model stops learning |
| Status mix | `output.csv` | COMPLETE / INCOMPLETE / NOT_APPLICABLE share moves > 10 points day over day |
| Late citations | validator citation check | any citation after `audit_at` |

A daily dashboard would show: run health (validator result, parse errors, runtime), a cost and
calls panel with cache hit rate, an intent panel (disagreements, fallback engine share), an
inference panel (rows by link type, tie-break rows, learned timing parameters over time), and the
status mix with the claim-vs-reality matrix from the console. A shadow sample of rows each week
would be hand-checked to estimate accuracy outside the 32 public cases.

## Layout

```
code/
  main.py                    entry point (writes output.csv, trace, usage; exits 1 on a contract problem)
  check.sh                   quality gate: unit tests + full run + validator + evaluation
  audit/engine.py            thin facade wiring the modules below (public: AuditEngine, IdentityResolver)
  audit/identity.py          current + historical identifiers of a user_id
  audit/semantics.py         what one observation says: category, state, identifier match
  audit/linking.py           evidence -> resources, catalog-link verification, owner index
  audit/workflow.py          workflow attribution, one-to-one job assignment, learned timing model
  audit/planner.py           state at audit_at, policy -> ordered steps, confidence flags
  audit/config.py            tunable constants (windows, support thresholds), documented
  audit/evidence.py          evidence normalizer (all formats)
  audit/intent.py            intent: strict-schema LLM answers + rule model with veto
  audit/media.py             screenshot transcription (Gemini vision / RapidOCR)
  audit/llm.py               model chain: Gemini -> Groq / Mistral / NVIDIA, retries, circuit breaker
  audit/prompts.py           prompt loader; untrusted text JSON-escaped inside delimiter tags
  audit/validate.py          output contract validator
  audit/usage.py             token / cost ledger
  audit/SAFETY.md            threat model for untrusted request text and evidence
  prompts/*.md               versioned LLM prompts (intent single / batch, VLM transcription)
  tests/                     offline pytest unit tests (python3 -m pytest code/tests -q)
  evaluation/main.py         metrics, metamorphic + injection suite, ablations, held-out and perturbation checks
  evaluation/*.md            evaluation and usage reports
  ui/                        Ghost Ledger console (template + builder + built html)
  cache/                     content-hash keyed model responses (reproducible re-runs)
```

## Principles we held to

* **No hard-coded answers.** No case ids, labels or sample outputs are used in prediction; the gold is
  read only by `evaluation/main.py`.
* **Claims are not evidence.** `reported_status` and activity results never decide a state.
* **Precision over guessing.** When evidence cannot separate two requests, the agent does not invent a
  link; those cases are listed in the error analysis.
* **Secrets** are read from the environment or an uncommitted `.env`, and never logged.

## How we used AI to build this

The agent was built with Claude Code, split across sessions with separate jobs (all logged in
`log.txt`):

* **Build session**: evidence normalizer, engine, evaluation workflow, console.
* **Helper sessions** with API keys ran the live model chain (`HELPER_GEMINI_RUN.md`) and saved the
  answers to `code/cache/`, so the final code runs keyless and reproducibly.
* **Accuracy pass**: error analysis on the samples, which produced the learned workflow timing
  (chain linkage and the 30 s lattice) and the ablations that measure it.
* **Independent reviewer** with a read-only brief (`review/REVIEW.md`): a contract audit with its
  own checker, CLI and console QA. Its findings were fixed in a later commit.
* **Docs and console session**: these README sections and the console accessibility/privacy fixes.

Gates every change had to pass before it was pushed: the contract validator on the full 518-row
run, the evaluation suite (metrics, 12 metamorphic tests, ablations), a byte-identical keyless
clean-room run, a grep showing no case ids in the prediction code, and Playwright checks of the
console at 1440 and 400 px in light and dark themes.
