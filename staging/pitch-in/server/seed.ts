// Sample neighbourhood for the demo. Everything seeded here is marked "sample" in the ledger and the UI.
// Money only ever moves through the live flows, never through seeding.

import { clock } from "./clock.ts";
import { db } from "./db.ts";
import { record } from "./ledger.ts";
import { HOLDBACK_PCT, suggestPrice } from "./pricing.ts";
import type { Bounty, JobType, Skill } from "./types.ts";

const PEOPLE = [
  ["u_asha", "Asha (reports problems)", "SANDBOX_REPORTER"],
  ["u_ben", "Ben (funder)", "SANDBOX_FUNDER_1"],
  ["u_chen", "Chen (funder)", "SANDBOX_FUNDER_2"],
  ["u_dev", "Dev (does the jobs)", "SANDBOX_DOER"],
  ["u_esi", "Esi (neighbour who rechecks)", "SANDBOX_NEIGHBOUR"],
] as const;

interface Seed {
  id: string;
  title: string;
  report: string;
  job: JobType;
  skill: Skill;
  hours: number;
  materials: number;
  checklist: [string, string][];
  project?: string;
  depends?: string[];
  startDay: number;
  days: number;
  dLat: number;
  dLng: number;
}

const BASE = { lat: 12.9719, lng: 77.6412, area: "Lakeview Lane" };

const SEEDS: Seed[] = [
  { id: "b_canal", title: "Clear litter along the canal footpath", report: "The footpath by the canal between the bus stop and the bridge is covered in plastic and wrappers. People walk on the road instead.", job: "litter", skill: "basic", hours: 1.5, materials: 300, checklist: [["path", "No loose litter on the footpath between the bus stop and the bridge"], ["bags", "Filled bags are tied and left at the collection point, not on the path"]], startDay: 0, days: 14, dLat: 0.0004, dLng: 0.0002 },
  { id: "b_drain", title: "Unblock the drain outside the school gate", report: "The drain grate outside the school gate is choked with leaves and silt. Water stands there for days after rain and mosquitoes breed.", job: "drain", skill: "semi", hours: 2, materials: 0, checklist: [["grate", "The grate is clear of leaves and silt"], ["water", "No standing water around the grate"]], startDay: 0, days: 10, dLat: -0.0003, dLng: 0.0005 },
  { id: "b_bench", title: "Fix the broken slat on the park bench", report: "One slat on the bench near the swings is cracked and sticks up. Older people can't sit there.", job: "repair", skill: "skilled", hours: 1.5, materials: 900, checklist: [["slat", "The cracked slat is replaced and level with the others"], ["fixings", "No protruding screws or splinters"]], startDay: 1, days: 14, dLat: 0.0006, dLng: -0.0004 },
  // A bigger project split into dependent bounties (shown on the Gantt plan).
  { id: "b_pond1", title: "Pond path: clear rubbish from the bank", report: "Project: restore the path round the pond. Step 1, clear rubbish from the bank.", job: "litter", skill: "basic", hours: 3, materials: 400, checklist: [["bank", "No rubbish on the bank along the path"]], project: "p_pond", startDay: 0, days: 7, dLat: -0.0008, dLng: -0.0006 },
  { id: "b_pond2", title: "Pond path: cut back overgrown weeds", report: "Project: restore the path round the pond. Step 2, cut back weeds so the path is walkable.", job: "greenery", skill: "basic", hours: 3, materials: 0, checklist: [["path", "The path is clear of weeds at full width"]], project: "p_pond", depends: ["b_pond1"], startDay: 7, days: 7, dLat: -0.0009, dLng: -0.0005 },
  { id: "b_pond3", title: "Pond path: repaint the railing", report: "Project: restore the path round the pond. Step 3, scrape and repaint the rusty railing.", job: "paint", skill: "semi", hours: 4, materials: 1800, checklist: [["paint", "The railing is evenly painted with no rust showing"], ["clean", "No paint drips on the path"]], project: "p_pond", depends: ["b_pond2"], startDay: 14, days: 10, dLat: -0.001, dLng: -0.0004 },
  { id: "b_pond4", title: "Pond path: plant shade saplings", report: "Project: restore the path round the pond. Step 4, plant four saplings with guards.", job: "greenery", skill: "basic", hours: 2.5, materials: 2400, checklist: [["saplings", "Four saplings planted with guards around them"]], project: "p_pond", depends: ["b_pond2"], startDay: 14, days: 10, dLat: -0.0011, dLng: -0.0003 },
];

export function seed() {
  const n = (db.prepare("SELECT COUNT(*) AS n FROM users").get() as { n: number }).n;
  if (n > 0) return;
  const addUser = db.prepare("INSERT INTO users (id, name, paypal_email) VALUES (?, ?, ?)");
  for (const [id, name, envKey] of PEOPLE) addUser.run(id, name, process.env[`PAYPAL_${envKey}_EMAIL`] ?? `${id.slice(2)}@pitchin.example`);
  const now = clock.now().getTime();
  for (const s of SEEDS) {
    const price = suggestPrice({ est_hours: s.hours, skill: s.skill, materials_cents: s.materials, urgent: s.job === "drain", area: "default" });
    const start = new Date(now + s.startDay * 86_400_000).toISOString();
    const end = new Date(now + (s.startDay + s.days) * 86_400_000).toISOString();
    const b: Bounty = {
      id: s.id, title: s.title, report_text: s.report, area: BASE.area, lat: BASE.lat + s.dLat, lng: BASE.lng + s.dLng,
      job_type: s.job, skill: s.skill, est_hours: s.hours, materials_cents: s.materials, hazard: null,
      checklist: s.checklist.map(([id, text]) => ({ id, text })),
      price_low_cents: price.low_cents, price_high_cents: price.high_cents, goal_cents: price.goal_cents,
      holdback_pct: HOLDBACK_PCT[s.job], pricing_notes: price.notes, status: "funding", reporter_id: "u_asha",
      doer_id: null, claimed_at: null, deadline: new Date(now + 21 * 86_400_000).toISOString(), project_id: s.project ?? null,
      depends_on: s.depends ?? [], start_date: start, end_date: end, created_at: new Date(now - (SEEDS.length - SEEDS.indexOf(s)) * 60_000).toISOString(),
      window_ends_at: null, recheck_due_at: null,
    };
    db.prepare("INSERT INTO bounties (id, data, status, created_at) VALUES (?, ?, ?, ?)").run(b.id, JSON.stringify(b), b.status, b.created_at);
    record(b.id, "bounty.seeded", { sample: true, goal_cents: b.goal_cents, checklist: b.checklist, note: "Sample bounty for the demo; no money has moved." });
  }
}
