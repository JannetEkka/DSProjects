// Suggested price. The AI estimates the inputs (hours, skill, materials) from the report and photo;
// this formula, not the AI, turns them into money, so every number can be explained.

import type { JobType, Skill } from "./types.ts";

export const SKILL_MULTIPLIER: Record<Skill, number> = { basic: 1, semi: 1.25, skilled: 1.6 };

// How much of the payment waits for the "still fixed?" recheck. It reflects how much a lasting
// result depends on the doer's work: people litter again whatever the doer did; a bench repair holds or it doesn't.
export const HOLDBACK_PCT: Record<JobType, number> = {
  litter: 10,
  greenery: 15,
  drain: 20,
  paint: 20,
  other: 20,
  repair: 30,
};

// Fair hourly rates per area, in cents. Never below the local minimum wage.
// Sample values for the sandbox demo; a real deployment would load these per city.
export const AREA_RATES: Record<string, { hourly_cents: number; source: string }> = {
  default: { hourly_cents: 1600, source: "sample fair rate (USD) for the sandbox demo" },
};

export interface PriceInput {
  est_hours: number;
  skill: Skill;
  materials_cents: number;
  urgent: boolean;
  area: string;
  similar_paid_cents?: number[]; // what neighbours paid for similar jobs
}

export interface PriceSuggestion {
  low_cents: number;
  high_cents: number;
  goal_cents: number;
  notes: string[];
}

const round50 = (c: number) => Math.round(c / 50) * 50;

export function suggestPrice(i: PriceInput): PriceSuggestion {
  const rate = AREA_RATES[i.area] ?? AREA_RATES.default;
  const hours = Math.min(Math.max(i.est_hours, 0.25), 16);
  const labour = hours * rate.hourly_cents * SKILL_MULTIPLIER[i.skill];
  const urgency = i.urgent ? labour * 0.1 : 0;
  let mid = labour + urgency;
  const notes = [
    `${hours} h × $${(rate.hourly_cents / 100).toFixed(2)}/h (${rate.source})`,
    `× ${SKILL_MULTIPLIER[i.skill]} for ${i.skill} skill`,
  ];
  if (urgency) notes.push("+10% because it's urgent");
  if (i.similar_paid_cents && i.similar_paid_cents.length >= 3) {
    const sorted = [...i.similar_paid_cents].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    // History can pull the price up toward what neighbours have paid, never below the fair-rate floor.
    if (median > mid) {
      mid = (mid + median) / 2;
      notes.push(`nudged up toward the $${(median / 100).toFixed(2)} neighbours paid for similar jobs`);
    }
  }
  const low = round50(mid * 0.9);
  const high = round50(mid * 1.15);
  const goal = round50(mid) + i.materials_cents;
  if (i.materials_cents) notes.push(`+ $${(i.materials_cents / 100).toFixed(2)} materials, paid against a receipt photo`);
  return { low_cents: low + i.materials_cents, high_cents: high + i.materials_cents, goal_cents: goal, notes };
}
