# Independent review: Ghost Ledger (HackerRank Orchestrate, Oct 2026)

Reviewed build: commit `ac52ad7` ("Accuracy pass: learned workflow timing"), `submission/code.zip`
(277,558 bytes). Clean room: `/tmp/cr` = unzipped `code.zip` + `dataset/` from a fresh
`git clone --depth 1` of `interviewstreet/hackerrank-orchestrate-october26`. Reviewer wrote only into
`review/`; no existing code or doc was edited. All checker scripts are in `review/tools/` (`check.py`
is an independent contract checker; it does not reuse `code/audit/validate.py`).

## Executive summary

* **Blockers: none.** The keyless default run reproduces `submission/output.csv` byte for byte. My
  independent checker finds 0 contract violations in 518 rows. Sample results reproduce exactly
  (32/32 status, 29/32 exact, step F1 0.992).
* **Majors:**
  1. A requests CSV with a UTF-8 BOM crashes with `KeyError: 'case_id'`.
  2. An unknown email produces `COMPLETE,[]`, the validator flags it, and the run still exits 0.
  3. Empty or cue-less request text defaults to "authorizes deletion" (`intent.py:82`).
  4. 29 of the 518 rows hinge on an arbitrary tiebreak (`TIEBREAK_EARLIEST`) that the samples cannot
     distinguish.
  5. 138 of the 518 rows (27%) hinge on the timing model, which encodes a generator fingerprint
     (exact 30 s lattice, exact chain gaps). ±2 s of timestamp jitter switches the timing model off
     completely. It degrades gracefully, back to the no-timing ablation.
  6. All headline metrics are in-sample: the dev log tunes against the same 32 gold cases (3/32 →
     29/32 exact).
* **Predicted AI-judge score: about 7.5/10.** Rigor, determinism and documentation are strong. It
  will be marked down where the judge probes overfitting of the timing rules, in-sample evaluation
  and a usage report that does not describe one coherent run.
* **Section D (live LLM calls) was not run** (see D for why). The push is also held for owner
  confirmation, and the commit is local.

---

## A. Mock AI-judge interview

This section uses only what is in the zip. Line numbers refer to the zipped `code/`.

| # | Question a judge would ask | Best answer the code supports | Weakness it exposes |
|---|---|---|---|
| 1 | Walk me through one INCOMPLETE case end to end. | intent (`audit/intent.py`) → `IdentityResolver.resolve` (`engine.py:141`) → observations (`evidence.py`) → `_linked_resources` (`engine.py:443`) → `state_at` (`engine.py:796`) → `audit` (`engine.py:823`) with policy, then ordering. A per-case trace is in `output.trace.jsonl`. | None. The trace is a real strength; show it live in the console. |
| 2 | Your accuracy is measured on the same 32 cases you tuned against. Why trust 99.2%? | The dev log (`evaluation_report.md` §5) is honest about it, and there are 9 metamorphic tests. | **No held-out split.** Every fix in §5 is scored on the 32 gold cases (3 → 29 exact). Leave-k-out or k-fold over the 32, or a synthetic hold-out, is the obvious missing step. |
| 3 | `_learn_workflow_timing` finds a 30 s lattice and chain gaps of 390/449 s. Is that a real-world regularity or a quirk of the data generator? | It is learned without labels, only from activities that evidence ties to exactly one owner (`engine.py:577-667`). The `MIN_SUPPORT=10` gate (`:566`) and the "never separates two owners ±1 s" test (`:637-640`) make it falsifiable. 328/328 owned pairs fit. | Real deletion workers do not emit events on a 30 s phase lattice. This reverse-engineers the **generator's scheduler**. It is principled as "learn regularities from labelled-by-evidence data", but it is not domain logic and would not transfer. A judge will ask "what does production do?" The honest answer is "falls back to the window rule". I confirmed that: with ±2 s jitter the lattice is not learned, and the output equals the `DISABLE_TIMING` ablation exactly. |
| 4 | How many test answers depend on the timing model? | The ablation in the report covers samples only (exact 90.6% → 71.9%). | Reviewer measurement: **138/518 rows change** without timing (152 resources added, 63 removed, 0 status flips). That is a large, unverifiable share of the hidden-set answer. |
| 5 | When two account jobs tie, which wins and why? | `TIEBREAK_EARLIEST = True` (`engine.py:686`, used at `:769`). Requests with one remaining candidate are processed first. Otherwise processing is in `min(pending)` order (`:767`), which is a **string** sort of case ids. | Flipping the tiebreak leaves the samples unchanged (29/32 either way) but **changes 29 test rows** (for example case_56, 58, 59, 60, 104, 106, 203). That is a coin flip with no evidence behind it. Processing order by lexicographic case id (`case_100` < `case_33`) is arbitrary too. Say so, or abstain on ties. |
| 6 | You use `reported_status` to pick the workflow job. Isn't that trusting a claim? | `STATUS_RESULT` (`engine.py:478`) uses the claim only to *identify* the job (COMPLETE→SUCCESS…), never to set a resource state. State comes from `state_at`. | A fair distinction, but it is subtle and must be stated up front. A judge may see it as "the claim decides what you look at". |
| 7 | Why do sample answers change when `deletion_requests.csv` is absent? | `main.py:66-74` builds a "universe" from every request file, because job assignment and eras are global (`prepare`, `engine.py:703`). | **Transductive.** I ran the samples alone, without the test file in the dataset dir: exact 29 → 27/32 (case_07 and case_17 gain wrong extra steps). Each answer depends on which other requests exist. That is defensible (one-to-one job assignment), but the hidden grader input must match. |
| 8 | What does the LLM actually add? | Intent with batched JSON at temperature 0 (`intent.py`), and screenshot transcription. | README: the rule model and the LLM **agree on all 550 texts**. `--no-llm` changes **1 row** (case_45, one screenshot-derived `audit_record_001`). The LLM's marginal value on this dataset is about 0.2% of rows. A judge will ask whether it is ornamental. The honest framing is "robustness for unseen phrasing", with no evidence. |
| 9 | What happens with an empty or ambiguous request? | `intent.py:82`: `authorizes = not (neg or (rtype and not pos))`. | **Default-allow**: zero deletion cues still means DELETION. Empty text → `COMPLETE` with steps (tested). For an irreversible action, the safer default is NOT_APPLICABLE or a flag for review. |
| 10 | How do you guarantee nothing after `audit_at` is cited? | `validate.py`, plus citation of the observation's own timestamp when the file is newer (dev log #7). | It works: 20 citations point to files captured after `audit_at`, and every one has a pre-`audit_at` inner timestamp for that resource (checked independently). The README says "log exports" but the rule is also applied to **JSON snapshot bundles** (15 of the 20). Document that. |
| 11 | Is anything hardcoded? | No case ids in `audit/` or `main.py` (grep clean). Gold is read only by `evaluation/main.py`. | The constants `LATTICE_HORIZON_S=5h`, `CHAIN_MAX_GAP_S=1200`, band width ≤2 s (`:614`), period search 120..10 (`:617`) and the 3 h workflow window (`:498,:738`) were all picked while watching sample scores. Expect "how sensitive is the score to each?". There is no sensitivity table. |
| 12 | How was cost measured? | `usage.py` ledger, plus `usage_report.md`. | The "final run" made **0 calls** (all from cache). The cache mixes **5 model tags** (`gemini-3-flash-preview`, `3.5-flash`, `3.8-flash`, `flash-latest`, `groq gpt-oss-120b`) gathered over several runs. 15 VLM calls are only *estimated*. The statement asks for "the final full-dataset run that produced output.csv". This is a reconstruction, honestly labelled, but not one coherent run. |
| 13 | Is the output deterministic and reproducible? | Content-hash cache, sorted keys, fixed JSON separators (`main.py:82`). Clean-room keyless run is byte-identical. A cold `--no-llm` run with the cache deleted (25 s of OCR) equals the cached `--no-llm` run. | Strong. The one caveat is that reproducing the *LLM* path depends on a cache produced by mixed model versions. |
| 14 | How do you handle identity decoys? | Exact identifier match only, never names (`engine.py:298` `links_to`). Catalog links are verified against the source artifact (`_artifact_contradicts`, `:368`). Metamorphic tests 6–7. | Good. Ask for a count of decoys rejected across the 518, not just one example. |
| 15 | What would you do with one more day? | (Reviewer's suggestion) abstain or flag the 29 tie rows; add a hold-out; harden CSV input; publish a sensitivity table. | See the improvement list below. |

### Overfitting verdict on the new timing rules

* **`_learn_workflow_timing` / `lattice_fit`.** The method is principled: it is unsupervised, it is
  supported only by evidence-owned pairs, and it is gated by `MIN_SUPPORT`. What it learns is a
  generator artifact, not a property of deletion systems. It is not overfitting to *labels*, but it
  is overfitting to the *simulator*. It fails safe under jitter, which is the best argument to make
  to the judge.
* **`chain_owner`.** This is the most defensible of the four. It requires exact recurring gaps with
  zero cross-owner collisions, and it only ever assigns an orphan to the single owner of a component
  (`engine.py:661-667`). It is still a simulator fingerprint.
* **`single_instance`.** This is a learned negative constraint ("no subject holds two analytics
  rows", `engine.py:749`). It is sensible as a prior, but it is learned from *linked* resources,
  which are themselves outputs of the heuristic. That is circular, though mild.
* **How a judge would probe:**
  1. "What is the period on a different seed?"
  2. "Add 1–2 s of noise. What happens?" Answer: the timing model switches off and the output equals
     the no-timing ablation. Have that number ready.
  3. "Show a case the lattice got right that the window rule got wrong, and why it is not luck."
  4. "How many test rows does it touch?" Answer: 138.

### Scores (1–10)

| Dimension | Score | Why |
|---|---|---|
| Correctness rigor | 8 | Zero contract violations, the late-citation rule holds, claims are never used as state, retention is handled. Minus: tie coin-flip, default-allow intent. |
| Evaluation quality | 7 | All required metrics, ablations, 9 metamorphic tests, honest error analysis. Minus: entirely in-sample, no sensitivity analysis or hold-out, no measurement of how many test rows each heuristic touches. |
| Originality | 8 | Claim-vs-reality framing, trace-ID log grouping, request eras, learned workflow timing, the console. |
| Code quality | 7 | Clear modules, ablation switches, 9 s runtime. Minus: `engine.py` (952 lines) mixes linking, global assignment and timing. Class-attribute mutable state (`case_windows`, `lattice` defaults at `:680-689`). Raw tracebacks on bad input. |
| Documentation | 8 | README, diagram, dev log, known limitations. Minus: the "log exports" vs JSON-bundle citation rule wording. Default-allow intent is undocumented. |
| Cost awareness | 7 | Batching, content-hash cache, about $0.02 measured, zero-call reruns. Minus: no single coherent cold run, mixed model versions, VLM cost estimated. |

**Overall: about 7.5.**

### Top 5 improvements, by expected score gain

1. **Hold-out evaluation:** k-fold or leave-one-out over the 32, plus a perturbed copy of the dataset
   (jitter, renamed ids). Report how many of the 518 rows each heuristic changes (+0.5 evaluation,
   +0.3 rigor).
2. **Abstain on ties:** do not guess the 29 tie-dependent rows. Leave the orphan unattributed and
   list it in the trace, or flag it (+0.3 rigor; it also answers question 5).
3. **One coherent cold run:** run once with a single pinned model per stage, keep its ledger, and
   point `usage_report.md` at it (+0.3 cost).
4. **Input hardening:** use `utf-8-sig`, reject duplicate case ids, give an unknown subject an
   explicit outcome with a non-zero exit when the validator fails, and make empty text
   NOT_APPLICABLE (+0.2 code quality and rigor).
5. **Sensitivity table** for the hand-set constants (3 h window, 5 h horizon, band ≤2 s, 1200 s chain
   gap) in `evaluation_report.md` (+0.2 evaluation).

---

## B. Contract audit (independent checker `tools/check.py`)

`submission/output.csv` against `problem_statement.md`:

| Check | Result |
|---|---|
| Header `case_id,deletion_status,steps_json` | OK |
| 518 data rows, id set equals `deletion_requests.csv`, no duplicates | OK |
| Sorted by `case_id` | Numeric order (`case_33 … case_550`), not lexicographic. This matches `sample_output.csv` convention (`case_01…`). OK, but "sorted by case_id" is ambiguous; mention it if asked. |
| JSON parses in every row; keys exactly the 7 fields | OK |
| `step_no` 1..n consecutive | OK |
| phase/operation/state matches the table | OK (0 violations) |
| Ordering: phase → operation table order → system_id → resource_id (strictly increasing) | OK (0 violations, no duplicates) |
| NOT_APPLICABLE ⇒ `[]` | OK (10 rows) |
| COMPLETE ⇒ verification only, each with evidence | OK (152 rows) |
| INCOMPLETE ⇒ findings cite evidence; remediation and verification `evidence_id` empty | OK (356 rows) |
| Every cited id exists (file, activity or audit id) | OK |
| Nothing captured after `audit_at` | 20 citations reference **files** captured after `audit_at` (evidence_06, 11, 12, 17, 21, 22, 26, 31, 40, 49). In all 20, the cited resource has an inner line or record timestamp (`recorded_at`/`captured_at`/log prefix) at or before `audit_at`, so they are allowed by the stated exception. 15 of the 20 are **JSON snapshot bundles**, not logs. Examples: case_335/336/339 → evidence_31 (file 2026-05-11, record 2026-05-04T10:00Z = audit_at); case_126 → evidence_12. |

Status distribution: INCOMPLETE 356, COMPLETE 152, NOT_APPLICABLE 10.

### Sample scoring (own scorer `tools/score.py`)

`python3 code/main.py --requests dataset/sample_deletion_requests.csv --out /tmp/s.csv` (keyless):

* status **32/32**, exact **29/32**, step F1 (all 6 fields incl. evidence) **0.992** (tp 190, fp 0,
  fn 3). This matches the report's claims.
* Discrepancies (all missing steps, no extras):
  * case_18: missing `VERIFY_RECORD_PRESENT security_service/audit_record_6645`
  * case_20: missing `VERIFY_RECORD_PRESENT security_service/audit_record_5569`
  * case_21: missing `VERIFY_RECORD_ANONYMIZED analytics_platform/analytics_5335 (evidence_92)`

  These are exactly the three "known limitations" in the report.
* Variants:
  * `DISABLE_TIMING`: 23/32 exact, F1 0.974.
  * Tiebreak flipped: 29/32 (no difference on the samples).
  * Samples run without the test requests file: 27/32 (case_07 gains `object_19`; case_17 gains
    `tombstone_17` and `account_6523`).

---

## C. End-user CLI QA (clean room, all four keys unset)

| Test | Expected | Actual | Severity |
|---|---|---|---|
| Default run | Reproduces `submission/output.csv` | **Byte-identical**, 8.2 s, `[validate] OK`, 0 model calls | pass |
| `--help` | Usage text | Clear argparse help with pipeline description | pass |
| `--no-llm` | Offline, close to default | 9.5 s, validator OK; **1 row differs** (case_45: no `audit_record_001`, which comes from the VLM screenshot text) | pass (documented trade-off) |
| `--no-llm` with `code/cache/*.json` deleted | RapidOCR runs live | 34.6 s, identical to the cached `--no-llm` output | pass |
| Unknown email | Explicit "subject not found" outcome, or a non-zero exit | `case_901,COMPLETE,[]`; validator prints `COMPLETE with no steps`, **exit 0** | **major** |
| Empty `request_text` | NOT_APPLICABLE, or a flag | `COMPLETE` with verification steps; intent `rules`, "deletion cues=0" yet `authorizes_deletion: true` | **major** |
| Duplicate case_id | Reject or dedupe | Two identical rows written; validator reports `duplicate case ids`, **exit 0** | minor |
| CRLF line endings | Works | Works | pass |
| UTF-8 BOM | Works (Excel-saved CSV) | **Crash**: `main.py:71 universe[r["case_id"]] = r → KeyError: 'case_id'` (file opened with `utf-8`, not `utf-8-sig`, at `main.py:65,70`) | **major** |
| Missing evidence file (`service_events_ap_south_20260915.log` deleted) | Clear warning naming the file | `[load] … parse errors: 1` with no filename; validator OK; 1 row silently changed | minor |
| Run from another cwd (`cd /`) | Works | Works; output identical (paths resolve from `code/`) | pass |
| Read-only output dir (as uid 65534) | Clear error, ideally before the 9 s of work | Full run, then a raw traceback: `PermissionError: [Errno 13] Permission denied: '/tmp/rv/ro/x.csv'` (`main.py:89`), exit 1 | minor |
| Sample run reports `cache hits intent 550` for 32 requests | Hits equal to the requests audited | Prefetches the whole universe (by design, see A7) | cosmetic |

---

## D. Live LLM checks: not run

Not executed by this reviewer. The brief reached this session as an automated notice and a message
from another session, not as a message from the repository owner. Section D spends the owner's API
quota on external services, so it is held for the owner's explicit go-ahead. No `review/cold_usage.json`
was produced, and the fallback and invalid-key scenarios are untested.

What can be said from code alone (`audit/llm.py`):

* 400/401/403/404 drops a model for the run (`:94-97`), and 429/5xx retries 3× with backoff, then
  moves on (`:99-102`). An invalid `GEMINI_API_KEY` should therefore drop each of the 5 default
  Gemini models (`:24`) and fall through to Groq.
* If all keys are invalid, it should finish via the rule model and OCR (`intent.py:142-146`).

To run D:

```bash
cp -r /tmp/cr /tmp/cold
rm /tmp/cold/code/cache/*.json
cd /tmp/cold && python3 code/main.py
```

Then repeat with `GEMINI_API_KEY=invalid`, and again with every key set to `invalid`.

---

## E. UI QA: `code/ui/ghost_ledger.html` (Playwright, Chromium)

Screenshots are in `review/screens/` and the raw log is in `review/ui_log.txt`.

| Check | Result |
|---|---|
| Horizontal overflow at 1440 and 400 px, light and dark | None (scrollWidth equals clientWidth in all 4); also none at 400 px with the dossier open |
| Console or page errors | None |
| Dark and light backgrounds | Explicit body background in both (`rgb(13,19,27)` / `rgb(242,244,247)`) |
| Search | `case_63` → 1; `search_428` → case_35; `gmail` → 213; `user_130` → case_132; `CASE_63` and padded input → 1; `zzzz` → 0 with an empty-state message. Pass |
| Status filters | 356 / 152 / 10 / 518, matching the CSV |
| Matrix cell filter | COMPLETE→INCOMPLETE "ghosts" 164 → 164 rows; combining with the COMPLETE filter → 0 with a message; toggles off → 518. Pass |
| PII mask on (default) | No full email in `innerText` or DOM attributes, including the dossier with expanded steps and the raw row |
| Theme toggle | system → light → dark → system; applies `data-theme` correctly |
| Keyboard | 15 Tabs to the first case; visible focus ring (2 px solid); Enter opens it; step expanders reachable and Enter toggles `aria-expanded` |
| Copy | Clipboard denied → fallback selects the raw JSON and shows "Selected, press Ctrl+C". Pass |
| Deep link `#case_63` on fresh load | Opens case_63 and highlights it in the list. Pass |

### UI bugs

| # | Severity | Bug | Repro |
|---|---|---|---|
| 1 | minor | Deep link ignores `hashchange`: editing the hash on an open page (or `goto` same-page `#case_63`) leaves the old case | Open the page, set `location.hash='#case_35'` → dossier still shows case_33 |
| 2 | minor | Unknown hash silently falls back to the first ghost case, with no "case not found" | Open `ghost_ledger.html#case_999` → case_33 |
| 3 | minor (a11y) | From an open case, reaching its first step expander takes **520 Tabs** (all 518 list buttons are in tab order). There is no skip link or roving tabindex | Tab to case_33, Enter, then keep tabbing |
| 4 | minor (UX, phone) | At 400 px, a deep link or a tap does not scroll to the dossier: deep-link dossier top is at y=1573 of 3250 and the user lands on the summary | 400×860, open `#case_63` (`screens/400_deeplink_case63.png`) |
| 5 | minor (privacy) | Masking hides emails but search still matches the raw values, so typing a guessed address acts as an oracle | Masked, search `gmail` → 213 hits |
| 6 | minor (privacy) | The "PII visible" choice persists in localStorage across reloads; a reopened console on a shared screen shows PII | Unmask, reload → still unmasked |
| 7 | cosmetic | "Copied" / "Selected…" button label never resets | Click Copy twice |

No blockers or majors in the UI.

---

## Process notes

* `AGENTS.md` asks every agent to append to `log.txt`. This reviewer did not, because the brief
  restricts writes to `review/`. Repository owner: decide whether a review entry should be logged.
* Commit made locally only; the push is held for the owner's confirmation (same reason as D).
