"""Identity resolution: every email, phone and email hash a stable user_id has ever held."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Identity:
    user_id: str
    emails: set = field(default_factory=set)
    phones: set = field(default_factory=set)
    hashes: set = field(default_factory=set)
    names: set = field(default_factory=set)
    audit_ids: list = field(default_factory=list)

    @property
    def strong(self) -> set:
        return {v.lower() for v in self.emails | self.phones | self.hashes} | {self.user_id.lower()}

    def matches_value(self, v) -> bool:
        if not isinstance(v, str):
            return False
        return v.strip().lower() in self.strong

    def mentioned_in(self, text) -> bool:
        if not isinstance(text, str) or not text:
            return False
        t = text.lower()
        if any(e.lower() in t for e in self.emails | self.hashes):
            return True
        if any(p in text for p in self.phones):
            return True
        return re.search(rf"\b{re.escape(self.user_id)}\b", text) is not None


class IdentityResolver:
    def __init__(self, dataset_dir: Path):
        self.users = {}
        with open(dataset_dir / "user_identities.csv", newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                self.users[r["user_id"]] = Identity(r["user_id"], {r["email"].lower()}, {r["phone"]},
                                                   {r["email_hash"]}, {r["name"]})
        self.history = []
        p = dataset_dir / "user_audit_log.csv"
        if p.exists():
            with open(p, newline="", encoding="utf-8-sig") as f:
                self.history = list(csv.DictReader(f))
        self.by_email = {}
        for u in self.users.values():
            for e in u.emails:
                self.by_email.setdefault(e, set()).add(u.user_id)
        for h in self.history:
            if h["field_name"] == "email":
                for v in (h["old_value"], h["new_value"]):
                    self.by_email.setdefault(v.lower(), set()).add(h["user_id"])

    def resolve(self, email: str, as_of: str | None = None) -> Identity | None:
        cands = self.by_email.get(email.strip().lower(), set())
        if not cands:
            return None
        return self.resolve_user(sorted(cands)[0])

    @staticmethod
    def adhoc(email: str) -> Identity:
        """Identity built from the request email alone, for an address no identity table knows."""
        e = email.strip().lower()
        return Identity(f"unregistered:{e}", {e})

    def resolve_user(self, uid: str) -> Identity:
        base = self.users[uid]
        ident = Identity(uid, set(base.emails), set(base.phones), set(base.hashes), set(base.names))
        for h in self.history:
            if h["user_id"] != uid:
                continue
            fld = h["field_name"]
            vals = [h["old_value"], h["new_value"]]
            target = {"email": ident.emails, "phone": ident.phones, "email_hash": ident.hashes,
                      "name": ident.names}.get(fld)
            if target is not None:
                for v in vals:
                    if v:
                        target.add(v.lower() if fld == "email" else v)
            ident.audit_ids.append(h["audit_id"])
        return ident
