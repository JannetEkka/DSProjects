"""Evidence normalizer.

Every supplied evidence file (SQL snapshot, JSON export, log, plain-text
handover, PDF, screenshot) is turned into a flat list of ``Observation``
objects: "at time T, file F showed resource R in system S with these fields".
Down-stream logic never touches raw formats again.
"""
from __future__ import annotations

import csv
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

RESOURCE_RE = re.compile(
    r"\b(account|search|analytics|support|export|data_flow|backup|audit_record|"
    r"tombstone|legal_hold|marketing|object|cache|email_log|telemetry)_\d+\b"
)

DOC_RESOURCE_RE = re.compile(
    r"(?<![A-Za-z_])(account|search|analytics|support|export|data_flow|backup|audit_record|"
    r"tombstone|legal_hold|marketing|object|cache)_\d+\b"
)

PREFIX_SYSTEM = {
    "account": "account_service",
    "search": "search_service",
    "analytics": "analytics_platform",
    "support": "support_platform",
    "export": "export_service",
    "data_flow": "integration_service",
    "backup": "backup_service",
    "audit_record": "security_service",
    "tombstone": "identity_service",
    "legal_hold": "legal_service",
    "marketing": "marketing_platform",
    "object": "object_storage",
    "cache": "cache_service",
}


def resource_prefix(rid: str) -> str:
    m = re.match(r"^(.*)_\d+$", rid)
    return m.group(1) if m else rid


def system_for(rid: str) -> str:
    return PREFIX_SYSTEM.get(resource_prefix(rid), "unknown_service")


@dataclass
class Observation:
    evidence_id: str
    time: str  # ISO timestamp of the observation itself
    captured_at: str  # capture time of the file (manifest)
    system: str
    resource_id: str
    source: str  # parser family, for debugging / explanation
    fields: dict = field(default_factory=dict)  # normalized lower-case keys -> value (str/bool/None)
    keys: set = field(default_factory=set)  # lookup keys used to fetch this resource (trace context)

    def get(self, *names, default=None):
        for n in names:
            if n in self.fields:
                return self.fields[n]
        return default


# --------------------------------------------------------------------------- helpers

def _norm_val(v):
    if isinstance(v, str):
        s = v.strip()
        if s.lower() in ("null", "none", ""):
            return None
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
        return s
    return v


def flatten(d, prefix="", out=None):
    out = {} if out is None else out
    if isinstance(d, dict):
        for k, v in d.items():
            key = k.lower()
            if isinstance(v, (dict, list)):
                flatten(v, key + ".", out) if isinstance(v, dict) else out.setdefault(prefix + key, json.dumps(v))
                if isinstance(v, dict):
                    # also expose nested keys without prefix for convenience
                    for kk, vv in v.items():
                        if not isinstance(vv, (dict, list)):
                            out.setdefault(kk.lower(), _norm_val(vv))
            else:
                out[prefix + key] = _norm_val(v)
    return out


KV_RE = re.compile(r'([A-Za-z_][\w.]*)=("(?:[^"\\]|\\.)*"|\S+)')


def parse_kv(text: str) -> dict:
    out = {}
    for k, v in KV_RE.findall(text):
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1].replace('\\"', '"')
        out[k.lower()] = _norm_val(v)
    return out


TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s*(.*)$")


def parse_log_line(line: str):
    """Return (ts, dict) for any of the supported log dialects, or None."""
    m = TS_RE.match(line.strip())
    if not m:
        return None
    ts, rest = m.groups()
    d: dict = {}
    if rest.startswith("{"):
        try:
            d = {k.lower(): _norm_val(v) for k, v in json.loads(rest).items()}
        except json.JSONDecodeError:
            d = parse_kv(rest)
        if "logger" in d and "service" not in d:
            d["service"] = d["logger"]
    elif rest.startswith("<"):  # RFC5424 syslog
        # <pri>ver host app procid msgid sd kv...
        parts = rest.split(" ", 6)
        if len(parts) >= 7:
            d = parse_kv(parts[6])
            d.setdefault("service", parts[2])
            d.setdefault("trace_id", parts[3])
    elif rest.startswith("["):  # [LEVEL] [service] [trace] event: kv
        mm = re.match(r"\[(\w+)\]\s*\[([^\]]+)\]\s*\[([^\]]+)\]\s*([\w.]+):\s*(.*)$", rest)
        if mm:
            lvl, svc, trace, event, kv = mm.groups()
            d = parse_kv(kv)
            d.update({"level": lvl, "service": svc, "trace_id": trace, "event": event})
    elif rest.startswith("|"):
        parts = [p.strip() for p in rest.strip("| ").split("|")]
        if len(parts) >= 5:
            lvl, svc, trace, event = parts[:4]
            d = parse_kv(" ".join(parts[4:]))
            d.update({"level": lvl, "service": svc, "trace_id": trace, "event": event})
    else:
        d = parse_kv(rest)
        if "message" in d and isinstance(d["message"], str) and "=" in d["message"]:
            inner = parse_kv(d.pop("message"))
            d.update(inner)
        if "function" in d and "service" not in d:
            d["service"] = d["function"]
        if "requestid" in d and "trace_id" not in d:
            d["trace_id"] = d["requestid"]
    return ts, d


LOOKUP_KEYS = ("lookup_key", "match_key", "subject_key", "owner_key", "scan_key", "subject_ref", "correlation_key")


class EvidenceStore:
    def __init__(self, dataset_dir: Path, media_extractor=None):
        self.dataset_dir = Path(dataset_dir)
        self.manifest = {}
        with open(self.dataset_dir / "evidence_files.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.manifest[row["file_id"]] = row
        self.observations: list[Observation] = []
        # snapshot coverage: (evidence_id, system, captured_at, set(resource ids present))
        self.coverage: list[tuple] = []
        self.media_extractor = media_extractor
        self.media_text: dict[str, str] = {}
        self.parse_errors: list[str] = []
        for eid, row in self.manifest.items():
            path = self.dataset_dir / row["file_path"]
            try:
                self._load(eid, path, row["captured_at"])
            except Exception as exc:  # keep going; record the failure
                self.parse_errors.append(f"{eid}: {exc!r}")

    # ------------------------------------------------------------------ dispatch
    def _add(self, eid, time, captured, rid, source, fields, keys=(), system=None):
        if not rid or not RESOURCE_RE.fullmatch(rid):
            return
        sysid = system or fields.get("system") or fields.get("origin_system") or fields.get("data_store")
        if not sysid or sysid in ("profile_service",):
            sysid = system_for(rid)
        if system_for(rid) != "unknown_service":
            sysid = system_for(rid)
        self.observations.append(
            Observation(eid, time or captured, captured, sysid, rid, source, dict(fields), set(k for k in keys if k))
        )

    def _load(self, eid, path: Path, captured):
        ext = path.suffix.lower()
        if ext == ".sql":
            self._load_sql(eid, path, captured)
        elif ext == ".json":
            self._load_json(eid, path, captured)
        elif ext == ".log":
            self._load_log(eid, path, captured)
        elif ext == ".txt":
            self._load_text(eid, path.read_text(encoding="utf-8"), captured, "text")
        elif ext == ".pdf":
            self._load_pdf(eid, path, captured)
        elif ext in (".png", ".jpg", ".jpeg"):
            self._load_image(eid, path, captured)

    # ------------------------------------------------------------------ SQL
    def _load_sql(self, eid, path, captured):
        con = sqlite3.connect(":memory:")
        con.executescript(path.read_text(encoding="utf-8"))
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table'")]
        scope = {}
        if "snapshot_scope" in tables:
            scope = dict(cur.execute("select origin_system, captured_at from snapshot_scope").fetchall())
        per_system: dict[str, set] = {}
        for t in tables:
            if t == "snapshot_scope":
                continue
            cols = [c[1] for c in cur.execute(f'pragma table_info("{t}")')]
            for row in cur.execute(f'select * from "{t}"').fetchall():
                rec = dict(zip(cols, row))
                fields = {k.lower(): _norm_val(v) for k, v in rec.items()}
                if "record_json" in rec:
                    fields.pop("record_json")
                    fields.update(flatten(json.loads(rec["record_json"])))
                fields["table"] = t
                rid = fields.get("resource_id")
                time = fields.get("updated_at") or fields.get("indexed_at") or captured
                if time and time > captured:
                    time = captured
                self._add(eid, time, captured, rid, "sql", fields)
                if rid:
                    per_system.setdefault(system_for(rid), set()).add(rid)
        for sysid, cap in scope.items():
            self.coverage.append((eid, sysid, cap, per_system.get(sysid, set())))
        if not scope:
            for sysid, rids in per_system.items():
                self.coverage.append((eid, sysid, captured, rids))

    # ------------------------------------------------------------------ JSON
    def _load_json(self, eid, path, captured):
        d = json.loads(path.read_text(encoding="utf-8"))
        if "service_exports" in d:
            for sysid, colls in d["service_exports"].items():
                for coll, rows in colls.items():
                    for r in rows:
                        fields = flatten(r)
                        fields["collection"] = coll
                        keys = []
                        if "hits" in r and isinstance(r["hits"], dict):
                            fields["total_hits"] = r["hits"].get("total")
                            docs = r["hits"].get("documents") or []
                            keys.append(r.get("query"))
                            if docs:
                                for doc in docs:
                                    f2 = dict(fields)
                                    f2.update({k.lower(): _norm_val(v) for k, v in doc.items()})
                                    f2["result"] = "hit"
                                    self._add(eid, r.get("observed_at"), captured, doc.get("resource_id"), "json_export", f2, keys, sysid)
                                continue
                            fields["result"] = "miss"
                        self._add(eid, r.get("observed_at"), captured, r.get("resource_id"), "json_export", fields, keys, sysid)
        elif "snapshots" in d:
            for snap in d["snapshots"]:
                cap = snap.get("captured_at") or captured
                rids = set()
                for r in snap.get("records", []):
                    fields = flatten(r)
                    fields["collection"] = snap.get("collection")
                    self._add(eid, r.get("recorded_at") or cap, captured, r.get("resource_id"), "json_snapshot", fields, (), snap.get("data_store"))
                    rids.add(r.get("resource_id"))
                self.coverage.append((eid, snap.get("data_store"), cap, rids))
        elif "records" in d:
            for r in d["records"]:
                fields = flatten(r)
                fields["collection"] = d.get("collection")
                t = r.get("recorded_at") or r.get("observed_at") or d.get("captured_at") or captured
                self._add(eid, t, captured, r.get("resource_id"), "json_records", fields, (), r.get("system"))

    # ------------------------------------------------------------------ logs
    def _load_log(self, eid, path, captured):
        traces: dict[str, dict] = {}
        order = []
        for line in path.read_text(encoding="utf-8").splitlines():
            parsed = parse_log_line(line)
            if not parsed:
                continue
            ts, d = parsed
            if d.get("event") == "record_lookup" or ("record_type" in d and "resource_id" in d and "result" in d):
                self._add(eid, ts, captured, d.get("resource_id"), "log_record", d, (), d.get("system"))
                continue
            tid = d.get("trace_id") or f"__line{len(order)}"
            if tid not in traces:
                traces[tid] = {"keys": set(), "events": []}
                order.append(tid)
            tr = traces[tid]
            for k in LOOKUP_KEYS:
                if d.get(k):
                    tr["keys"].add(str(d[k]))
            tr["events"].append((ts, d))
        for tid in order:
            tr = traces[tid]
            for ts, d in tr["events"]:
                rid = d.get("resource_id")
                if not rid:
                    continue
                ev = str(d.get("event", ""))
                if ev.endswith("_started"):
                    continue
                self._add(eid, ts, captured, rid, "log_trace", d, tr["keys"], None)

    # ------------------------------------------------------------------ text / pdf / images
    HANDOVER_RE = re.compile(
        r"^-?\s*(\S+Z)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(.+)$"
    )

    def _load_text(self, eid, text, captured, source):
        structured = False
        for line in text.splitlines():
            m = self.HANDOVER_RE.match(line.strip())
            if m:
                ts, sysid, rid, rtype, result, ref = m.groups()
                ref = ref.strip()
                fields = {"system": sysid, "record_type": rtype, "result": result,
                          "subject_reference": None if ref.lower().startswith("no direct") else ref}
                self._add(eid, ts, captured, rid, source, fields, (), sysid)
                structured = True
        if not structured:
            self._load_document_text(eid, text, captured, source)

    def _load_document_text(self, eid, text, captured, source):
        """Unstructured business artifact (PDF/screenshot). Emit one observation per resource id
        mentioned, carrying the whole document text so identifiers can be matched."""
        # OCR can glue a row number onto an id ("1data_flow_9846"), so do not require a word boundary
        rids = sorted(set(m.group(0) for m in DOC_RESOURCE_RE.finditer(text)))
        lines = text.splitlines()
        for rid in rids:
            if len(rids) == 1 and source == "pdf":
                context = text  # single-subject artifact (e.g. one attachment, one detail page)
            else:
                # multi-row screen: only the row(s) naming this resource describe it
                context = "\n".join(l for l in lines if re.search(rf"(?<![A-Za-z_]){re.escape(rid)}\b", l))
            self._add(eid, captured, captured, rid, source,
                      {"document_text": context, "full_text": text, "mentions_only": True}, (), None)
        self.media_text[eid] = text

    def _load_pdf(self, eid, path, captured):
        text = ""
        try:
            import pdfplumber

            with pdfplumber.open(str(path)) as pdf:
                text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        except Exception:
            try:
                from pypdf import PdfReader

                text = "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
            except Exception as exc:
                self.parse_errors.append(f"{eid}: pdf {exc!r}")
        self._load_document_text(eid, text, captured, "pdf")

    def _load_image(self, eid, path, captured):
        text = ""
        if self.media_extractor is not None:
            text = self.media_extractor.extract(path) or ""
        self._load_document_text(eid, text, captured, "image")
