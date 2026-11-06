export type BountyStatus =
  | "draft" // AI has written it, the reporter hasn't published
  | "funding" // open for pledges
  | "funded" // pledges cover the goal; open to claim
  | "claimed" // a doer has it; before photo taken
  | "checking" // after photo in; AI and rules running
  | "objection_window" // checks passed; funders can object before capture
  | "needs_neighbour" // checks passed; large bounty waits for a neighbour's confirmation
  | "vote" // AI unsure or failed; funders decide, doer can add photos
  | "paid" // proof stage paid; held-back share waits for the recheck
  | "recheck_vote" // recheck didn't clearly pass; funders decide on the held-back share
  | "closed" // everything settled
  | "expired" // nobody finished in time; holds voided
  | "referred"; // hazardous: turned into a council report, never priced

export type JobType = "litter" | "drain" | "paint" | "repair" | "greenery" | "other";
export type Skill = "basic" | "semi" | "skilled";

export interface ChecklistItem {
  id: string;
  text: string; // what the after photo must show
}

export interface Bounty {
  id: string;
  title: string;
  report_text: string;
  area: string;
  lat: number;
  lng: number;
  job_type: JobType;
  skill: Skill;
  est_hours: number;
  materials_cents: number;
  hazard: string | null;
  checklist: ChecklistItem[];
  price_low_cents: number;
  price_high_cents: number;
  goal_cents: number;
  holdback_pct: number;
  pricing_notes: string[];
  status: BountyStatus;
  reporter_id: string;
  doer_id: string | null;
  claimed_at: string | null;
  deadline: string;
  project_id: string | null;
  depends_on: string[];
  start_date: string;
  end_date: string;
  created_at: string;
  window_ends_at: string | null;
  recheck_due_at: string | null;
}

export type PledgeStatus = "created" | "authorized" | "captured" | "voided" | "refunded" | "expired";

export interface Pledge {
  id: string;
  bounty_id: string;
  funder_id: string;
  amount_cents: number;
  order_id: string;
  authorization_id: string | null;
  auth_expires_at: string | null;
  status: PledgeStatus;
  captured_cents: number;
  capture_id: string | null;
  refunded_cents: number;
  created_at: string;
}

export interface User {
  id: string;
  name: string;
  paypal_email: string;
  completed_rechecks: number;
}

export type PhotoKind = "report" | "before" | "after" | "recheck" | "confirm";

export interface Photo {
  id: string;
  bounty_id: string;
  user_id: string;
  kind: PhotoKind;
  path: string;
  dhash: string;
  lat: number | null;
  lng: number | null;
  accuracy: number | null;
  live_capture: boolean;
  taken_at: string;
}

export interface CriterionVerdict {
  id: string;
  pass: boolean;
  confidence: number; // 0..1
  reason: string;
}

export interface ProofVerdict {
  same_place: { pass: boolean; confidence: number; reason: string };
  criteria: CriterionVerdict[];
  staged_suspected: boolean;
  staged_reason: string;
  instructions_in_image: boolean; // text in a photo trying to steer the check; always ignored, always flagged
  summary: string;
  model: string;
}

export interface RecheckVerdict {
  still_fixed: boolean;
  confidence: number;
  reason: string;
  same_place: boolean;
  model: string;
}

export interface FraudFlag {
  code:
    | "reused_photo"
    | "no_visible_change"
    | "location_far"
    | "location_missing"
    | "not_live_capture"
    | "instructions_in_image"
    | "staged_suspected"
    | "repeat_pair";
  detail: string;
  blocking: boolean;
}
