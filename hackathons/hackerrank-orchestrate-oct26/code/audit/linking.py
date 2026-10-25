"""Linking: which resources an identity's evidence reaches (identifier matches, verified catalog
links, connector/restore lineage), plus the global owner index used to keep strangers' records out."""
from __future__ import annotations

import re
from datetime import datetime

from . import config
from .evidence import Observation, RESOURCE_RE
from .identity import Identity
from .semantics import TEXT_FIELDS, links_to


class LinkingMixin:
    """Evidence -> resource linking. Expects `store`, `ids`, `activities`, `by_resource` on the engine."""

    def _attach_catalog_media(self):
        """The data catalog registers each business artifact (screenshot / PDF) a few minutes after
        capture and names the resource it shows. Pair the artifact with that resource so its contents
        become an observation of the resource."""
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        media = [(eid, row) for eid, row in self.store.manifest.items()
                 if row["file_path"].lower().endswith((".png", ".jpg", ".jpeg", ".pdf"))]
        for a in self.activities:
            if a["event_type"] != "LINK_RESOURCE_IDENTITY":
                continue
            t = P(a["event_time"])
            best = None
            for eid, row in media:
                dt = (t - P(row["captured_at"])).total_seconds()
                if 0 <= dt <= config.CATALOG_MEDIA_WINDOW_S and (best is None or dt < best[0]):
                    best = (dt, eid, row)
            if not best:
                continue
            _, eid, row = best
            text = self.store.media_text.get(eid, "")
            o = Observation(eid, row["captured_at"], row["captured_at"], a["target_system"], a["resource_id"],
                            "catalog_media", {"document_text": text + "\n" + a["details"], "mentions_only": True, "no_link": True},
                            set())
            self.store.observations.append(o)
            self.by_resource.setdefault(a["resource_id"], []).append(o)
            self.catalog_media[a["activity_id"]] = (eid, text)

    def _artifact_contradicts(self, activity, ident) -> bool:
        """A catalog link is a claim. If the artifact it was registered from shows the resource with
        someone else's contact details and none of the subject's, the claim is rejected."""
        eid, text = self.catalog_media.get(activity["activity_id"], (None, ""))
        if not text or self.TRUST_CATALOG:
            return False
        rid = activity["resource_id"]
        rows = [l for l in text.splitlines() if rid in l.replace(" ", "")] or text.splitlines()
        ctx = "\n".join(rows)
        if ident.mentioned_in(ctx) or ident.mentioned_in(text):
            return False
        emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", ctx)
        return bool(emails)

    def _build_owner_index(self):
        """resource_id -> set(user_id) linked by any direct identifier in any evidence (global view).
        Used to avoid attributing another person's resource to the subject."""
        val2u = {}
        for uid in self.ids.users:
            ident = self.ids.resolve_user(uid)
            for v in ident.strong:
                val2u.setdefault(v, set()).add(uid)
        owners = {}
        for o in self.store.observations:
            vals = [k.lower() for k in o.keys] + [str(v).strip().lower() for v in o.fields.values() if isinstance(v, str)]
            for v in vals:
                for u in val2u.get(v, ()):
                    owners.setdefault(o.resource_id, set()).add(u)
        for a in self.activities:
            if a["event_type"] == "LINK_RESOURCE_IDENTITY":
                for m in re.finditer(r"\buser_\d+\b", a["details"]):
                    owners.setdefault(a["resource_id"], set()).add(m.group(0))
        return owners


    def linked_resources(self, ident: Identity, audit_at: str, since: str = "") -> dict[str, list[str]]:
        """resource_id -> list of evidence ids that link it to the subject (in (since, audit_at])."""
        key = (ident.user_id, audit_at, since, self.TRUST_CATALOG)
        cache = self.__dict__.setdefault("_link_cache", {})
        if key not in cache:
            cache[key] = self._linked_resources(ident, audit_at, since)
        return {k: list(v) for k, v in cache[key].items()}

    def _build_value_index(self):
        """Inverted index: lower-cased identifier value -> observations carrying it (exact-value fields
        and lookup keys). Free-text observations are kept aside and scanned with substring matching."""
        idx, text_obs = {}, []
        for o in self.store.observations:
            if o.fields.get("no_link"):
                continue
            vals = {k.strip().lower() for k in o.keys}
            for k, v in o.fields.items():
                if k in TEXT_FIELDS:
                    if v:
                        text_obs.append(o)
                elif isinstance(v, str):
                    vals.add(v.strip().lower())
            for v in vals:
                idx.setdefault(v, []).append(o)
        self._value_index, self._text_obs = idx, text_obs

    def _linked_resources(self, ident: Identity, audit_at: str, since: str = "") -> dict[str, list[str]]:
        linked: dict[str, list[str]] = {}
        if not hasattr(self, "_value_index"):
            self._build_value_index()
        cands = {id(o): o for v in ident.strong for o in self._value_index.get(v, [])}
        for o in self._text_obs:
            cands.setdefault(id(o), o)
        for o in sorted(cands.values(), key=lambda o: (o.time, o.evidence_id, o.resource_id)):
            if o.time > audit_at or o.time <= since:
                continue
            if links_to(o, ident):
                linked.setdefault(o.resource_id, []).append(o.evidence_id)
        # catalog links and connector->downstream dependencies from the activity stream
        for a in self.activities:
            if a["event_time"] > audit_at or a["event_time"] <= since:
                continue
            d = a["details"]
            if a["event_type"] == "LINK_RESOURCE_IDENTITY":
                if (ident.mentioned_in(d) or re.search(rf"\b{re.escape(ident.user_id)}\b", d)) \
                        and not self._artifact_contradicts(a, ident):
                    linked.setdefault(a["resource_id"], []).append(a["activity_id"])
        changed = True
        while changed:
            changed = False
            for a in self.activities:
                if a["event_time"] > audit_at:
                    continue
                if a["event_type"] in ("SYNC_RECORD", "RESTORE_BACKUP") and "repopulated downstream resource" in a["details"]:
                    m = RESOURCE_RE.search(a["details"].split("resource", 1)[1])
                    if m and m.group(0) in linked and a["resource_id"] not in linked:
                        linked[a["resource_id"]] = [a["activity_id"]]
                        changed = True
        return linked
