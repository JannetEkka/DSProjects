// Area health: what the bounties themselves prove (real), plus neighbourhood signals that a live
// deployment would collect with one-tap questions. Those are SAMPLE values in this demo and are labelled so.

import { listBounties, pledgesFor, payoutsFor } from "./bounties.ts";

export function areaHealth() {
  const areas = new Map<string, ReturnType<typeof listBounties>>();
  for (const b of listBounties()) areas.set(b.area, [...(areas.get(b.area) ?? []), b]);
  return [...areas.entries()].map(([area, bs]) => {
    const fixed = bs.filter((b) => b.status === "paid" || b.status === "closed");
    const rechecked = bs.filter((b) => b.status === "closed");
    return {
      area,
      measured: {
        bounties: bs.length,
        fixes_paid: fixed.length,
        rechecks_passed: rechecked.length,
        pledged_cents: bs.flatMap((b) => pledgesFor(b.id)).filter((p) => p.status !== "voided").reduce((s, p) => s + p.amount_cents, 0),
        paid_to_doers_cents: bs.flatMap((b) => payoutsFor(b.id)).reduce((s, p) => s + p.amount_cents, 0),
        referred_to_council: bs.filter((b) => b.status === "referred").length,
      },
      sample: {
        label: "SAMPLE DATA: shows what a live deployment would track; not measured",
        weeks: ["W1", "W2", "W3", "W4", "W5", "W6"],
        still_clean_pct: [null, 60, 70, 75, 80, 85],
        neighbours_walking_here_per_week: [12, 15, 21, 26, 30, 34],
        mosquito_reports: [9, 8, 5, 4, 2, 2],
      },
    };
  });
}
