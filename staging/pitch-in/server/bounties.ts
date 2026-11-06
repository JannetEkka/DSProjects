// The bounty lifecycle. Each step: check permissions, call PayPal or the AI, apply rules.ts, write the ledger.
// PayPal calls use request ids derived from our own ids, and payouts are reserved in the database
// (unique batch id) before PayPal is called, so retries and double clicks can't pay twice.

import { config } from "./config.ts";
import { clock } from "./clock.ts";
import { db, getDoc, listDocs, newId } from "./db.ts";
import { record } from "./ledger.ts";
import { paypal, PayPalError } from "./paypal.ts";
import { draftBounty, verifyProof, verifyRecheck } from "./ai.ts";
import { suggestPrice, HOLDBACK_PCT } from "./pricing.ts";
import { fraudFlags, photosFor, readPhoto, repeatPairFlag, storePhoto } from "./photos.ts";
import {
  authorizedTotal,
  canClaim,
  canPayout,
  capturePlan,
  decideRecheck,
  decideRelease,
  holdsNeedingRenewal,
  payoutSplit,
  tallyVote,
  tierOf,
} from "./rules.ts";
import type { Bounty, FraudFlag, Pledge, PhotoKind, ProofVerdict, User } from "./types.ts";

export class Refused extends Error {
  constructor(public reasons: string[]) {
    super(reasons.join(" "));
  }
}

// ---------------- storage helpers ----------------

export function getUser(id: string): User {
  const u = db.prepare("SELECT * FROM users WHERE id = ?").get(id) as User | undefined;
  if (!u) throw new Refused([`Unknown user ${id}.`]);
  return u;
}
export function listUsers(): User[] {
  return db.prepare("SELECT * FROM users ORDER BY name").all() as unknown as User[];
}
export function getBounty(id: string): Bounty {
  const b = getDoc<Bounty>("bounties", id);
  if (!b) throw new Refused([`Unknown bounty ${id}.`]);
  return b;
}
export function listBounties(): Bounty[] {
  return listDocs<Bounty>("bounties").sort((a, b) => b.created_at.localeCompare(a.created_at));
}
function saveBounty(b: Bounty) {
  db.prepare("INSERT INTO bounties (id, data, status, created_at) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data, status = excluded.status").run(
    b.id,
    JSON.stringify(b),
    b.status,
    b.created_at,
  );
}
export function pledgesFor(bountyId: string): Pledge[] {
  return listDocs<Pledge>("pledges", "bounty_id = ?", bountyId).sort((a, b) => a.created_at.localeCompare(b.created_at));
}
function savePledge(p: Pledge) {
  db.prepare("INSERT INTO pledges (id, bounty_id, data) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data").run(p.id, p.bounty_id, JSON.stringify(p));
}
export function payoutsFor(bountyId: string) {
  return db.prepare("SELECT * FROM payouts WHERE bounty_id = ? ORDER BY created_at").all(bountyId) as unknown as {
    id: string;
    bounty_id: string;
    stage: string;
    amount_cents: number;
    batch_id: string;
    paypal_batch_id: string | null;
    status: string;
    created_at: string;
  }[];
}
export function checksFor(bountyId: string) {
  return (db.prepare("SELECT data FROM checks WHERE bounty_id = ? ORDER BY created_at").all(bountyId) as { data: string }[]).map((r) => JSON.parse(r.data));
}
function saveCheck(bountyId: string, stage: string, data: Record<string, unknown>) {
  const id = newId("chk");
  db.prepare("INSERT INTO checks (id, bounty_id, stage, data, created_at) VALUES (?, ?, ?, ?, ?)").run(id, bountyId, stage, JSON.stringify({ id, stage, ...data, at: clock.iso() }), clock.iso());
  return id;
}

export function notify(userIds: string[], bountyId: string | null, text: string) {
  for (const u of new Set(userIds.filter(Boolean))) db.prepare("INSERT INTO notifications VALUES (?, ?, ?, ?, ?)").run(newId("n"), u, bountyId, text, clock.iso());
}

export function openCase(bountyId: string | null, openedBy: string, kind: string, body: string) {
  const id = newId("case");
  db.prepare("INSERT INTO cases (id, bounty_id, opened_by, kind, body, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'open', ?, ?)").run(
    id,
    bountyId,
    openedBy,
    kind,
    body,
    clock.iso(),
    clock.iso(),
  );
  record(bountyId, "case.opened", { case_id: id, kind, opened_by: openedBy, body });
  return id;
}

const funderIds = (bountyId: string) => [...new Set(pledgesFor(bountyId).filter((p) => p.status !== "voided" && p.status !== "created").map((p) => p.funder_id))];

// ---------------- 1. report → draft ----------------

export async function reportProblem(input: { reporter_id: string; text: string; photo: Buffer | null; lat: number; lng: number; accuracy: number | null; area: string; live_capture: boolean; project_id?: string; depends_on?: string[] }) {
  getUser(input.reporter_id);
  if (!input.text.trim()) throw new Refused(["Describe the problem in a sentence or two."]);
  const d = await draftBounty(input.text, input.photo);
  const similar = listBounties()
    .filter((b) => b.job_type === d.job_type && (b.status === "closed" || b.status === "paid"))
    .map((b) => b.goal_cents);
  const price = suggestPrice({ est_hours: d.est_hours, skill: d.skill, materials_cents: d.materials_cents, urgent: d.urgent, area: "default", similar_paid_cents: similar });
  const now = clock.now();
  const b: Bounty = {
    id: newId("b"),
    title: d.title,
    report_text: input.text,
    area: input.area,
    lat: input.lat,
    lng: input.lng,
    job_type: d.job_type,
    skill: d.skill,
    est_hours: d.est_hours,
    materials_cents: d.materials_cents,
    hazard: d.hazard,
    checklist: d.checklist,
    price_low_cents: price.low_cents,
    price_high_cents: price.high_cents,
    goal_cents: price.goal_cents,
    holdback_pct: HOLDBACK_PCT[d.job_type],
    pricing_notes: [...price.notes, d.reasoning],
    status: d.hazard ? "referred" : "draft",
    reporter_id: input.reporter_id,
    doer_id: null,
    claimed_at: null,
    deadline: new Date(now.getTime() + 21 * 86_400_000).toISOString(),
    project_id: input.project_id ?? null,
    depends_on: input.depends_on ?? [],
    start_date: now.toISOString(),
    end_date: new Date(now.getTime() + 21 * 86_400_000).toISOString(),
    created_at: now.toISOString(),
    window_ends_at: null,
    recheck_due_at: null,
  };
  saveBounty(b);
  if (input.photo)
    await storePhoto({ bounty_id: b.id, user_id: input.reporter_id, kind: "report", image: input.photo, lat: input.lat, lng: input.lng, accuracy: input.accuracy, live_capture: input.live_capture });
  record(b.id, "bounty.drafted", { by: input.reporter_id, model: d.model, job_type: b.job_type, skill: b.skill, est_hours: b.est_hours, goal_cents: b.goal_cents, checklist: b.checklist, hazard: b.hazard });
  if (b.hazard) {
    record(b.id, "bounty.referred", { hazard: b.hazard, note: "Hazardous jobs are never priced; a council report was prepared instead." });
    openCase(b.id, "system", "council_report", `Hazard (${b.hazard}). Report for the municipality: ${b.report_text}`);
  }
  return b;
}

export function publish(bountyId: string, userId: string, goalCents?: number) {
  const b = getBounty(bountyId);
  if (b.reporter_id !== userId) throw new Refused(["Only the reporter can publish their draft."]);
  if (b.status !== "draft") throw new Refused([`This bounty is ${b.status}.`]);
  if (goalCents !== undefined) {
    if (!Number.isInteger(goalCents) || goalCents < b.price_low_cents) throw new Refused([`The goal can't be below the fair-price floor of $${(b.price_low_cents / 100).toFixed(2)}.`]);
    b.goal_cents = goalCents;
  }
  b.status = "funding";
  saveBounty(b);
  record(b.id, "bounty.published", { by: userId, goal_cents: b.goal_cents, holdback_pct: b.holdback_pct });
  return b;
}

// ---------------- 2. pledges (PayPal: create order → buyer approves → authorize) ----------------

export async function startPledge(bountyId: string, funderId: string, amountCents: number, renewOf?: string) {
  const b = getBounty(bountyId);
  getUser(funderId);
  if (!["funding", "funded", "claimed"].includes(b.status)) throw new Refused([`This bounty is ${b.status} and isn't taking pledges.`]);
  if (b.doer_id === funderId) throw new Refused(["You claimed this bounty, so you can't fund it."]);
  if (!Number.isInteger(amountCents) || amountCents < 100 || amountCents > 50000) throw new Refused(["Pledges are between $1 and $500."]);
  const p: Pledge = {
    id: newId("pl"),
    bounty_id: b.id,
    funder_id: funderId,
    amount_cents: amountCents,
    order_id: "",
    authorization_id: null,
    auth_expires_at: null,
    status: "created",
    captured_cents: 0,
    capture_id: null,
    refunded_cents: 0,
    created_at: clock.iso(),
  };
  const order = await paypal.createOrder({ amount_cents: amountCents, bounty_id: b.id, pledge_id: p.id, description: `Pledge to "${b.title}" (held, charged only if the fix is verified)` }, `order-${p.id}`);
  p.order_id = order.id;
  savePledge(p);
  record(b.id, "pledge.order_created", { pledge_id: p.id, funder_id: funderId, amount_cents: amountCents, order_id: order.id, renew_of: renewOf ?? null });
  if (renewOf) db.prepare("INSERT INTO renewals (new_id, old_id) VALUES (?, ?)").run(p.id, renewOf);
  return p;
}

export async function confirmPledge(pledgeId: string, funderId: string) {
  const p = getDoc<Pledge>("pledges", pledgeId);
  if (!p) throw new Refused(["Unknown pledge."]);
  if (p.funder_id !== funderId) throw new Refused(["That pledge isn't yours."]);
  if (p.status !== "created") return p; // idempotent: already authorised
  // PayPal is the source of truth: check the order really is approved and for the amount we asked.
  const o = await paypal.getOrder(p.order_id);
  if (o.amount_cents !== p.amount_cents) throw new Refused([`PayPal order amount ${o.amount_cents}¢ doesn't match the pledge ${p.amount_cents}¢.`]);
  if (o.status !== "APPROVED" && paypal.mode === "sandbox") throw new Refused([`The PayPal order is ${o.status}, not approved yet.`]);
  const a = await paypal.authorizeOrder(p.order_id, `auth-${p.id}`);
  if (a.amount_cents !== p.amount_cents) throw new Refused([`Authorised ${a.amount_cents}¢, expected ${p.amount_cents}¢.`]);
  p.authorization_id = a.id;
  p.auth_expires_at = a.expires_at;
  p.status = "authorized";
  savePledge(p);
  record(p.bounty_id, "pledge.authorized", { pledge_id: p.id, funder_id: funderId, amount_cents: p.amount_cents, authorization_id: a.id, expires_at: a.expires_at, payer_email: o.payer_email ?? null });

  // A renewal replaces an older hold: void the old one now that the new one is in place.
  const ren = db.prepare("SELECT old_id FROM renewals WHERE new_id = ?").get(p.id) as { old_id: string } | undefined;
  if (ren) await voidPledge(ren.old_id, "renewed");

  const b = getBounty(p.bounty_id);
  if (b.status === "funding" && authorizedTotal(pledgesFor(b.id)) >= b.goal_cents) {
    b.status = "funded";
    saveBounty(b);
    record(b.id, "bounty.funded", { authorized_cents: authorizedTotal(pledgesFor(b.id)), goal_cents: b.goal_cents });
    notify([b.reporter_id, ...funderIds(b.id)], b.id, `"${b.title}" is fully pledged and open to claim.`);
  }
  return p;
}

async function voidPledge(pledgeId: string, why: string) {
  const p = getDoc<Pledge>("pledges", pledgeId);
  if (!p || p.status !== "authorized" || !p.authorization_id) return;
  try {
    await paypal.voidAuthorization(p.authorization_id, `void-${p.id}`);
  } catch (e) {
    if (!(e instanceof PayPalError && e.status === 422)) throw e; // already expired/voided at PayPal: fine
  }
  p.status = "voided";
  savePledge(p);
  record(p.bounty_id, "pledge.voided", { pledge_id: p.id, authorization_id: p.authorization_id, why, charged_cents: 0 });
}

// ---------------- 3. claim ----------------

function doerOpenCents(userId: string) {
  return listBounties()
    .filter((b) => b.doer_id === userId && ["claimed", "checking", "objection_window", "needs_neighbour", "vote"].includes(b.status))
    .reduce((s, b) => s + b.goal_cents, 0);
}

export function claim(bountyId: string, userId: string) {
  const b = getBounty(bountyId);
  const user = getUser(userId);
  const unfinishedDeps = b.depends_on.filter((d) => !["paid", "closed"].includes(getBounty(d).status));
  if (unfinishedDeps.length) throw new Refused([`Do these first: ${unfinishedDeps.map((d) => getBounty(d).title).join(", ")}.`]);
  const d = canClaim(b, user, pledgesFor(b.id), clock.now(), doerOpenCents(userId));
  record(b.id, d.action === "allow" ? "claim.allowed" : "claim.refused", { user_id: userId, reasons: d.reasons });
  if (d.action === "deny") throw new Refused(d.reasons);
  b.status = "claimed";
  b.doer_id = userId;
  b.claimed_at = clock.iso();
  saveBounty(b);
  notify([b.reporter_id, ...funderIds(b.id)], b.id, `${user.name} claimed "${b.title}".`);
  return b;
}

// ---------------- 4. photos ----------------

export async function addPhoto(input: { bounty_id: string; user_id: string; kind: PhotoKind; image: Buffer; lat: number | null; lng: number | null; accuracy: number | null; live_capture: boolean }) {
  const b = getBounty(input.bounty_id);
  getUser(input.user_id);
  const isDoer = b.doer_id === input.user_id;
  const isFunder = funderIds(b.id).includes(input.user_id);
  if (input.kind === "report") throw new Refused(["Report photos are added when the problem is reported."]);
  if ((input.kind === "before" || input.kind === "after") && (!isDoer || b.status !== "claimed")) throw new Refused(["Only the doer adds before and after photos, while the bounty is claimed."]);
  if (input.kind === "after" && !photosFor(b.id, "before").length) throw new Refused(["Take the before photo first."]);
  if (input.kind === "confirm" && (b.status !== "needs_neighbour" || isDoer || isFunder || b.reporter_id === input.user_id))
    throw new Refused(["A confirming neighbour can't be the doer, the reporter or a funder, and the bounty must be waiting for confirmation."]);
  if (input.kind === "recheck" && (b.status !== "paid" || isDoer)) throw new Refused(["Rechecks are taken by someone other than the doer, after the proof stage is paid."]);
  const photo = await storePhoto(input);
  record(b.id, "photo.added", { photo_id: photo.id, kind: photo.kind, by: input.user_id, dhash: photo.dhash, live_capture: photo.live_capture, at: photo.taken_at });
  return photo;
}

// ---------------- 5. proof ----------------

export async function submitProof(bountyId: string, userId: string) {
  const b = getBounty(bountyId);
  if (b.doer_id !== userId || b.status !== "claimed") throw new Refused(["Only the doer can submit proof for a claimed bounty."]);
  const before = photosFor(b.id, "before").at(-1);
  const after = photosFor(b.id, "after").at(-1);
  if (!before || !after) throw new Refused(["Add a before and an after photo first."]);
  const report = photosFor(b.id, "report").at(-1) ?? null;
  b.status = "checking";
  saveBounty(b);

  const all = listDocs<import("./types.ts").Photo>("photos");
  const flags: FraudFlag[] = [...fraudFlags(b, before, report, all), ...fraudFlags(b, after, before, all)];
  const pair = repeatPairFlag(b, userId, listBounties());
  if (pair) flags.push(pair);
  const verdict = await verifyProof({ checklist: b.checklist, report: report ? readPhoto(report) : null, before: readPhoto(before), after: readPhoto(after) });
  if (verdict.instructions_in_image) flags.push({ code: "instructions_in_image", detail: "A photo contains text aimed at the checker.", blocking: true });
  if (verdict.staged_suspected) flags.push({ code: "staged_suspected", detail: verdict.staged_reason, blocking: true });
  const checkId = saveCheck(b.id, "proof", { verdict, flags, photos: { report: report?.id ?? null, before: before.id, after: after.id } });
  record(b.id, "proof.checked", { check_id: checkId, model: verdict.model, same_place: verdict.same_place, criteria: verdict.criteria, flags: flags.map((f) => f.code), summary: verdict.summary });
  return applyReleaseDecision(b.id, verdict, flags);
}

function latestProof(bountyId: string): { verdict: ProofVerdict; flags: FraudFlag[] } {
  const c = checksFor(bountyId).filter((c) => c.stage === "proof").at(-1);
  if (!c) throw new Refused(["No proof check on record."]);
  return { verdict: c.verdict, flags: c.flags };
}

async function applyReleaseDecision(bountyId: string, verdict: ProofVerdict, flags: FraudFlag[]) {
  const b = getBounty(bountyId);
  const objections = (db.prepare("SELECT COUNT(*) AS n FROM objections WHERE bounty_id = ?").get(b.id) as { n: number }).n;
  const neighbourConfirmed = photosFor(b.id, "confirm").length > 0;
  const objectionWindowOver = !!b.window_ends_at && new Date(b.window_ends_at) <= clock.now();
  const d = decideRelease(b, verdict, flags, { neighbourConfirmed, objectionWindowOver, objections });
  record(b.id, "release.decided", { action: d.action, reasons: d.reasons, tier: tierOf(b.goal_cents) });
  if (d.action === "capture_and_pay") return releaseProofStage(b.id);
  if (d.action === "objection_window") {
    b.status = "objection_window";
    b.window_ends_at ??= new Date(clock.now().getTime() + config.limits.objectionWindowHours * 3_600_000).toISOString();
  } else if (d.action === "needs_neighbour") b.status = "needs_neighbour";
  else b.status = "vote";
  saveBounty(b);
  const who = [b.reporter_id, ...funderIds(b.id), ...(b.doer_id ? [b.doer_id] : [])];
  notify(who, b.id, `"${b.title}": ${d.reasons.join(" ")}`);
  return b;
}

export function object(bountyId: string, funderId: string, reason: string) {
  const b = getBounty(bountyId);
  if (!funderIds(b.id).includes(funderId)) throw new Refused(["Only funders can object."]);
  if (b.status !== "objection_window") throw new Refused(["Objections are open only during the 24-hour window."]);
  db.prepare("INSERT OR REPLACE INTO objections VALUES (?, ?, ?)").run(b.id, funderId, reason.slice(0, 500));
  record(b.id, "objection.raised", { funder_id: funderId, reason });
  b.status = "vote";
  saveBounty(b);
  notify([b.doer_id ?? "", ...funderIds(b.id)], b.id, `A funder objected to "${b.title}": ${reason}. Funders now vote; the doer can add photos.`);
  return b;
}

export async function neighbourConfirm(bountyId: string, userId: string, photo: { image: Buffer; lat: number | null; lng: number | null; accuracy: number | null; live_capture: boolean }) {
  await addPhoto({ bounty_id: bountyId, user_id: userId, kind: "confirm", ...photo });
  record(bountyId, "neighbour.confirmed", { by: userId });
  const { verdict, flags } = latestProof(bountyId);
  return applyReleaseDecision(bountyId, verdict, flags);
}

// Capture every pledge's share, then pay the doer the proof-stage share. Safe to re-run after a failure.
export async function releaseProofStage(bountyId: string) {
  const b = getBounty(bountyId);
  if (!b.doer_id) throw new Refused(["No doer."]);
  const doer = getUser(b.doer_id);
  const pledges = pledgesFor(b.id);
  const plan = capturePlan(b.goal_cents, pledges);
  try {
    for (const line of plan) {
      const p = pledges.find((x) => x.id === line.pledge_id)!;
      if (p.status !== "authorized" || !p.authorization_id) continue;
      const c = await paypal.captureAuthorization(p.authorization_id, line.amount_cents, true, `cap-${p.id}`, `${b.id}-${p.id}`);
      p.status = "captured";
      p.captured_cents = c.amount_cents;
      p.capture_id = c.id;
      savePledge(p);
      record(b.id, "pledge.captured", { pledge_id: p.id, authorization_id: p.authorization_id, capture_id: c.id, amount_cents: c.amount_cents, authorized_cents: p.amount_cents, released_cents: p.amount_cents - c.amount_cents });
    }
    const captured = pledgesFor(b.id).reduce((s, p) => s + p.captured_cents, 0);
    const split = payoutSplit(captured, b.holdback_pct);
    await payout(b, doer, "proof", split.now_cents, `Paid for "${b.title}". ${b.holdback_pct}% ($${(split.held_cents / 100).toFixed(2)}) follows if the fix holds at the ${config.limits.recheckAfterDays}-day recheck.`);
    b.status = "paid";
    b.recheck_due_at = new Date(clock.now().getTime() + config.limits.recheckAfterDays * 86_400_000).toISOString();
    saveBounty(b);
    record(b.id, "stage.proof_paid", { captured_cents: captured, paid_now_cents: split.now_cents, held_cents: split.held_cents, recheck_due_at: b.recheck_due_at });
    notify([b.reporter_id, ...funderIds(b.id)], b.id, `Your pledge paid for "${b.title}". Before and after photos are on the receipt.`);
    notify([doer.id], b.id, `You were paid $${(split.now_cents / 100).toFixed(2)} for "${b.title}".`);
    return b;
  } catch (e) {
    const msg = (e as Error).message;
    record(b.id, "release.failed", { error: msg.slice(0, 500) });
    openCase(b.id, "system", "payment_failed", `Releasing the proof stage failed: ${msg.slice(0, 500)}. It is safe to retry.`);
    throw e;
  }
}

async function payout(b: Bounty, doer: User, stage: "proof" | "recheck", amountCents: number, note: string) {
  const pledges = pledgesFor(b.id);
  const captured = pledges.reduce((s, p) => s + p.captured_cents, 0);
  const refunded = pledges.reduce((s, p) => s + p.refunded_cents, 0);
  const prior = payoutsFor(b.id).filter((p) => p.status !== "failed" && p.stage !== stage);
  const paid = prior.reduce((s, p) => s + p.amount_cents, 0);
  const d = canPayout(amountCents, captured, paid, refunded);
  if (d.action === "deny") {
    record(b.id, "payout.refused", { stage, amount_cents: amountCents, reasons: d.reasons });
    throw new Refused(d.reasons);
  }
  const batchId = `pi-${b.id}-${stage}`;
  const existing = payoutsFor(b.id).find((p) => p.batch_id === batchId);
  if (existing?.paypal_batch_id) return existing; // already paid: idempotent
  if (!existing)
    db.prepare("INSERT INTO payouts (id, bounty_id, stage, amount_cents, batch_id, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)").run(newId("po"), b.id, stage, amountCents, batchId, clock.iso());
  const r = await paypal.createPayout(batchId, { email: doer.paypal_email, amount_cents: amountCents, note, item_id: `${batchId}-1` });
  db.prepare("UPDATE payouts SET paypal_batch_id = ?, status = ? WHERE batch_id = ?").run(r.payout_batch_id, r.status, batchId);
  record(b.id, "payout.sent", { stage, amount_cents: amountCents, to: doer.paypal_email, batch_id: batchId, paypal_batch_id: r.payout_batch_id, status: r.status });
}

// ---------------- 6. recheck ----------------

export async function submitRecheck(bountyId: string, userId: string, photo: { image: Buffer; lat: number | null; lng: number | null; accuracy: number | null; live_capture: boolean }) {
  const b = getBounty(bountyId);
  if (b.status !== "paid") throw new Refused(["This bounty isn't waiting for a recheck."]);
  if (b.recheck_due_at && new Date(b.recheck_due_at) > clock.now())
    throw new Refused([`The recheck opens on ${b.recheck_due_at.slice(0, 10)}, ${config.limits.recheckAfterDays} days after the fix.`]);
  const ph = await addPhoto({ bounty_id: b.id, user_id: userId, kind: "recheck", ...photo });
  const after = photosFor(b.id, "after").at(-1)!;
  const flags = fraudFlags(b, ph, null, listDocs("photos"));
  const v = await verifyRecheck({ checklist: b.checklist, after: readPhoto(after), recheck: readPhoto(ph), days: Math.round((clock.now().getTime() - new Date(after.taken_at).getTime()) / 86_400_000) });
  if (v.instructions_in_image) flags.push({ code: "instructions_in_image", detail: "The recheck photo contains text aimed at the checker.", blocking: true });
  const checkId = saveCheck(b.id, "recheck", { verdict: v, flags, photos: { after: after.id, recheck: ph.id }, by: userId });
  const d = decideRecheck(v, flags);
  record(b.id, "recheck.checked", { check_id: checkId, by: userId, model: v.model, still_fixed: v.still_fixed, confidence: v.confidence, reason: v.reason, action: d.action, reasons: d.reasons });
  if (d.action === "release_held") return releaseHeld(b.id);
  b.status = "recheck_vote";
  saveBounty(b);
  notify([b.doer_id!, ...funderIds(b.id)], b.id, `Recheck of "${b.title}": ${d.reasons.join(" ")} Funders vote on the held-back share; the doer can respond.`);
  return b;
}

async function releaseHeld(bountyId: string) {
  const b = getBounty(bountyId);
  const doer = getUser(b.doer_id!);
  const pledges = pledgesFor(b.id);
  const captured = pledges.reduce((s, p) => s + p.captured_cents, 0);
  const held = payoutSplit(captured, b.holdback_pct).held_cents;
  if (held > 0) await payout(b, doer, "recheck", held, `The fix on "${b.title}" held at the recheck. This is the held-back share.`);
  b.status = "closed";
  saveBounty(b);
  db.prepare("UPDATE users SET completed_rechecks = completed_rechecks + 1 WHERE id = ?").run(doer.id);
  record(b.id, "bounty.closed", { outcome: "fix_held", held_paid_cents: held });
  notify([doer.id, ...funderIds(b.id), b.reporter_id], b.id, `"${b.title}" held at the recheck. Everything is settled.`);
  return b;
}

// Refund the held-back share to funders pro rata, against their captures.
async function refundHeld(bountyId: string, why: string) {
  const b = getBounty(bountyId);
  const pledges = pledgesFor(b.id).filter((p) => p.capture_id);
  const captured = pledges.reduce((s, p) => s + p.captured_cents, 0);
  const held = payoutSplit(captured, b.holdback_pct).held_cents;
  let left = held;
  for (const [i, p] of pledges.entries()) {
    const share = i === pledges.length - 1 ? left : Math.floor((held * p.captured_cents) / captured);
    left -= share;
    if (share <= 0) continue;
    const r = await paypal.refundCapture(p.capture_id!, share, `refund-${p.id}-held`, `Held-back share of "${b.title}" returned: ${why}`);
    p.refunded_cents += share;
    p.status = "refunded";
    savePledge(p);
    record(b.id, "pledge.refunded", { pledge_id: p.id, capture_id: p.capture_id, refund_id: r.id, amount_cents: share, why });
  }
  b.status = "closed";
  saveBounty(b);
  record(b.id, "bounty.closed", { outcome: "held_share_refunded", refunded_cents: held });
  return b;
}

// ---------------- votes ----------------

export async function vote(bountyId: string, funderId: string, choice: "pay" | "refund") {
  const b = getBounty(bountyId);
  const stage = b.status === "vote" ? "proof" : b.status === "recheck_vote" ? "recheck" : null;
  if (!stage) throw new Refused(["There's no vote open on this bounty."]);
  if (!funderIds(b.id).includes(funderId)) throw new Refused(["Only funders vote."]);
  db.prepare("INSERT OR REPLACE INTO votes VALUES (?, ?, ?, ?)").run(b.id, stage, funderId, choice);
  record(b.id, "vote.cast", { stage, funder_id: funderId, choice });
  const votes = db.prepare("SELECT funder_id, choice FROM votes WHERE bounty_id = ? AND stage = ?").all(b.id, stage) as { funder_id: string; choice: "pay" | "refund" }[];
  const pledges = pledgesFor(b.id);
  if (votes.length < funderIds(b.id).length) {
    // Decide early only once a side has a clear majority of the pledged money.
    const total = pledges.filter((p) => p.status !== "voided").reduce((s, p) => s + p.amount_cents, 0);
    const weightOf = (c: string) => votes.filter((v) => v.choice === c).reduce((s, v) => s + pledges.filter((p) => p.funder_id === v.funder_id).reduce((t, p) => t + p.amount_cents, 0), 0);
    if (weightOf("pay") * 2 <= total && weightOf("refund") * 2 <= total) return b;
  }
  const t = tallyVote(pledges, votes);
  record(b.id, "vote.decided", { stage, action: t.action, reasons: t.reasons });
  if (stage === "proof") {
    if (t.action === "pay") return releaseProofStage(b.id);
    for (const p of pledges) await voidPledge(p.id, "funders voted the proof didn't show the job done");
    b.status = "closed";
    saveBounty(b);
    record(b.id, "bounty.closed", { outcome: "not_paid_by_vote", charged_cents: 0 });
    return b;
  }
  return t.action === "pay" ? releaseHeld(b.id) : refundHeld(b.id, "funders voted the fix didn't hold");
}

// ---------------- time-based work (run every minute, and on demand in the demo) ----------------

export async function tick() {
  const now = clock.now();
  const out: string[] = [];
  for (const b of listBounties()) {
    const pledges = pledgesFor(b.id);
    // Holds PayPal has let lapse.
    for (const p of pledges.filter((p) => p.status === "authorized" && p.auth_expires_at && new Date(p.auth_expires_at) <= now)) {
      p.status = "expired";
      savePledge(p);
      record(b.id, "pledge.expired", { pledge_id: p.id, authorization_id: p.authorization_id, charged_cents: 0 });
      if (b.status === "claimed") openCase(b.id, "system", "hold_expired_during_work", `A pledge hold expired while ${b.doer_id} was working. Funders were asked to renew; support follows up.`);
      out.push(`${b.id}: hold ${p.id} expired`);
    }
    // Holds running out: ask funders to renew (one tap) before they lapse.
    if (["funding", "funded", "claimed"].includes(b.status))
      for (const p of holdsNeedingRenewal(pledgesFor(b.id), now)) {
        const key = `renew-asked-${p.id}`;
        const asked = db.prepare("SELECT 1 FROM ledger WHERE bounty_id = ? AND event = 'pledge.renewal_requested' AND data LIKE ?").get(b.id, `%${p.id}%`);
        if (!asked) {
          record(b.id, "pledge.renewal_requested", { pledge_id: p.id, expires_at: p.auth_expires_at, key });
          notify([p.funder_id], b.id, `Your hold for "${b.title}" expires ${p.auth_expires_at?.slice(0, 10)}. Tap Renew to keep it.`);
        }
      }
    // Objection window over with no objection: release.
    if (b.status === "objection_window" && b.window_ends_at && new Date(b.window_ends_at) <= now) {
      const { verdict, flags } = latestProof(b.id);
      await applyReleaseDecision(b.id, verdict, flags);
      out.push(`${b.id}: objection window over`);
    }
    // Deadline passed with nobody done: void every hold. Nobody is charged.
    if (["funding", "funded", "claimed"].includes(b.status) && new Date(b.deadline) <= now) {
      for (const p of pledges) await voidPledge(p.id, "deadline passed before the job was done");
      b.status = "expired";
      saveBounty(b);
      record(b.id, "bounty.expired", { charged_cents: 0 });
      notify([b.reporter_id, ...funderIds(b.id)], b.id, `"${b.title}" wasn't finished by the deadline. Your hold was cancelled; you weren't charged.`);
      out.push(`${b.id}: expired`);
    }
    if (b.status === "funded" && authorizedTotal(pledgesFor(b.id)) < b.goal_cents) {
      b.status = "funding";
      saveBounty(b);
      record(b.id, "bounty.underfunded", { authorized_cents: authorizedTotal(pledgesFor(b.id)), goal_cents: b.goal_cents });
    }
  }
  return out;
}

// ---------------- reconciliation: our records against PayPal's ----------------

export async function reconcile() {
  const mismatches: string[] = [];
  for (const b of listBounties()) {
    for (const p of pledgesFor(b.id)) {
      if (!p.authorization_id || p.status === "created") continue;
      try {
        const a = await paypal.getAuthorization(p.authorization_id);
        const expected: Record<string, string[]> = {
          authorized: ["CREATED", "PENDING"],
          captured: ["CAPTURED", "PARTIALLY_CAPTURED"],
          refunded: ["CAPTURED", "PARTIALLY_CAPTURED"],
          voided: ["VOIDED", "EXPIRED"],
          expired: ["EXPIRED", "VOIDED"],
        };
        if (!(expected[p.status] ?? []).includes(a.status)) mismatches.push(`${b.id}/${p.id}: we say ${p.status}, PayPal says ${a.status}`);
      } catch (e) {
        mismatches.push(`${b.id}/${p.id}: couldn't read authorization (${(e as Error).message.slice(0, 80)})`);
      }
    }
    for (const po of payoutsFor(b.id)) {
      if (!po.paypal_batch_id) {
        mismatches.push(`${b.id}: payout ${po.batch_id} reserved but never sent`);
        continue;
      }
      const r = await paypal.getPayout(po.paypal_batch_id);
      if (r.status === "DENIED" || r.items.some((i) => ["FAILED", "RETURNED", "BLOCKED"].includes(i.transaction_status)))
        mismatches.push(`${b.id}: payout ${po.paypal_batch_id} is ${r.status}/${r.items.map((i) => i.transaction_status).join(",")}`);
    }
  }
  record(null, "reconcile.run", { mismatches });
  for (const m of mismatches) openCase(m.split(/[/:]/)[0], "system", "reconcile_mismatch", m);
  return mismatches;
}
