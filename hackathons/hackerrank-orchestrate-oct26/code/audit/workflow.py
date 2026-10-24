"""Workflow attribution: which records *this request's* deletion workflow processed.

A scrubbed record carries no identifier, so only the workflow's own activity ties it to a request:
the account job before `reported_at` (one-to-one across all requests), the learned timing model
(policy-action chains and the 30 s lattice anchored at the account job), and per-subject eras."""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from . import config
from .evidence import RESOURCE_RE, resource_prefix
from .identity import Identity


class WorkflowMixin:
    """Expects `activities`, `owners`, `ids` and `linked_resources()` on the engine."""

    STATUS_RESULT = {"COMPLETE": "SUCCESS", "PARTIALLY_COMPLETE": "PARTIAL", "NOT_STARTED": "FAILED"}

    def workflow_resources(self, case: dict, ident: Identity, linked: dict[str, list[str]],
                           window_h: float = config.WORKFLOW_WINDOW_H) -> dict[str, str]:
        """Resources processed by *this request's* deletion workflow.

        Records that were already scrubbed (404 profile, anonymized analytics row) no longer carry
        identifiers, so evidence alone cannot tie them to the subject. The deletion workflow's own
        activity can: its account job runs shortly before `reported_at`, and its outcome is what the
        workflow reported (COMPLETE<-SUCCESS, PARTIALLY_COMPLETE<-PARTIAL, NOT_STARTED<-FAILED).
        Only resources that no evidence attributes to a different person are eligible."""
        if self.DISABLE_WORKFLOW:
            return {}
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        rep = P(case["reported_at"])
        lo = max(P(case["requested_at"]), rep - timedelta(hours=window_h))
        expected = self.STATUS_RESULT.get(case["reported_status"])
        out = {}

        def eligible(rid):
            own = self.owners.get(rid, set())
            return not own or own == {ident.user_id}

        has_account = any(resource_prefix(r) == "account" for r in linked)
        acc_time = None
        if not has_account and case["case_id"] in self.assigned_accounts:
            a = self.assigned_accounts[case["case_id"]]
            if a is not None:
                out[a["resource_id"]] = a["activity_id"]
                acc_time = P(a["event_time"])
        elif not has_account:
            cands = [a for a in self.activities
                     if a["source_system"] == "deletion_worker" and a["target_system"] == "account_service"
                     and lo <= P(a["event_time"]) <= rep and a["reported_result"] == expected
                     and eligible(a["resource_id"])]
            if cands:
                a = max(cands, key=lambda a: a["event_time"])
                out[a["resource_id"]] = a["activity_id"]
                acc_time = P(a["event_time"])
        else:
            accs = [a for a in self.activities if a["resource_id"] in linked
                    and a["target_system"] == "account_service" and a["source_system"] == "deletion_worker"
                    and lo <= P(a["event_time"]) <= rep]
            if accs:
                acc_time = P(min(accs, key=lambda a: a["event_time"])["event_time"])
        if acc_time is None and not has_account and case["case_id"] in self.assigned_accounts:
            # no account job at all (the profile was never submitted): the workflow window is the
            # reporting window itself
            acc_time = lo
        if acc_time is not None and self.case_windows is not None:
            held = {resource_prefix(r) for r in linked} & self.single_instance
            for a in self.activities:
                if a["source_system"] != "deletion_worker" or a["target_system"] == "account_service":
                    continue
                t = P(a["event_time"])
                if not (acc_time <= t <= rep) or a["resource_id"] in linked or self.owners.get(a["resource_id"]):
                    continue
                # 1) chain linkage: the orphan sits at an exact chain gap from an owned policy action
                chain = self.chain_owner.get(a["activity_id"])
                if chain is not None:
                    if chain == ident.user_id:
                        out.setdefault(a["resource_id"], a["activity_id"])
                    continue
                # a subject never holds two records of a single-instance category
                if resource_prefix(a["resource_id"]) in held:
                    continue
                # 2) attribute only when no other request's workflow window could explain this activity;
                #    with a learned lattice, only workflows whose account job is in phase can explain it
                others = [cid for cid, (w0, w1) in self.case_windows.items()
                          if cid != case["case_id"] and w0 <= t <= w1
                          and self.case_subject.get(cid) != ident.user_id]
                fit = self.lattice_fit(a, acc_time)
                if fit is False:
                    continue
                if fit:
                    others = [cid for cid in others if self.lattice_fit(a, self.case_windows[cid][0])]
                if not others:
                    out.setdefault(a["resource_id"], a["activity_id"])
        return out


    @staticmethod
    def _template(a):
        return re.sub(r"\bfrom [a-z_]+", "from <S>", RESOURCE_RE.sub("<R>", a["details"]))

    def _sole_owner(self, rid):
        own = self.owners.get(rid, set())
        return next(iter(own)) if len(own) == 1 else None

    def _learn_workflow_timing(self):
        """Two timing regularities of the deletion workflow, learned from evidence-attributed activity
        only (activities whose resource evidence ties to exactly one person; no labels involved).

        * Lattice: a workflow's events sit at a fixed phase after its account job, modulo a period,
          with one phase band per event template (e.g. 'received the final result' vs 'Policy action
          completed'). The period is the largest one for which every template's same-owner phases
          collapse into a band of <= 3 s.
        * Chain: consecutive policy actions of one workflow are spaced by a few exact gaps. A gap is
          kept when it recurs for the same owner, is sharp (>= 80% of same-owner pairs within +-3 s
          fall exactly on it) and never (+-1 s) separates two different owners;
          gaps that are the sum of two kept gaps (two hops) are implied by the union below.
        Orphan activities (no owner in any evidence) that a chain connects to owned activities of a
        single person inherit that owner (`chain_owner`)."""
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
        self.lattice, self.lattice_period, self.chain_gaps, self.chain_owner = {}, None, {}, {}
        if self.DISABLE_TIMING:
            return
        dw = [a for a in self.activities if a["source_system"] == "deletion_worker"]
        jobs = [(P(a["event_time"]), self._sole_owner(a["resource_id"])) for a in dw
                if a["target_system"] == "account_service"]
        events = sorted(((P(a["event_time"]), self._template(a), self._sole_owner(a["resource_id"]), a)
                         for a in dw if a["target_system"] != "account_service"), key=lambda x: x[0])
        # --- lattice
        pairs = {}
        for tj, uj in jobs:
            if uj is None:
                continue
            for te, tpl, ue, _ in events:
                if ue == uj and 0 < te - tj <= config.LATTICE_HORIZON_S:
                    pairs.setdefault(tpl, []).append(int(te - tj))
        pairs = {k: v for k, v in pairs.items() if len(v) >= config.MIN_SUPPORT}

        def band(vals, period):
            res = sorted({v % period for v in vals})
            for start in res:  # smallest circular window holding every phase
                width = max((r - start) % period for r in res)
                if width <= config.LATTICE_MAX_BAND_S:
                    return {(start + i) % period for i in range(width + 1)}
            return None
        for period in config.LATTICE_PERIODS:
            bands = {k: band(v, period) for k, v in pairs.items()}
            if bands and all(b is not None for b in bands.values()):
                self.lattice, self.lattice_period = bands, period
                break
        # --- chain
        same, cross = {}, {}
        for i, (ti, tpl, ui, _) in enumerate(events):
            for tj, tpl2, uj, _ in events[i + 1:]:
                d = int(tj - ti)
                if d > config.CHAIN_MAX_GAP_S:
                    break
                if tpl2 != tpl or ui is None or uj is None:
                    continue
                bucket = same if ui == uj else cross
                bucket.setdefault(tpl, {}).setdefault(d, 0)
                bucket[tpl][d] += 1
        for tpl, hist in same.items():
            bad = cross.get(tpl, {})
            # a chain gap must be sharp: nearly all same-owner pairs within +-3 s of it sit exactly on it
            # (blurred timing means the workflow clock is not exact, so no chain is learned)
            gaps = sorted(g for g, n in hist.items() if n >= config.MIN_SUPPORT
                          and n >= config.CHAIN_SHARPNESS * sum(hist.get(g + e, 0) for e in range(-config.CHAIN_SHARP_WINDOW_S, config.CHAIN_SHARP_WINDOW_S + 1))
                          and not any(bad.get(g + e) for e in (-1, 0, 1)))
            gaps = [g for g in gaps if not any(abs(g - x - y) <= 1 for x in gaps for y in gaps if x <= y < g)]
            if gaps:
                self.chain_gaps[tpl] = gaps
        parent = list(range(len(events)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i, (ti, tpl, _, _) in enumerate(events):
            gaps = self.chain_gaps.get(tpl)
            if not gaps:
                continue
            for j in range(i + 1, len(events)):
                tj, tpl2 = events[j][0], events[j][1]
                if tj - ti > max(gaps) + 1:
                    break
                if tpl2 == tpl and any(abs(tj - ti - g) <= 1 for g in gaps):
                    parent[find(i)] = find(j)
        comps = {}
        for i, e in enumerate(events):
            comps.setdefault(find(i), []).append(e)
        for members in comps.values():
            owners = {u for _, _, u, _ in members if u}
            if len(members) > 1 and len(owners) == 1:
                uid = next(iter(owners))
                for _, _, u, a in members:
                    if u is None and not self.owners.get(a["resource_id"]):
                        self.chain_owner[a["activity_id"]] = uid

    def lattice_fit(self, a: dict, job_time) -> bool | None:
        """None if no lattice is known for this activity's template, else whether the activity is in
        phase with a workflow whose account job ran at `job_time`."""
        band = self.lattice.get(self._template(a))
        if band is None or job_time is None:
            return None
        t = datetime.fromisoformat(a["event_time"].replace("Z", "+00:00")).timestamp()
        jt = job_time.timestamp() if hasattr(job_time, "timestamp") else job_time
        return 0 < t - jt <= config.LATTICE_HORIZON_S and int(t - jt) % self.lattice_period in band

    def era_start(self, case: dict, ident: Identity) -> str:
        """Audit time of the same subject's previous request: older evidence belongs to that request."""
        prev = ""
        if self.DISABLE_ERAS:
            return prev
        for c in self.all_cases:
            if c["case_id"] == case["case_id"] or c["requested_at"] >= case["requested_at"]:
                continue
            other = self.ids.resolve(c["email"])
            if other and other.user_id == ident.user_id and c["audit_at"] > prev:
                prev = c["audit_at"]
        return prev

    def prepare(self, cases: list[dict]) -> None:
        """Pre-compute every request's workflow window [account job, reported_at] (global view)."""
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        self.case_windows = None
        self.case_subject = {}
        self.all_cases = list(cases)
        self.assigned_accounts = {}
        self.single_instance = set()
        self._learn_workflow_timing()
        prefix_counts = {}
        # 1) candidate workflow account jobs per request lacking an evidence-linked account
        cand = {}
        subject = {}
        taken = set()
        alias = {}  # duplicate submissions (same subject + same workflow timing) share one workflow
        first_of = {}
        for c in cases:
            ident = self.ids.resolve(c["email"])
            if ident is None:
                continue
            wkey = (ident.user_id, c["requested_at"], c["reported_at"], c["reported_status"])
            if wkey in first_of:
                alias[c["case_id"]] = first_of[wkey]
                continue
            first_of[wkey] = c["case_id"]
            linked = self.linked_resources(ident, c["audit_at"], self.era_start(c, ident))
            for pre in {resource_prefix(r) for r in linked}:
                prefix_counts.setdefault(pre, []).append(sum(resource_prefix(r) == pre for r in linked))
            accs = [r for r in linked if resource_prefix(r) == "account"]
            taken.update(accs)
            subject[c["case_id"]] = ident.user_id
            if accs:
                continue
            rep = P(c["reported_at"])
            lo = max(P(c["requested_at"]), rep - timedelta(hours=config.WORKFLOW_WINDOW_H))
            exp = self.STATUS_RESULT.get(c["reported_status"])
            own_ok = lambda r: not self.owners.get(r) or self.owners.get(r) == {ident.user_id}
            cand[c["case_id"]] = [a for a in self.activities
                                  if a["source_system"] == "deletion_worker" and a["target_system"] == "account_service"
                                  and lo <= P(a["event_time"]) <= rep and a["reported_result"] == exp
                                  and own_ok(a["resource_id"])]
        # 2) resolve: requests with a single remaining candidate claim it first; others take the job
        #    closest to reported_at that nobody else claimed
        # categories no subject ever holds twice (learned): an orphan of such a category cannot be
        # attributed to a subject who already holds one
        self.single_instance = {p for p, n in prefix_counts.items()
                                if len(n) >= config.MIN_SUPPORT and max(n) == 1 and p != "account"}
        for cid in cand:
            cand[cid] = [a for a in cand[cid] if a["resource_id"] not in taken]
            # lattice: keep the candidate jobs that are in phase with most of the subject's own
            # (evidence-attributed or chain-linked) workflow events
            own = [b for b in self.activities if b["source_system"] == "deletion_worker"
                   and b["target_system"] != "account_service"
                   and (self._sole_owner(b["resource_id"]) == subject[cid]
                        or self.chain_owner.get(b["activity_id"]) == subject[cid])]
            score = {a["activity_id"]: sum(bool(self.lattice_fit(b, P(a["event_time"]))) for b in own)
                     for a in cand[cid]}
            best = max(score.values(), default=0)
            if best > 0:
                cand[cid] = [a for a in cand[cid] if score[a["activity_id"]] == best]
        pending = dict(cand)
        while pending:
            forced = [cid for cid, lst in pending.items() if len(lst) <= 1]
            pick = forced[0] if forced else min(pending)
            lst = pending.pop(pick)
            choice = (min if self.TIEBREAK_EARLIEST else max)(lst, key=lambda a: a["event_time"]) if lst else None
            self.assigned_accounts[pick] = choice
            if choice:
                for cid in pending:
                    pending[cid] = [a for a in pending[cid] if a["resource_id"] != choice["resource_id"]]
        for dup, orig in alias.items():
            if orig in self.assigned_accounts:
                self.assigned_accounts[dup] = self.assigned_accounts[orig]
        wins = {}
        for c in cases:
            if c["case_id"] in alias:
                continue
            ident = self.ids.resolve(c["email"])
            if ident is None:
                continue
            linked = self.linked_resources(ident, c["audit_at"], self.era_start(c, ident))
            wf = self.workflow_resources(c, ident, linked)
            accs = [r for r in list(linked) + list(wf) if resource_prefix(r) == "account"]
            times = [P(a["event_time"]) for a in self.activities if a["resource_id"] in accs
                     and a["source_system"] == "deletion_worker"
                     and P(c["requested_at"]) <= P(a["event_time"]) <= P(c["reported_at"])]
            if times:
                wins[c["case_id"]] = (min(times), P(c["reported_at"]))
                self.case_subject[c["case_id"]] = ident.user_id
        self.case_windows = wins
