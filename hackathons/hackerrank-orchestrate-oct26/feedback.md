# Judges' feedback: HackerRank Orchestrate (Ghost Ledger)

Received by Jannet by email and shared on 2026-11-08. The email calls it the "September Edition", but our entry was the edition that started Oct 24 (score 75.9/100, #93 on the live board, not placed). It's kept verbatim below. The lessons drawn from it are in [../lessons.md](../lessons.md).

> Thanks for taking part and submitting your build. We have reviewed your work across a few areas, and here is how to make your next submission even stronger.
>
> The decisions and action sequences in your output CSV were largely correct. The next priority is directing the AI tool before implementation: define the evidence flow, decision responsibilities, and unresolved policy questions upfront, and capture the full exchange as it happens so your reasoning and verification remain visible.
>
> **Judge Interview**
> Specific explanations of timing attribution, fallback behavior, and model substitution made your interview grounded and demonstrated personal understanding beyond the AI-generated implementation. For future answers, practise stating what is implemented versus proposed before giving a concrete example, especially for monitoring and review queues. Prepare to explain why ambiguous job assignments should be accepted or escalated, including what evidence supports the tiebreak. Rehearse an end-to-end retention walkthrough showing which records must remain and which identifiers must be removed; that would make the policy reasoning as tangible as the timing explanation.
>
> **Chat Transcript**
> Upfront direction of the AI tool needs substantial improvement: the initial instructions left the core architecture for the tool to choose. Before requesting implementation, describe how request interpretation, identity matching, evidence reconstruction, and policy decisions should connect, and assign responsibilities between model judgment and fixed rules. Turn product ambitions such as a distinctive interface into concrete acceptance conditions before expanding the build. Explicitly settle historical identity matching, remediation order, and retention responsibilities rather than leaving those decisions implicit. The incomplete record in your chat transcript limited what could be assessed; next time, capture a genuine logged back-and-forth as it happens, including your real prompts and the tool's real responses throughout.
>
> **Code Zip**
> Completion decisions in your submitted code need to depend on evidence coverage: unreadable files and unknown resource states should prevent a claim that deletion is complete. Make retention rules executable, requiring proof that mandatory records remain and prohibited identifiers are removed before producing a plan. Enforce required fields and allowed values on model responses, and handle damaged caches and malformed values without breaking the run; align the documented recovery promises with those implemented paths. To measure whether AI adds useful judgment, compare the model-assisted and rules-only paths on the provided data, checking correctness alongside how often missing-evidence and retention cases are handled safely.
>
> **Output CSV**
> Deletion decisions and many action sequences in your output CSV were largely correct. The most useful refinement is a policy-driven verification pass before each plan is emitted: require explicit checks that retained security audit records remain present, and include the necessary analytics and legal-hold verifications. In that same pass, confirm that account identifiers and evidence references agree with the plan, and that support records requiring deletion are not merely redacted. This would make the proposed actions and their supporting evidence more consistently aligned.
>
> Thank you for participating in the September Edition. The next Orchestrate is here. Take this feedback into the next one.

## Scores, for reference

Interview 26.4/30 · output 28.2/30 · code 18.3/30 · chat transcript 3.0/10. The transcript and the code lost the most points, and the feedback says why: the architecture was left to the tool, the transcript was curated, not raw, and "complete" didn't depend on evidence coverage.

## Next edition

**Orchestrate Holiday Edition** starts **Dec 12, 18:00 IST** (24 h), followed by the AI judge interview; live evaluation Dec 14–15, results Dec 15. Same prizes: $1,200 for 1st, $300 each for 2nd–5th. Listed in [../november-2026.md](../november-2026.md).
