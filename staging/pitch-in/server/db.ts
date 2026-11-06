import { DatabaseSync } from "node:sqlite";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { config } from "./config.ts";

mkdirSync(config.dataDir, { recursive: true });

export const db = new DatabaseSync(process.env.DB_PATH ?? join(config.dataDir, "pitch-in.db"));

db.exec(`
PRAGMA journal_mode = WAL;
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, paypal_email TEXT NOT NULL UNIQUE,
  completed_rechecks INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS bounties (
  id TEXT PRIMARY KEY, data TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pledges (
  id TEXT PRIMARY KEY, bounty_id TEXT NOT NULL, data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS photos (
  id TEXT PRIMARY KEY, bounty_id TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS payouts (
  id TEXT PRIMARY KEY, bounty_id TEXT NOT NULL, stage TEXT NOT NULL, amount_cents INTEGER NOT NULL,
  batch_id TEXT NOT NULL UNIQUE, paypal_batch_id TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS votes (
  bounty_id TEXT NOT NULL, stage TEXT NOT NULL, funder_id TEXT NOT NULL, choice TEXT NOT NULL,
  PRIMARY KEY (bounty_id, stage, funder_id)
);
CREATE TABLE IF NOT EXISTS objections (
  bounty_id TEXT NOT NULL, funder_id TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY (bounty_id, funder_id)
);
CREATE TABLE IF NOT EXISTS cases (
  id TEXT PRIMARY KEY, bounty_id TEXT, opened_by TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL,
  status TEXT NOT NULL, resolution TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ledger (
  seq INTEGER PRIMARY KEY, at TEXT NOT NULL, bounty_id TEXT, event TEXT NOT NULL,
  data TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS renewals (new_id TEXT PRIMARY KEY, old_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS notifications (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, bounty_id TEXT, text TEXT NOT NULL, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS checks (
  id TEXT PRIMARY KEY, bounty_id TEXT NOT NULL, stage TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL
);
`);

export const newId = (prefix: string) => `${prefix}_${randomUUID().replace(/-/g, "").slice(0, 12)}`;

// Small JSON-document helpers for the tables that store a "data" column.
export function getDoc<T>(table: "bounties" | "pledges" | "photos" | "checks", id: string): T | null {
  const row = db.prepare(`SELECT data FROM ${table} WHERE id = ?`).get(id) as { data: string } | undefined;
  return row ? (JSON.parse(row.data) as T) : null;
}

export function listDocs<T>(table: "bounties" | "pledges" | "photos" | "checks", where = "1=1", ...params: (string | number)[]): T[] {
  const rows = db.prepare(`SELECT data FROM ${table} WHERE ${where}`).all(...params) as { data: string }[];
  return rows.map((r) => JSON.parse(r.data) as T);
}

export function tx<T>(fn: () => T): T {
  db.exec("BEGIN IMMEDIATE");
  try {
    const out = fn();
    db.exec("COMMIT");
    return out;
  } catch (e) {
    db.exec("ROLLBACK");
    throw e;
  }
}
