// The money rules. Plain code, no AI: the AI's verdict is an input here, and these
// functions decide whether money may move. Every function is pure and unit-tested.

import { config } from "./config.ts";
import type { Bounty, FraudFlag, Pledge, ProofVerdict, RecheckVerdict, User } from "./types.ts";

export interface Decision<A extends string> {
  action: A;
  reasons: string[]; // human-readable, shown to funders and the doer, written to the ledger
}

const MIN_CONFIDENCE = 0.75;

export type Tier = "small" | "medium" | "large";

export function tierOf(goalCents: number): Tier {
  if (goalCents <= config.limits.smallBountyCents) return "small";
  if (goalCents <= config.limits.largeBountyCents) return "medium";
  return "large";
}

export function authorizedTotal(pledges: Pledge[]): number {
  return pledges.filter((p) => p.status === "authorized").reduce((s, p) => s + p.amount_cents, 0);
}

export function earliestExpiry(pledges: Pledge[]): string | null {
  const exp = pledges
    .filter((p) => p.status === "authorized" && p.auth_expires_at)
    .map((p) => p.auth_expires_at as string)
    .sort();
  return exp[0] ?? null;
}

// ---------- claiming ----------

export function canClaim(
  b: Bounty,
  user: User,
  pledges: Pledge[],
  now: Date,
  doerOpenCents: number,
): Decision<"allow" | "deny"> {
  const reasons: string[] = [];
  if (b.status !== "funded") reasons.push(`This bounty is ${b.status}, not open to claim.`);
  if (b.hazard) reasons.push(`Hazardous job (${b.hazard}): referred to the council, not claimable.`);
  if (b.reporter_id === user.id) reasons.push("You reported this problem, so you can't also be paid to fix it.");
  if (pledges.some((p) => p.funder_id === user.id && p.status !== "voided"))
    reasons.push("You pledged to this bounty, so you can't also be paid from it.");
  const exp = earliestExpiry(pledges);
  if (exp) {
    const daysLeft = (new Date(exp).getTime() - now.getTime()) / 86_400_000;
    if (daysLeft < config.limits.minHoldDaysToClaim)
      reasons.push(
        `The pledges' PayPal holds expire in ${daysLeft.toFixed(1)} days; a claim needs at least ${config.limits.minHoldDaysToClaim}. Funders have been asked to renew.`,
      );
  }
  const cap = user.completed_rechecks > 0 ? config.limits.doerDailyCapCents : config.limits.newDoerCapCents;
  if (doerOpenCents + b.goal_cents > cap)
    reasons.push(
      `This would take you to $${((doerOpenCents + b.goal_cents) / 100).toFixed(2)} of open work; your limit is $${(cap / 100).toFixed(2)}${user.completed_rechecks > 0 ? " a day" : " until your first fix passes its recheck"}.`,
    );
  return reasons.length ? { action: "deny", reasons } : { action: "allow", reasons: ["All claim checks passed."] };
}

// ---------- releasing the proof-stage payment ----------

export type ReleaseAction = "capture_and_pay" | "objection_window" | "needs_neighbour" | "vote";

export function decideRelease(
  b: Bounty,
  verdict: ProofVerdict,
  flags: FraudFlag[],
  opts: { neighbourConfirmed: boolean; objectionWindowOver: boolean; objections: number },
): Decision<ReleaseAction> {
  const reasons: string[] = [];
  const blocking = flags.filter((f) => f.blocking);
  for (const f of blocking) reasons.push(`Blocked: ${f.detail}`);
  if (!verdict.same_place.pass || verdict.same_place.confidence < MIN_CONFIDENCE)
    reasons.push(`Not shown to be the same place (${verdict.same_place.reason}).`);
  for (const c of verdict.criteria) {
    if (!c.pass) reasons.push(`Checklist "${c.id}" not met: ${c.reason}`);
    else if (c.confidence < MIN_CONFIDENCE) reasons.push(`Checklist "${c.id}" unclear (confidence ${c.confidence.toFixed(2)}): ${c.reason}`);
  }
  const ids = new Set(verdict.criteria.map((c) => c.id));
  for (const item of b.checklist) if (!ids.has(item.id)) reasons.push(`Checklist "${item.id}" was not assessed.`);
  if (verdict.staged_suspected) reasons.push(`Possible staging: ${verdict.staged_reason}`);
  if (verdict.instructions_in_image) reasons.push("A photo contains text addressed to the checker. It was ignored and the bounty goes to the funders.");

  // The AI never rejects on its own: anything short of a clean pass goes to the funders.
  if (reasons.length) return { action: "vote", reasons };
  if (opts.objections > 0) return { action: "vote", reasons: [`${opts.objections} funder objection(s) during the window.`] };

  const tier = tierOf(b.goal_cents);
  if (tier === "large" && !opts.neighbourConfirmed)
    return { action: "needs_neighbour", reasons: ["All checks passed. Over $100, so a neighbour must confirm on the spot."] };
  if (tier !== "small" && !opts.objectionWindowOver)
    return { action: "objection_window", reasons: [`All checks passed. Funders have ${config.limits.objectionWindowHours} hours to object before capture.`] };
  return { action: "capture_and_pay", reasons: ["Every checklist item, the same-place check and the fraud checks passed."] };
}

// ---------- splitting money ----------

export interface CaptureLine {
  pledge_id: string;
  amount_cents: number;
  final: boolean;
}

// Pro-rata capture: each funder pays their share of the goal, never more than they authorised.
// Leftover cents go to the largest pledges first, then by id, so the result is deterministic.
export function capturePlan(goalCents: number, pledges: Pledge[]): CaptureLine[] {
  const live = pledges.filter((p) => p.status === "authorized");
  const total = live.reduce((s, p) => s + p.amount_cents, 0);
  if (total === 0) return [];
  const target = Math.min(goalCents, total);
  const lines = live.map((p) => ({ pledge_id: p.id, amount_cents: Math.floor((p.amount_cents * target) / total), max: p.amount_cents }));
  let left = target - lines.reduce((s, l) => s + l.amount_cents, 0);
  const order = [...lines].sort((a, b) => b.max - a.max || a.pledge_id.localeCompare(b.pledge_id));
  for (const l of order) {
    if (left === 0) break;
    if (l.amount_cents < l.max) {
      l.amount_cents += 1;
      left -= 1;
    }
  }
  return lines.map((l) => ({ pledge_id: l.pledge_id, amount_cents: l.amount_cents, final: true }));
}

export function payoutSplit(capturedCents: number, holdbackPct: number): { now_cents: number; held_cents: number } {
  const held = Math.round((capturedCents * holdbackPct) / 100);
  return { now_cents: capturedCents - held, held_cents: held };
}

// A payout may never exceed what was captured for this bounty minus what was already paid or refunded.
export function canPayout(amountCents: number, capturedCents: number, paidCents: number, refundedCents: number): Decision<"allow" | "deny"> {
  const room = capturedCents - paidCents - refundedCents;
  if (!Number.isInteger(amountCents) || amountCents <= 0) return { action: "deny", reasons: ["Payout amount must be a positive whole number of cents."] };
  if (amountCents > room)
    return { action: "deny", reasons: [`Payout of ${amountCents}¢ exceeds the ${room}¢ captured and not yet paid or refunded.`] };
  return { action: "allow", reasons: ["Within captured funds."] };
}

// ---------- the recheck ----------

export function decideRecheck(v: RecheckVerdict, flags: FraudFlag[]): Decision<"release_held" | "vote"> {
  const reasons: string[] = [];
  for (const f of flags.filter((f) => f.blocking)) reasons.push(`Blocked: ${f.detail}`);
  if (!v.same_place) reasons.push("The recheck photo doesn't show the same place.");
  if (!v.still_fixed) reasons.push(`Not still fixed: ${v.reason}`);
  else if (v.confidence < MIN_CONFIDENCE) reasons.push(`Unclear whether it held (confidence ${v.confidence.toFixed(2)}): ${v.reason}`);
  return reasons.length ? { action: "vote", reasons } : { action: "release_held", reasons: [`The fix held: ${v.reason}`] };
}

// ---------- votes ----------

// Votes are weighted by the amount pledged. Ties and no-shows favour the doer.
export function tallyVote(pledges: Pledge[], votes: { funder_id: string; choice: "pay" | "refund" }[]): Decision<"pay" | "refund"> {
  const weight = new Map<string, number>();
  for (const p of pledges) if (p.status !== "voided") weight.set(p.funder_id, (weight.get(p.funder_id) ?? 0) + p.amount_cents);
  let pay = 0;
  let refund = 0;
  for (const v of votes) {
    const w = weight.get(v.funder_id) ?? 0;
    if (v.choice === "pay") pay += w;
    else refund += w;
  }
  const total = [...weight.values()].reduce((s, w) => s + w, 0);
  if (refund * 2 > total) return { action: "refund", reasons: [`Funders holding ${refund}¢ of ${total}¢ voted to refund.`] };
  return { action: "pay", reasons: [`Refund votes (${refund}¢ of ${total}¢) are not a majority; the doer is paid.`] };
}

// ---------- holds that are running out ----------

export function holdsNeedingRenewal(pledges: Pledge[], now: Date, withinDays = 7): Pledge[] {
  return pledges.filter(
    (p) => p.status === "authorized" && p.auth_expires_at && new Date(p.auth_expires_at).getTime() - now.getTime() < withinDays * 86_400_000,
  );
}
