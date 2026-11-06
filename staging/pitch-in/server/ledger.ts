// Append-only receipt log. Each entry's hash covers the previous entry's hash, so changing or
// deleting any past entry breaks every hash after it. Anyone can re-run verify().

import { createHash } from "node:crypto";
import { db } from "./db.ts";
import { clock } from "./clock.ts";

export interface LedgerEntry {
  seq: number;
  at: string;
  bounty_id: string | null;
  event: string;
  data: Record<string, unknown>;
  prev_hash: string;
  hash: string;
}

const GENESIS = "0".repeat(64);

// Stable JSON: object keys sorted, so the same data always hashes the same way.
export function canonical(v: unknown): string {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return `[${v.map(canonical).join(",")}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o)
    .filter((k) => o[k] !== undefined)
    .sort()
    .map((k) => `${JSON.stringify(k)}:${canonical(o[k])}`)
    .join(",")}}`;
}

export function hashEntry(e: Omit<LedgerEntry, "hash">): string {
  return createHash("sha256").update(canonical({ seq: e.seq, at: e.at, bounty_id: e.bounty_id, event: e.event, data: e.data, prev_hash: e.prev_hash })).digest("hex");
}

export function record(bountyId: string | null, event: string, data: Record<string, unknown>): LedgerEntry {
  const last = db.prepare("SELECT seq, hash FROM ledger ORDER BY seq DESC LIMIT 1").get() as { seq: number; hash: string } | undefined;
  const base = { seq: (last?.seq ?? 0) + 1, at: clock.iso(), bounty_id: bountyId, event, data, prev_hash: last?.hash ?? GENESIS };
  const entry = { ...base, hash: hashEntry(base) };
  db.prepare("INSERT INTO ledger (seq, at, bounty_id, event, data, prev_hash, hash) VALUES (?, ?, ?, ?, ?, ?, ?)").run(
    entry.seq,
    entry.at,
    entry.bounty_id,
    entry.event,
    JSON.stringify(entry.data),
    entry.prev_hash,
    entry.hash,
  );
  return entry;
}

export function entries(bountyId?: string): LedgerEntry[] {
  const rows = (
    bountyId
      ? db.prepare("SELECT * FROM ledger WHERE bounty_id = ? ORDER BY seq").all(bountyId)
      : db.prepare("SELECT * FROM ledger ORDER BY seq").all()
  ) as unknown as (Omit<LedgerEntry, "data"> & { data: string })[];
  return rows.map((r) => ({ ...r, data: JSON.parse(r.data) }));
}

export function verify(all: LedgerEntry[] = entries()): { ok: boolean; count: number; broken_at: number | null; head: string } {
  let prev = GENESIS;
  for (const e of all) {
    const { hash, ...rest } = e;
    if (e.prev_hash !== prev || hashEntry(rest) !== hash) return { ok: false, count: all.length, broken_at: e.seq, head: prev };
    prev = hash;
  }
  return { ok: true, count: all.length, broken_at: null, head: prev };
}
