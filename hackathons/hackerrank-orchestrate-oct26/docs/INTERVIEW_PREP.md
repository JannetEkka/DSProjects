# Interview prep - Ghost Ledger deletion-audit agent

Rehearsal notes for the 30-minute AI interview. Answers are written to be spoken: short, specific,
with a file or a number in each one. Every number below comes from
`code/evaluation/evaluation_report.md`, `code/evaluation/usage_report.md`, `review/REVIEW.md` or a
run of `python3 code/main.py` (checked on 24 Oct 2026 after the final review fixes). The engine is
split into `audit/identity.py`, `semantics.py`, `linking.py`, `workflow.py` and `planner.py`, with
`engine.py` as a thin facade and the constants in `config.py`.

---

## 60-second pitch

"Northstar's dashboards say deletions are Complete. Our agent checks whether that's true. For each
of the 518 requests it first decides whether the person actually asked for deletion, using an LLM
with a rule model as a cross-check. Then it resolves every email, phone and hash the person ever
had, turns 94 evidence files (SQL dumps, JSON, six log dialects, text, PDFs, screenshots) into time-stamped observations, works out each record's state at the audit time, and
applies the deletion policy. The output is COMPLETE, INCOMPLETE or NOT_APPLICABLE with an ordered,
evidence-cited plan. We never trust the workflow's own status. Claims only help find the right job,
never decide a state. On the 32 public samples we get 100% status accuracy and 99.2% step F1. Every
row passes a contract validator, the full run takes about 9 seconds, and it costs well under ten
cents in model calls because everything after intent is deterministic Python. There's also an
offline console that shows claim versus reality for every case."

## 2-minute architecture walkthrough (script)

1. **Entry point.** "`code/main.py` loads the requests, runs the pipeline, writes `output.csv`,
   a per-case `output.trace.jsonl` and `output.usage.json`, then runs the validator. It exits 1 if
   the validator finds any problem."
2. **Intent** (`audit/intent.py`). "Distinct request texts go to Gemini Flash in batches of 10,
   JSON mode, temperature 0, through a model chain that falls back to Groq. A negation-aware
   multilingual rule model votes on every text and disagreements go into the trace. Empty text is
   NOT_APPLICABLE without a model call."
3. **Identity** (`IdentityResolver`). "The request email can be current or historical. We collect
   every email, phone and email hash ever held by the stable user_id from `user_identities.csv`
   and `user_audit_log.csv`. We never link on names, because customers share names."
4. **Evidence** (`audit/evidence.py`, `EvidenceStore`). "Each file becomes `Observation` objects:
   SQL runs in in-memory SQLite with replicas kept separate, six log dialects are parsed and
   grouped by trace_id, PDFs go through pdfplumber, screenshots through Gemini vision or RapidOCR.
   2,932 observations, zero parse errors."
5. **Linking** (`_linked_resources`, `links_to`). "A record belongs to the subject if it carries an
   exact identifier, if a catalog link names them and the source artifact doesn't contradict it, if
   an active connector or restore job repopulated their record, or if this request's own deletion
   workflow processed it. That last rule is how we find scrubbed records with no identifier left.
   Workflow timing (chains and a 30-second lattice) separates requests that report in the same
   minute."
6. **State and policy** (`state_at`, `audit`). "Latest observation at or before audit_at wins.
   `deletion_rules.csv` gives DELETE, REDACT, ANONYMIZE or RETAIN per category. Steps are ordered:
   stop flows and restores first, then fix records, then verify; inside a phase, the operation
   order from the problem statement, then system_id, then resource_id."
7. **Validator** (`audit/validate.py`). "Checks header, row count, sort, JSON, step numbering, the
   phase/operation/state table, evidence rules for COMPLETE vs INCOMPLETE, and that every cited id
   exists and was observable by audit_at."

---

## Topic 1 - Overview

**Q: What problem does this solve, in one sentence?**
A: Deletion workflows report "Complete" while copies survive in replicas, logs, exports, search
indexes and backups. The agent audits each request against the evidence and returns a verdict with
an ordered remediation and verification plan.

**Q: What are the inputs and outputs?**
A: Inputs are `deletion_requests.csv`, identity tables, `system_activity.csv`, the data catalog,
`deletion_rules.csv` and 94 evidence files. The output is `output.csv` with case_id, status and
steps_json for 518 cases (356 INCOMPLETE, 152 COMPLETE, 10 NOT_APPLICABLE), plus a trace explaining
every linked record.

**Q: How good is it?**
A: On the 32 public samples: 100% status accuracy, 99.2% step F1, 100% step precision, 98.4%
recall, 29 of 32 cases exactly right, and 98.7% evidence-citation accuracy. Those are in-sample
numbers, so I treat them as optimistic. The 19 metamorphic tests (7 of them prompt injections), the
leave-one-out timing model and the perturbed-dataset run are the out-of-sample checks.

**Q: Where is AI used and where isn't it?**
A: Two places: intent classification and screenshot transcription. Everything that decides a state,
a link or a step is deterministic Python. That keeps it reproducible, cheap and auditable, which
matters for an action like deletion.

**Q: What's the single most important design decision?**
A: Treating every reported status and activity result as a claim, never as state. We use the
workflow claim only to pick out which job belongs to this request. The record's state always comes
from an observation in the evidence.

**Q: How long does it take and what does it cost?**
A: About 9 seconds for the full 518-case run. The recorded ledger is 30 model calls, 42,662 tokens,
about $0.019. With the 15 untracked vision calls estimated, the whole build is under $0.10. A
re-run makes zero calls because answers are cached by content hash.

## Topic 2 - Information retrieval and agent architecture

**Q: How do you find all of a person's data when the email in the request may be old?**
A: `IdentityResolver` maps the email to the stable user_id, then pulls every email, phone and email
hash that user ever had from `user_identities.csv` and `user_audit_log.csv`. Metamorphic test 1
checks that a historical email resolves to the same subject.

**Q: How do you find a record that was scrubbed and has no identifier left?**
A: Through the request's own deletion workflow. Its account job runs shortly before reported_at
and its result mirrors the claim (COMPLETE→SUCCESS, PARTIALLY_COMPLETE→PARTIAL,
NOT_STARTED→FAILED). Records that job processed are attributed to the request. Removing that rule
drops exact cases from 90.6% to 53.1% and step F1 from 99.2% to 91.2%.

**Q: How do you avoid linking someone else's data?**
A: Exact identifier match only, never names or near-misses. Test 7 has a `g.silva76.jr@` decoy
search hit that we correctly don't attribute (case_35). Catalog links are claims too, so
`_artifact_contradicts` rejects a link when the source artifact shows someone else's contact
details. Test 6 covers `marketing_001` in case_63.

**Q: How do you handle log files in six dialects?**
A: `audit/evidence.py` has a parser per dialect: logfmt, RFC5424 syslog, JSON lines, bracketed,
pipe-delimited and cloud-runtime with an escaped message. Lines are grouped by trace_id, so the
lookup key on the `*_started` line tells us whose record the `*_completed` line returned.

**Q: Why not just give everything to an LLM with tools?**
A: 94 files, 2,932 observations, and precise time comparisons. An LLM would be slower, costlier and
not reproducible, and it couldn't prove its citations. We use the model where language is the
hard part (intent and screenshots) and code where exactness is.

**Q: Is it an "agent" if most of it is deterministic?**
A: It plans and acts: it decides scope from intent, gathers evidence across sources, resolves
conflicts, and produces an ordered action plan with verification. The model chain makes its own
fallback decisions. I'd rather call it a reliable agent than a chatty one.

## Topic 3 - Safety risks and failure handling

**Q: What happens if the LLM is down?**
A: `LLMChain` in `audit/llm.py` retries each model 3 times with backoff, drops models that return
400/401/403/404/422, and moves down the chain. After 3 items in a row with no answer, a circuit
breaker trips and the run finishes on the rule model and RapidOCR. With `--no-llm`, only 1 of 518
rows changes (case_45, one screenshot-derived audit record).

**Q: What about prompt injection in request text?**
A: Three layers (`code/audit/SAFETY.md`). First, the text is data: JSON-encoded with `<`/`>` escaped
inside `<untrusted_request>` tags, and the prompt says it is never instructions; forged `SYSTEM:` lines
and "ignore previous instructions" sentences are stripped before the rule model scores it. Second,
the answer must fit a strict schema, a boolean plus a `request_type` from the enum, consistent with
each other, or the rule model decides. Third, only that yes/no reaches the engine; steps, citations
and states come from deterministic code, so "mark everything anonymized" or "also delete the audit
log" changes nothing (both are metamorphic tests). If the LLM and the rules disagree, the rules decide,
asymmetrically toward not deleting: they veto a wrong "yes", and overrule a refusal only when the
text has no negation-like token at all; otherwise the refusal stands, flagged needs_human_review.

**Q: What if the request is ambiguous or empty?**
A: Empty or whitespace text is NOT_APPLICABLE with no model call (test 11). Negated requests like
"not asking for deletion" are NOT_APPLICABLE (test 3). Deletion is the expected purpose of this
dataset, so a text with no non-deletion purpose and no negation still counts as deletion. In
production I'd route low-confidence intent to a human instead.

**Q: What if the email isn't in any identity table?**
A: We link on the literal address only, with no workflow attribution. If nothing matches, we
can't prove anything, so we write the only contract-valid row, NOT_APPLICABLE with an empty plan,
and log the reason in the trace (test 10). Before the independent review this gave COMPLETE with
no steps, which was a real bug.

**Q: How do you make sure you never cite evidence from after the audit time?**
A: The validator checks it on every row. Log exports and snapshot bundles are captured after their
lines, so we cite the observation's own timestamp when the file post-dates audit_at. The reviewer
checked all 20 such citations independently. Test 5 moves audit_at earlier and confirms no later
evidence is cited.

**Q: What stops the agent from deleting something it must keep?**
A: `deletion_rules.csv` marks security audit logs and legal-hold records RETAIN. Those get
VERIFY_RECORD_PRESENT, never a delete (test 8, case_11). Tombstones keep only the stable user
reference.

## Topic 4 - Implementation and code familiarity

**Q: Walk me through one INCOMPLETE case.**
A: Open the console at `#case_35`. Intent: deletion. Identity: the subject's emails and hashes.
Linking finds `account_013` and `search_428` and rejects the similar-email decoy. `state_at` shows
the search record still present at audit_at, so the plan reports it (citing `evidence_09`), deletes
it, then verifies both the account and the search record absent. Remediation and verification are
future steps, so their evidence_id is empty, as the contract requires. The trace line for case_35 has every link reason.

**Q: How does the workflow timing model work?**
A: `_learn_workflow_timing` learns only from activities that evidence ties to exactly one owner.
Two regularities: a request's policy actions are chained by exact gaps (390 s and 449 s, never seen
between two different owners), and every workflow event sits at a fixed phase after its account job
modulo a 30-second period (328 of 328 owned pairs fit). `chain_owner` gives an orphan record to the
single owner of its chain; `lattice_fit` keeps only account jobs and orphans in phase with the
subject's own events.

**Q: What's MIN_SUPPORT?**
A: A regularity needs at least 10 evidence-owned observations before we use it
(`MIN_SUPPORT = 10`). Chain gaps must also be sharp. Under ±2 s jitter nothing is learned and the
output is identical to the timing-off ablation.

**Q: How do you handle two requests competing for the same workflow job?**
A: Global one-to-one assignment: forced choices first, then the earliest job per request
(`TIEBREAK_EARLIEST = True`). Flipping that to latest changes 29 of 518 rows while the samples
score the same either way, so those rows are the least certain part of the output, and the report
says so.

**Q: What are request eras?**
A: When one subject has two requests months apart, evidence older than the previous request's
audit_at belongs to that request. Without eras, exact cases drop from 90.6% to 84.4%.

**Q: How is the output ordered?**
A: Flows and restores are stopped first so data isn't recreated, then records fixed, then checks.
Inside a phase: the operation order from the problem statement, then system_id, then resource_id.
The reviewer's checker found 0 ordering violations.

## Topic 5 - Testing and evaluation

**Q: How did you evaluate?**
A: `code/evaluation/main.py` scores the 32 samples on status, steps, fields, sequence and
citations, runs 19 metamorphic tests and 108 unit tests, runs ablations, a leave-one-out timing
model, a perturbed-dataset run, and a sensitivity table (tie-break flip, timing off, ±2 s jitter, and
every hand-set bound moved both ways). It's deterministic from the cache, so anyone can reproduce it without a
key.

**Q: Your metrics are in-sample. Why should I trust 99.2%?**
A: You shouldn't treat it as a hold-out score, and the report says so in section 5. Two things
help: the metamorphic tests check invariants on derived cases the gold never covered, and the
development log shows each fix with its root cause, going from 3 to 29 exact cases. Two hold-out
checks now exist: leave-one-out over the 32 re-learns an identical timing model in 32/32 folds, and a
copy of the dataset with every id renamed and every timestamp shifted reproduces 518/518 rows. I'd be
clear that these test parameter stability, not my design choices, which were made watching samples.

**Q: Isn't the 30-second lattice just overfitting to the data generator?**
A: It's fitted to the simulator, not to labels. It's learned without gold, only from records the
evidence already ties to one owner, and gated by MIN_SUPPORT. Real deletion workers won't sit on a
30-second lattice. What matters is that it fails safe: when the regularity isn't there, as with
±2 s jitter, it switches itself off and we fall back to the window rule. The same idea in
production would learn whatever scheduler fingerprint the real system has, or nothing.

**Q: Why is a learned "generator fingerprint" legitimate and not hardcoding?**
A: Hardcoding would be case ids, answers or constants read off the gold. There are no case ids in
the prediction code; the gold is read only by the evaluation script. The period and gaps are
estimated from the evidence on every run, so different data gives different parameters, or none.
The hand-set parts are search bounds, and the report has a sensitivity table for them: a 2.5, 4 or
6 h window, MIN_SUPPORT 5, and a 600 or 2,400 s chain cap change 0 of 518 rows; MIN_SUPPORT 20 changes
2. The one knife-edge is the lattice band: 1 s changes 113 rows (samples drop to 26/32), because the
observed band is 3 s wide; 2 s is the smallest band that learns it, chosen from the data.

**Q: How much of the hidden-set answer depends on that timing model?**
A: Switching it off changes 138 of 518 rows; on the samples it's the difference between 71.9% and
90.6% exact. That's a big share, which is exactly why we made it refuse to learn from blurred
timing instead of guessing.

**Q: What are the three remaining sample mismatches?**
A: case_21 misses `analytics_5335` because it's in phase with two requests' account jobs and we
won't guess. case_18 and case_20 each miss one audit record that appears in no participant-visible
file, so nothing can derive it. The organizers said those two don't affect the score: source is
the organizers' reply in the official Discord #hacker-help-desk on 24 Oct 2026 ("you can ignore sample case 18 & 20 ... scoring is on deletion_requests").

## Topic 6 - Production monitoring

**Q: If this ran daily, what would you watch?**
A: Validator failures first, because they block publishing. Then cost and calls per request, cache
hit rate, LLM-versus-rules intent disagreement, and the share of rows that depend on timing or
tie-break links. The README's "Production monitoring" section has the full table with thresholds.

**Q: What would tell you the data changed under you?**
A: The learned timing parameters. If the period or a chain gap shifts, or support drops near
MIN_SUPPORT, the attribution assumptions changed. Also evidence parse errors by format, and the
COMPLETE/INCOMPLETE mix moving more than 10 points day over day.

**Q: What fails first with real, messy production data?**
A: The timing fingerprint, which would most likely not be learned at all, so we'd fall back to
window uniqueness and leave more scrubbed records unattributed. That's the safe failure: more
"can't prove it" and fewer wrong links. Next would be new log dialects and screenshot layouts,
which show up as parse errors and missing identifiers.

**Q: How would you measure accuracy in production with no gold?**
A: A weekly shadow sample of rows checked by hand, stratified by link type so timing and tie-break
rows are over-sampled, plus every intent disagreement in a review queue.

**Q: How would you alert on cost?**
A: `output.usage.json` already records calls, tokens and cost per run. Alert if cost per request
goes above 3x baseline (about $0.00004 today), or if a warm re-run makes any call, which means the
cache key or prompt drifted.

## Topic 7 - What makes the approach different

**Q: What's different from a typical LLM agent?**
A: The LLM is used only where language is hard, and everything with legal weight is deterministic
and cited. The output is byte-for-byte reproducible without a key.

**Q: What's the most original part?**
A: Finding scrubbed records through the request's own workflow, then separating requests that
report in the same minute with learned timing that turns itself off when the signal isn't real.
Also trace-ID grouping for logs and request eras for repeat subjects.

**Q: Why the console?**
A: An auditor needs to see why. `code/ui/ghost_ledger.html` is one offline file: the
claim-vs-reality matrix (164 cases reported COMPLETE but actually INCOMPLETE), findings by
system, and a dossier per case where every step expands to its evidence, linkage and policy rule.
PII is masked on every load.

**Q: How did you use AI to build it?**
A: Several Claude Code sessions with separate jobs: build, helper runs to fill the LLM caches, an
accuracy pass, and an independent reviewer with a read-only brief that mock-interviewed the
design and audited the contract. Every change had to pass the validator, the evaluation suite and
a byte-identical clean-room run before it was pushed.

**Q: What would you do with another week?**
A: Turn the 14 low-confidence tie-break decisions into abstentions or human review once a reviewer
queue exists. Ship one coherent cold run with a single pinned model per stage once a quota allows it
(the attempt is recorded in the usage report). Widen the multilingual negation list with native
speakers, and replace the simulator-specific timing model with whatever scheduler fingerprint a real
deletion system has.

**Q: Why don't you guess ambiguous attributions?**
A: When an orphan record fits two requests equally, a guess that's wrong costs two errors: a missed
step in the right case and a wrong step in the other. Abstaining costs at most one. So we abstain, and
we don't hide it: both candidate cases carry a `needs_review` entry naming the record and the other
candidate, and the console shows a needs-review chip, so a human resolves it in seconds. On this run
that's 14 records across 28 cases.

**Q: Is this really an agent, or a rules engine?**
A: It's a deterministic agent with LLMs at the two judgment points: reading what the customer asked
for, and reading screenshots. Everything else, identity resolution, linking, state reconstruction,
policy and ordering, is code that plans and verifies over the evidence on its own. We chose that split
on purpose: every step is auditable back to a file or activity id, a re-run is byte-identical, and
the whole 518-case run costs about two cents of model calls. The LLM's answers are checked against a
schema and a rule model, so a model error can't turn into a wrong deletion silently.

---

## Limitations I'd own

* **In-sample metrics.** All headline numbers are on the 32 cases that guided development. The
  leave-one-out and perturbation checks test parameter stability, not the design choices.
* **Simulator fingerprint.** The 30 s lattice and the 390/449 s chain gaps describe the data
  generator, not real deletion systems. They fail safe (±2 s jitter turns them off) but would not
  transfer as-is.
* **Tie-dependent rows.** 29 of 518 rows change if the account-job tie-break flips; the samples
  can't tell the difference.
* **Timing-dependent rows.** 138 of 518 rows change with the timing model off.
* **Underivable sample records.** `audit_record_6645` (case_18) and `audit_record_5569` (case_20)
  are in no visible file. They do not affect the score; source: the organizers' reply in the official Discord #hacker-help-desk on 24 Oct 2026 ("you can ignore sample case 18 & 20 ... scoring is on deletion_requests").
* **Transductive.** Job assignment and eras are global, so an answer depends on which other
  requests are in the run. Running the samples alone gives 27/32 exact instead of 29/32
  (reviewer's measurement).
* **LLM adds little here.** LLM and rules agree on all 550 texts; `--no-llm` changes 1 row. The
  value is robustness to unseen phrasing, which this dataset doesn't test.
* **Cost report is a reconstruction.** The cache was filled over several runs with five model
  tags; 15 vision calls are estimated, not measured.
* **Hand-set bounds** were chosen while watching sample scores. The sensitivity table shows they
  are flat except the lattice band width (1 s → 113 rows changed).
* **Ambiguous records.** 14 orphan records fit two requests equally; they are not attributed and each
  of the 28 candidate cases carries a `needs_review` entry.
* **Negation coverage.** The rule model knows negation forms in 15 languages; an unlisted form plus an
  LLM error is the one remaining path to a wrong deletion (SAFETY.md residual risks).

## Numbers to remember

| What | Number |
|---|---|
| Requests in the test run | 518 (356 INCOMPLETE, 152 COMPLETE, 10 NOT_APPLICABLE) |
| Evidence | 94 files → 2,932 observations, 0 parse errors |
| Public samples | 32 |
| Status accuracy | 100% |
| Step F1 / precision / recall | 99.2% / 100% / 98.4% |
| Exact cases | 29/32 (90.6%) |
| Sequence accuracy | 100% |
| Citation accuracy | 98.7% |
| Metamorphic tests / unit tests | 19/19 pass / 108 pass |
| Hold-out checks | LOO timing model identical 32/32; perturbed dataset 518/518 identical |
| Needs review (abstentions) | 14 records, 28 candidate cases |
| Dev progression (exact) | 3 → 16 → 19 → 20 → 21 → 28 → 29 |
| Ablation: no workflow attribution | 53.1% exact, 91.2% F1 |
| Ablation: no timing model | 71.9% exact, 97.4% F1 |
| Ablation: no request eras | 84.4% exact, 97.4% F1 |
| Rows changed: timing off / tie-break flip | 138 / 29 of 518 |
| Lattice | 30 s period, 328/328 owned pairs fit |
| Chain gaps | 390 s and 449 s; 36 chains |
| MIN_SUPPORT | 10 |
| Request texts / LLM-rule agreement | 550 / all agree |
| `--no-llm` rows changed | 1 (case_45) |
| Runtime | about 9 s (was 27 s before the inverted index) |
| Ledger | 30 calls, 42,662 tokens, $0.0193; under $0.10 total with estimates |
| Warm re-run | 0 calls; cache hits 550 intent + 11 media |
| Ghost cases (claimed COMPLETE, actually INCOMPLETE) | 164 |
| LLM chain | 3 retries/model, backoff 2 s → 4 s, 90 s timeout, breaker after 3 strikes |
