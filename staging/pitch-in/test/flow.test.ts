import { describe, expect, it, beforeAll } from "vitest";
import sharp from "sharp";
import { db } from "../server/db.ts";
import { clock } from "../server/clock.ts";
import { verify, entries } from "../server/ledger.ts";
import * as B from "../server/bounties.ts";

// Distinct synthetic images: different gradients give different difference-hashes.
async function img(seed: number): Promise<Buffer> {
  const w = 64, h = 64;
  const raw = Buffer.alloc(w * h * 3);
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      const v = Math.floor(127 + 120 * Math.sin((x * (seed % 7 + 1) + y * (seed % 5 + 2)) / 6 + seed));
      raw.set([v, (v * seed) % 256, 255 - v], (y * w + x) * 3);
    }
  return sharp(raw, { raw: { width: w, height: h, channels: 3 } }).jpeg().toBuffer();
}
const here = { lat: 12.97, lng: 77.59, accuracy: 10, live_capture: true };

beforeAll(() => {
  const add = db.prepare("INSERT INTO users (id, name, paypal_email) VALUES (?, ?, ?)");
  for (const [id, name] of [["rep", "Reporter"], ["f1", "Funder One"], ["f2", "Funder Two"], ["doer", "Doer"], ["nb", "Neighbour"]]) add.run(id, name, `${id}@example.com`);
});

async function fundedBounty(text = "Litter all along the canal footpath near the bus stop") {
  const b = await B.reportProblem({ reporter_id: "rep", text, photo: await img(1 + Math.random() * 1000), area: "Canal Road", ...here });
  B.publish(b.id, "rep", 2500);
  for (const [f, amt] of [["f1", 1500], ["f2", 1500]] as const) {
    const p = await B.startPledge(b.id, f, amt);
    await B.confirmPledge(p.id, f);
  }
  return B.getBounty(b.id);
}

describe("full lifecycle", () => {
  it("pays on proof, holds back, pays the rest after the recheck, and the ledger verifies", async () => {
    const b0 = await fundedBounty();
    expect(b0.status).toBe("funded");
    expect(() => B.claim(b0.id, "f1")).toThrow(/pledged/);
    B.claim(b0.id, "doer");
    await B.addPhoto({ bounty_id: b0.id, user_id: "doer", kind: "before", image: await img(2), ...here });
    await B.addPhoto({ bounty_id: b0.id, user_id: "doer", kind: "after", image: await img(3), ...here });
    const b1 = await B.submitProof(b0.id, "doer");
    expect(b1.status).toBe("paid");
    const ps = B.pledgesFor(b0.id);
    expect(ps.reduce((s, p) => s + p.captured_cents, 0)).toBe(2500); // goal, not the 3000 pledged
    expect(B.payoutsFor(b0.id).map((p) => p.amount_cents)).toEqual([2250]);

    await expect(B.submitRecheck(b0.id, "nb", { image: await img(4), ...here })).rejects.toThrow(/opens on/);
    clock.advance(7);
    const b2 = await B.submitRecheck(b0.id, "nb", { image: await img(4), ...here });
    expect(b2.status).toBe("closed");
    expect(B.payoutsFor(b0.id).map((p) => p.amount_cents)).toEqual([2250, 250]);
    expect(verify().ok).toBe(true);
  });

  it("re-running a release never pays twice", async () => {
    const b = await fundedBounty();
    B.claim(b.id, "doer");
    await B.addPhoto({ bounty_id: b.id, user_id: "doer", kind: "before", image: await img(20), ...here });
    await B.addPhoto({ bounty_id: b.id, user_id: "doer", kind: "after", image: await img(21), ...here });
    await B.submitProof(b.id, "doer");
    await B.releaseProofStage(b.id);
    expect(B.payoutsFor(b.id).length).toBe(1);
  });

  it("a reused photo goes to the funders' vote, and a refund vote charges nobody", async () => {
    const b = await fundedBounty();
    B.claim(b.id, "doer");
    await B.addPhoto({ bounty_id: b.id, user_id: "doer", kind: "before", image: await img(2), ...here }); // same image as the first test
    await B.addPhoto({ bounty_id: b.id, user_id: "doer", kind: "after", image: await img(31), ...here });
    const v = await B.submitProof(b.id, "doer");
    expect(v.status).toBe("vote");
    await B.vote(b.id, "f1", "refund");
    expect(B.getBounty(b.id).status).toBe("vote"); // half the money is not a majority
    await B.vote(b.id, "f2", "refund");
    const done = B.getBounty(b.id);
    expect(done.status).toBe("closed");
    expect(B.pledgesFor(b.id).every((p) => p.status === "voided" && p.captured_cents === 0)).toBe(true);
    expect(B.payoutsFor(b.id)).toEqual([]);
  });

  it("an unfinished bounty expires and every hold is voided", async () => {
    const b = await fundedBounty();
    clock.advance(22);
    await B.tick();
    expect(B.getBounty(b.id).status).toBe("expired");
    expect(B.pledgesFor(b.id).every((p) => p.status === "voided")).toBe(true);
  });

  it("hazardous reports are referred, not priced", async () => {
    const b = await B.reportProblem({ reporter_id: "rep", text: "Live electric wire hanging from the pole", photo: null, area: "Canal Road", ...here });
    expect(b.status).toBe("referred");
    expect(() => B.publish(b.id, "rep")).toThrow();
  });

  it("tampering with any ledger entry is detected", () => {
    const all = entries();
    const tampered = all.map((e, i) => (i === 3 ? { ...e, data: { ...e.data, amount_cents: 999999 } } : e));
    expect(verify(tampered).ok).toBe(false);
    expect(verify(tampered).broken_at).toBe(all[3].seq);
  });
});
