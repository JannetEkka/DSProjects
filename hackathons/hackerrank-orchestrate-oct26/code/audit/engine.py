"""Deletion-audit engine facade: identity resolution, resource linking, state reconstruction,
policy application and step planning. Fully deterministic.

The work is split by concern; this module wires the parts together and keeps the public names
(`AuditEngine`, `IdentityResolver`, `OP_META`, `OP_ORDER`) importable from one place:

* identity.py  - current + historical identifiers of a user_id
* semantics.py - what one observation says (category, state) and whether it names a subject
* linking.py   - evidence -> resources, catalog verification, owner index
* workflow.py  - workflow attribution, one-to-one job assignment, learned timing model
* planner.py   - state at audit_at, policy -> ordered steps
* config.py    - tunable constants
"""
from __future__ import annotations

import csv
from pathlib import Path

from .evidence import EvidenceStore, Observation
from .identity import Identity, IdentityResolver
from .linking import LinkingMixin
from .planner import DEFAULT_TREATMENT, OP_META, OP_ORDER, PlannerMixin, ResourceState
from .semantics import classify, classify_document, links_to
from .workflow import WorkflowMixin

__all__ = ["AuditEngine", "Identity", "IdentityResolver", "OP_META", "OP_ORDER", "ResourceState",
           "classify", "classify_document", "links_to"]


class AuditEngine(LinkingMixin, WorkflowMixin, PlannerMixin):
    # ablation switches (set per instance by evaluation/main.py)
    DISABLE_WORKFLOW = False
    TRUST_CATALOG = False
    DISABLE_ERAS = False
    DISABLE_TIMING = False
    TIEBREAK_EARLIEST = True

    def __init__(self, dataset_dir: Path, store: EvidenceStore, identities: IdentityResolver):
        self.dataset_dir = Path(dataset_dir)
        self.store = store
        self.ids = identities
        self.rules = self._load_rules()
        self.activities = self._load_activities()
        self.by_resource: dict[str, list[Observation]] = {}
        for o in store.observations:
            self.by_resource.setdefault(o.resource_id, []).append(o)
        self.catalog_media = {}
        self._attach_catalog_media()
        for lst in self.by_resource.values():
            lst.sort(key=lambda o: (o.time, o.evidence_id))
        self.owners = self._build_owner_index()
        # global per-run state, filled by prepare()
        self.case_windows: dict | None = None
        self.case_subject: dict[str, str] = {}
        self.all_cases: list[dict] = []
        self.assigned_accounts: dict[str, dict | None] = {}
        self.single_instance: set[str] = set()
        self.lattice: dict[str, set[int]] = {}
        self.lattice_period: int | None = None
        self.chain_gaps: dict[str, list[int]] = {}
        self.chain_owner: dict[str, str] = {}
        self.timing_holdout: set[str] = set()  # users excluded from timing-model learning

    def _load_rules(self):
        rules = dict(DEFAULT_TREATMENT)
        self.rule_rows = {}
        p = self.dataset_dir / "deletion_rules.csv"
        with open(p, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rules[r["data_category"]] = r["required_action"]
                self.rule_rows[r["data_category"]] = r
        return rules

    def _load_activities(self):
        with open(self.dataset_dir / "system_activity.csv", newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
