# Ghost Ledger - deletion audit agent

Northstar Shop's dashboards said "Complete". This agent checks whether that is true. For every
request in `dataset/deletion_requests.csv` it decides whether deletion was asked for, finds every
copy of the person's data across 94 evidence files, reconstructs each record's state at `audit_at`,
applies `deletion_rules.csv`, and writes `COMPLETE` / `INCOMPLETE` / `NOT_APPLICABLE` with an
ordered, evidence-cited plan.

**Results on the 32 public samples** (`python3 code/evaluation/main.py`): status accuracy **100%**,
step F1 **99.2%** (29/32 exact), relative step order **100%**, 9/9 team-authored metamorphic tests pass. The full
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
   multilingual rule model votes too and disagreements are recorded in the trace (on this dataset the
   two agree on all 550 request texts). A request is
   `NOT_APPLICABLE` when it negates deletion ("not asking for deletion", "do not close") or states a
   non-deletion purpose with no deletion cue.
2. **Identity** (`audit/engine.py: IdentityResolver`). The request email may be current or historical.
   All emails, phones and email hashes ever held by the stable `user_id` come from `user_identities.csv`
   plus `user_audit_log.csv`. Names are never used to link because different customers share names.
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
7. **Validator** (`audit/validate.py`) checks every `output.csv` against the contract:
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
  attributions), and every step expandable to show its evidence file, linkage and policy rule.

## Evaluation

See `evaluation/evaluation_report.md` for:

* status, step, field, sequence and citation metrics;
* ablations showing what each component contributes;
* the metamorphic suite: historical email, upper-case email, negated and Hindi requests, time cutoff,
  catalog decoy, similar-email decoy, retention, and workflow-chain attribution;
* error analysis, including the cases we deliberately do not guess.

See `evaluation/usage_report.md` for tokens and cost.

## Layout

```
code/
  main.py                    entry point (writes output.csv, trace, usage)
  audit/evidence.py          evidence normalizer (all formats)
  audit/engine.py            identity, linking, state, policy, step planner
  audit/llm.py               model chain: Gemini -> Groq / Mistral / NVIDIA, retries, dead-model list
  audit/intent.py            intent classifier (batched LLM + rule model) and prompts
  audit/media.py             screenshot transcription (Gemini vision / RapidOCR) and prompt
  audit/validate.py          output contract validator
  audit/usage.py             token / cost ledger
  evaluation/main.py         evaluation workflow
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
