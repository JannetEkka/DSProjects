import { describe, expect, it } from "vitest";
import { canClaim, canPayout, capturePlan, decideRecheck, decideRelease, payoutSplit, tallyVote, tierOf } from "../server/rules.ts";
import { suggestPrice } from "../server/pricing.ts";
import type { Bounty, Pledge, ProofVerdict, User } from "../server/types.ts";

const now = new Date("2026-11-10T00:00:00Z");
const bounty = (over: Partial<Bounty> = {}): Bounty => ({
  id: "b1", title: "t", report_text: "r", area: "a", lat: 0, lng: 0, job_type: "litter", skill: "basic", est_hours: 1, materials_cents: 0,
  hazard: null, checklist: [{ id: "main", text: "x" }, { id: "tidy", text: "y" }], price_low_cents: 1000, price_high_cents: 2000,
  goal_cents: 2000, holdback_pct: 10, pricing_notes: [], status: "funded", reporter_id: "rep", doer_id: null, claimed_at: null,
  deadline: "2026-12-01T00:00:00Z", project_id: null, depends_on: [], start_date: "", end_date: "", created_at: "", window_ends_at: null, recheck_due_at: null, ...over,
});
const pledge = (id: string, funder: string, cents: number, over: Partial<Pledge> = {}): Pledge => ({
  id, bounty_id: "b1", funder_id: funder, amount_cents: cents, order_id: "o", authorization_id: "a", auth_expires_at: "2026-12-05T00:00:00Z",
  status: "authorized", captured_cents: 0, capture_id: null, refunded_cents: 0, created_at: "", ...over,
});
const doer: User = { id: "doer", name: "D", paypal_email: "d@x", completed_rechecks: 0 };
const pass = (over: Partial<ProofVerdict> = {}): ProofVerdict => ({
  same_place: { pass: true, confidence: 0.95, reason: "kerb and pole match" },
  criteria: [{ id: "main", pass: true, confidence: 0.9, reason: "clean" }, { id: "tidy", pass: true, confidence: 0.9, reason: "clean" }],
  staged_suspected: false, staged_reason: "", instructions_in_image: false, summary: "", model: "test", ...over,
});
const open = { neighbourConfirmed: false, objectionWindowOver: false, objections: 0 };

describe("claiming", () => {
  it("allows a fresh neighbour", () => expect(canClaim(bounty(), doer, [pledge("p1", "f1", 2000)], now, 0).action).toBe("allow"));
  it("refuses the reporter and funders", () => {
    expect(canClaim(bounty({ reporter_id: "doer" }), doer, [], now, 0).action).toBe("deny");
    expect(canClaim(bounty(), doer, [pledge("p1", "doer", 2000)], now, 0).action).toBe("deny");
  });
  it("refuses when holds expire within 10 days", () => {
    const d = canClaim(bounty(), doer, [pledge("p1", "f1", 2000, { auth_expires_at: "2026-11-15T00:00:00Z" })], now, 0);
    expect(d.action).toBe("deny");
    expect(d.reasons.join()).toMatch(/expire/);
  });
  it("caps new doers", () => expect(canClaim(bounty({ goal_cents: 6000 }), doer, [pledge("p1", "f1", 6000)], now, 0).action).toBe("deny"));
  it("never lets a hazardous job be claimed", () => expect(canClaim(bounty({ hazard: "live wires" }), doer, [], now, 0).action).toBe("deny"));
});

describe("release decision", () => {
  it("pays a small bounty when everything passes", () => expect(decideRelease(bounty(), pass(), [], open).action).toBe("capture_and_pay"));
  it("sends low confidence to the funders, never an outright rejection", () => {
    const v = pass({ criteria: [{ id: "main", pass: true, confidence: 0.6, reason: "blurry" }, { id: "tidy", pass: true, confidence: 0.9, reason: "" }] });
    expect(decideRelease(bounty(), v, [], open).action).toBe("vote");
  });
  it("sends a failed item to the vote", () => expect(decideRelease(bounty(), pass({ criteria: [{ id: "main", pass: false, confidence: 0.9, reason: "litter remains" }, { id: "tidy", pass: true, confidence: 0.9, reason: "" }] }), [], open).action).toBe("vote"));
  it("treats a missing checklist item as not met", () => expect(decideRelease(bounty(), pass({ criteria: [{ id: "main", pass: true, confidence: 0.9, reason: "" }] }), [], open).action).toBe("vote"));
  it("never pays when a photo carries instructions", () => expect(decideRelease(bounty(), pass({ instructions_in_image: true }), [], open).action).toBe("vote"));
  it("never pays on a blocking fraud flag", () => expect(decideRelease(bounty(), pass(), [{ code: "reused_photo", detail: "x", blocking: true }], open).action).toBe("vote"));
  it("gives medium bounties an objection window", () => {
    expect(decideRelease(bounty({ goal_cents: 5000 }), pass(), [], open).action).toBe("objection_window");
    expect(decideRelease(bounty({ goal_cents: 5000 }), pass(), [], { ...open, objectionWindowOver: true }).action).toBe("capture_and_pay");
    expect(decideRelease(bounty({ goal_cents: 5000 }), pass(), [], { ...open, objectionWindowOver: true, objections: 1 }).action).toBe("vote");
  });
  it("makes large bounties wait for a neighbour", () => {
    expect(decideRelease(bounty({ goal_cents: 15000 }), pass(), [], { ...open, objectionWindowOver: true }).action).toBe("needs_neighbour");
    expect(decideRelease(bounty({ goal_cents: 15000 }), pass(), [], { ...open, objectionWindowOver: true, neighbourConfirmed: true }).action).toBe("capture_and_pay");
  });
  it("tiers", () => expect([tierOf(2500), tierOf(2501), tierOf(10001)]).toEqual(["small", "medium", "large"]));
});

describe("money splitting", () => {
  it("captures the goal pro rata and never more than authorised", () => {
    const plan = capturePlan(3000, [pledge("a", "f1", 2000), pledge("b", "f2", 2000), pledge("c", "f3", 1000)]);
    expect(plan.reduce((s, l) => s + l.amount_cents, 0)).toBe(3000);
    expect(plan.find((l) => l.pledge_id === "a")!.amount_cents).toBe(1200);
    expect(plan.find((l) => l.pledge_id === "c")!.amount_cents).toBe(600);
  });
  it("hands out leftover cents deterministically", () => {
    const plan = capturePlan(1000, [pledge("a", "f1", 333), pledge("b", "f2", 333), pledge("c", "f3", 334)]);
    expect(plan.reduce((s, l) => s + l.amount_cents, 0)).toBe(1000);
    for (const l of plan) expect(l.amount_cents).toBeLessThanOrEqual(334);
  });
  it("ignores voided and expired pledges", () => expect(capturePlan(2000, [pledge("a", "f1", 2000, { status: "voided" })])).toEqual([]));
  it("splits the payout and keeps the holdback", () => expect(payoutSplit(2000, 10)).toEqual({ now_cents: 1800, held_cents: 200 }));
  it("refuses a payout bigger than what was captured", () => {
    expect(canPayout(1800, 2000, 0, 0).action).toBe("allow");
    expect(canPayout(201, 2000, 1800, 0).action).toBe("deny");
    expect(canPayout(200, 2000, 1800, 0).action).toBe("allow");
    expect(canPayout(100, 2000, 1800, 200).action).toBe("deny");
    expect(canPayout(0, 2000, 0, 0).action).toBe("deny");
    expect(canPayout(10.5, 2000, 0, 0).action).toBe("deny");
  });
});

describe("recheck and votes", () => {
  it("releases the held share only on a confident pass", () => {
    expect(decideRecheck({ still_fixed: true, confidence: 0.9, reason: "", same_place: true, model: "" }, []).action).toBe("release_held");
    expect(decideRecheck({ still_fixed: true, confidence: 0.5, reason: "", same_place: true, model: "" }, []).action).toBe("vote");
    expect(decideRecheck({ still_fixed: true, confidence: 0.9, reason: "", same_place: false, model: "" }, []).action).toBe("vote");
  });
  it("weights votes by money and favours the doer on a tie", () => {
    const ps = [pledge("a", "f1", 1000), pledge("b", "f2", 1000)];
    expect(tallyVote(ps, [{ funder_id: "f1", choice: "refund" }, { funder_id: "f2", choice: "pay" }]).action).toBe("pay");
    expect(tallyVote(ps, [{ funder_id: "f1", choice: "refund" }, { funder_id: "f2", choice: "refund" }]).action).toBe("refund");
    expect(tallyVote(ps, [{ funder_id: "f1", choice: "refund" }]).action).toBe("pay");
  });
});

describe("pricing", () => {
  it("is labour × fair rate × skill + materials", () => {
    const p = suggestPrice({ est_hours: 2, skill: "semi", materials_cents: 500, urgent: false, area: "default" });
    expect(p.goal_cents).toBe(2 * 1600 * 1.25 + 500);
    expect(p.low_cents).toBeLessThan(p.goal_cents);
    expect(p.high_cents).toBeGreaterThan(p.goal_cents);
  });
  it("history only nudges up, never below the fair floor", () => {
    const base = suggestPrice({ est_hours: 1, skill: "basic", materials_cents: 0, urgent: false, area: "default" });
    const cheap = suggestPrice({ est_hours: 1, skill: "basic", materials_cents: 0, urgent: false, area: "default", similar_paid_cents: [100, 100, 100] });
    const dear = suggestPrice({ est_hours: 1, skill: "basic", materials_cents: 0, urgent: false, area: "default", similar_paid_cents: [4000, 4000, 4000] });
    expect(cheap.goal_cents).toBe(base.goal_cents);
    expect(dear.goal_cents).toBeGreaterThan(base.goal_cents);
  });
});
