import express, { type NextFunction, type Request, type Response } from "express";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { z } from "zod";
import { config } from "./config.ts";
import { clock } from "./clock.ts";
import { db } from "./db.ts";
import { entries, record, verify } from "./ledger.ts";
import { paypal } from "./paypal.ts";
import * as B from "./bounties.ts";
import { investigate, listCases } from "./agent.ts";
import { photosFor } from "./photos.ts";
import { seed } from "./seed.ts";
import { tierOf } from "./rules.ts";
import { areaHealth } from "./health.ts";

const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "12mb" }));

// Security headers. The PayPal JS SDK needs its own hosts in the CSP.
app.use((_req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader("X-Frame-Options", "SAMEORIGIN");
  res.setHeader("Permissions-Policy", "camera=(self), geolocation=(self), microphone=()");
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self' https://*.paypal.com https://*.paypalobjects.com; frame-src https://*.paypal.com; img-src 'self' data: blob: https://*.paypal.com https://*.paypalobjects.com; connect-src 'self' https://*.paypal.com; style-src 'self' 'unsafe-inline'",
  );
  next();
});

// Simple per-IP rate limit for writes.
const hits = new Map<string, { n: number; reset: number }>();
app.use("/api", (req, res, next) => {
  if (req.method === "GET") return next();
  const k = req.ip ?? "?";
  const now = Date.now();
  const h = hits.get(k) ?? { n: 0, reset: now + 60_000 };
  if (now > h.reset) Object.assign(h, { n: 0, reset: now + 60_000 });
  h.n++;
  hits.set(k, h);
  if (h.n > 120) return res.status(429).json({ error: "Too many requests; wait a minute." });
  next();
});

// Demo sign-in: pick a neighbour. Production would use Log in with PayPal; see SECURITY.md.
function userId(req: Request): string {
  const c = req.headers.cookie?.match(/(?:^|;\s*)pi_user=([a-z0-9_]+)/)?.[1];
  if (!c) throw new B.Refused(["Choose who you are first."]);
  return B.getUser(c).id;
}

const wrap = (fn: (req: Request, res: Response) => Promise<unknown> | unknown) => async (req: Request, res: Response, next: NextFunction) => {
  try {
    const out = await fn(req, res);
    if (!res.headersSent) res.json(out ?? { ok: true });
  } catch (e) {
    next(e);
  }
};

const photoInput = z.object({
  image: z.string().regex(/^data:image\/(jpeg|png|webp);base64,/),
  lat: z.number().nullable(),
  lng: z.number().nullable(),
  accuracy: z.number().nullable(),
  live_capture: z.boolean(),
});
const toBuf = (dataUrl: string) => Buffer.from(dataUrl.split(",")[1], "base64");

// ---------- session ----------
app.get("/api/config", (_req, res) =>
  res.json({ paypal_mode: paypal.mode, paypal_client_id: config.paypal.clientId, ai_mode: config.ai.mode, ai_model: config.ai.model, demo: config.demo, limits: config.limits, clock_offset_days: clock.offsetDays(), now: clock.iso() }),
);
app.get("/api/users", wrap(() => B.listUsers()));
app.post(
  "/api/session",
  wrap((req, res) => {
    const id = z.object({ user_id: z.string() }).parse(req.body).user_id;
    B.getUser(id);
    res.setHeader("Set-Cookie", `pi_user=${id}; Path=/; HttpOnly; SameSite=Strict${process.env.NODE_ENV === "production" ? "; Secure" : ""}`);
    return { ok: true };
  }),
);
app.get("/api/me", wrap((req) => ({ user: B.getUser(userId(req)), notifications: db.prepare("SELECT * FROM notifications WHERE user_id = ? ORDER BY at DESC LIMIT 30").all(userId(req)) })));

// ---------- bounties ----------
function view(id: string) {
  const b = B.getBounty(id);
  const pledges = B.pledgesFor(id);
  return {
    bounty: b,
    tier: tierOf(b.goal_cents),
    pledges,
    authorized_cents: pledges.filter((p) => p.status === "authorized").reduce((s, p) => s + p.amount_cents, 0),
    captured_cents: pledges.reduce((s, p) => s + p.captured_cents, 0),
    payouts: B.payoutsFor(id),
    photos: photosFor(id).map(({ path: _p, ...p }) => p),
    checks: B.checksFor(id),
    ledger: entries(id),
    votes: db.prepare("SELECT * FROM votes WHERE bounty_id = ?").all(id),
    objections: db.prepare("SELECT * FROM objections WHERE bounty_id = ?").all(id),
  };
}
app.get(
  "/api/bounties",
  wrap(() =>
    B.listBounties().map((b) => {
      const ps = B.pledgesFor(b.id);
      return {
        ...b,
        tier: tierOf(b.goal_cents),
        authorized_cents: ps.filter((p) => p.status === "authorized").reduce((s, p) => s + p.amount_cents, 0),
        captured_cents: ps.reduce((s, p) => s + p.captured_cents, 0),
        paid_cents: B.payoutsFor(b.id).reduce((s, p) => s + p.amount_cents, 0),
        funders: new Set(ps.map((p) => p.funder_id)).size,
        hold_expires_at: ps.filter((p) => p.status === "authorized").map((p) => p.auth_expires_at).sort()[0] ?? null,
      };
    }),
  ),
);
app.get("/api/bounties/:id", wrap((req) => view(String(req.params.id))));
app.post(
  "/api/reports",
  wrap(async (req) => {
    const body = z
      .object({ text: z.string().min(5).max(2000), area: z.string().min(1).max(80), photo: photoInput.nullable(), lat: z.number(), lng: z.number(), project_id: z.string().optional(), depends_on: z.array(z.string()).optional() })
      .parse(req.body);
    return B.reportProblem({
      reporter_id: userId(req),
      text: body.text,
      area: body.area,
      photo: body.photo ? toBuf(body.photo.image) : null,
      lat: body.lat,
      lng: body.lng,
      accuracy: body.photo?.accuracy ?? null,
      live_capture: body.photo?.live_capture ?? false,
      project_id: body.project_id,
      depends_on: body.depends_on,
    });
  }),
);
app.post("/api/bounties/:id/publish", wrap((req) => B.publish(String(req.params.id), userId(req), z.object({ goal_cents: z.number().int().optional() }).parse(req.body).goal_cents)));
app.post(
  "/api/bounties/:id/pledges",
  wrap(async (req) => {
    const { amount_cents, renew_of } = z.object({ amount_cents: z.number().int(), renew_of: z.string().optional() }).parse(req.body);
    const p = await B.startPledge(String(req.params.id), userId(req), amount_cents, renew_of);
    return { pledge_id: p.id, order_id: p.order_id };
  }),
);
app.post("/api/pledges/:id/confirm", wrap((req) => B.confirmPledge(String(req.params.id), userId(req))));
app.post("/api/bounties/:id/claim", wrap((req) => B.claim(String(req.params.id), userId(req))));
app.post(
  "/api/bounties/:id/photos",
  wrap(async (req) => {
    const body = photoInput.extend({ kind: z.enum(["before", "after"]) }).parse(req.body);
    const { path: _p, ...ph } = await B.addPhoto({ bounty_id: String(req.params.id), user_id: userId(req), kind: body.kind, image: toBuf(body.image), lat: body.lat, lng: body.lng, accuracy: body.accuracy, live_capture: body.live_capture });
    return ph;
  }),
);
app.post("/api/bounties/:id/proof", wrap((req) => B.submitProof(String(req.params.id), userId(req))));
app.post("/api/bounties/:id/object", wrap((req) => B.object(String(req.params.id), userId(req), z.object({ reason: z.string().min(3).max(500) }).parse(req.body).reason)));
app.post("/api/bounties/:id/vote", wrap((req) => B.vote(String(req.params.id), userId(req), z.object({ choice: z.enum(["pay", "refund"]) }).parse(req.body).choice)));
app.post(
  "/api/bounties/:id/confirm",
  wrap((req) => {
    const p = photoInput.parse(req.body);
    return B.neighbourConfirm(String(req.params.id), userId(req), { image: toBuf(p.image), lat: p.lat, lng: p.lng, accuracy: p.accuracy, live_capture: p.live_capture });
  }),
);
app.post(
  "/api/bounties/:id/recheck",
  wrap((req) => {
    const p = photoInput.parse(req.body);
    return B.submitRecheck(String(req.params.id), userId(req), { image: toBuf(p.image), lat: p.lat, lng: p.lng, accuracy: p.accuracy, live_capture: p.live_capture });
  }),
);
app.post("/api/bounties/:id/retry-release", wrap((req) => (userId(req), B.releaseProofStage(String(req.params.id)))));
app.get(
  "/api/photos/:id",
  wrap((req, res) => {
    const row = db.prepare("SELECT data FROM photos WHERE id = ?").get(String(req.params.id)) as { data: string } | undefined;
    if (!row) throw new B.Refused(["No such photo."]);
    res.setHeader("Content-Type", "image/jpeg");
    res.setHeader("Cache-Control", "private, max-age=3600");
    res.send(readFileSync(JSON.parse(row.data).path));
  }),
);

// ---------- receipts, support, health ----------
app.get("/api/ledger", wrap(() => entries()));
app.get("/api/ledger/verify", wrap(() => verify()));
app.get("/api/cases", wrap(() => listCases()));
app.post(
  "/api/cases",
  wrap((req) => {
    const b = z.object({ bounty_id: z.string().nullable(), kind: z.string().min(2).max(40), body: z.string().min(5).max(2000) }).parse(req.body);
    return { id: B.openCase(b.bounty_id, userId(req), b.kind, b.body) };
  }),
);
app.post("/api/cases/:id/investigate", wrap((req) => (userId(req), investigate(String(req.params.id)))));
app.post("/api/reconcile", wrap(async () => ({ mismatches: await B.reconcile() })));
app.get("/api/health/areas", wrap(() => areaHealth()));

// Notifications as an RSS feed: Zapier's free "RSS by Zapier" trigger watches it and forwards each item (email, SMS, Slack).
app.get("/api/feed.rss", (_req, res) => {
  const rows = db.prepare("SELECT n.*, u.name FROM notifications n JOIN users u ON u.id = n.user_id ORDER BY at DESC LIMIT 50").all() as {
    id: string;
    name: string;
    bounty_id: string | null;
    text: string;
    at: string;
  }[];
  const esc = (s: string) => s.replace(/[<>&"']/g, (c) => `&#${c.charCodeAt(0)};`);
  res.type("application/rss+xml").send(
    `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Pitch In notifications</title><link>/</link><description>Bounty updates for neighbours</description>${rows
      .map((r) => `<item><guid isPermaLink="false">${r.id}</guid><title>${esc(`To ${r.name}: ${r.text.slice(0, 90)}`)}</title><description>${esc(r.text)}</description><pubDate>${new Date(r.at).toUTCString()}</pubDate></item>`)
      .join("")}</channel></rss>`,
  );
});

// PayPal webhooks: signature verified with PayPal before anything is trusted; then we re-read state from PayPal.
app.post(
  "/api/paypal/webhook",
  wrap(async (req) => {
    const ok = await paypal.verifyWebhook(req.headers as Record<string, string>, req.body);
    record(null, "webhook.received", { event_type: req.body?.event_type ?? null, id: req.body?.id ?? null, verified: ok });
    if (!ok) return { ok: false };
    await B.reconcile();
    return { ok: true };
  }),
);

// ---------- demo controls (clearly labelled in the UI; off when DEMO_MODE=0) ----------
app.post(
  "/api/demo/advance",
  wrap(async (req) => {
    if (!config.demo) throw new B.Refused(["Demo controls are off."]);
    const days = z.object({ days: z.number().min(0).max(30) }).parse(req.body).days;
    clock.advance(days);
    record(null, "demo.clock_advanced", { days, offset_days: clock.offsetDays() });
    return { ticked: await B.tick(), now: clock.iso() };
  }),
);

// ---------- errors ----------
app.use("/api", (err: unknown, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof B.Refused) return res.status(409).json({ error: err.message, reasons: err.reasons });
  if (err instanceof z.ZodError) return res.status(400).json({ error: "Invalid input", issues: err.issues.map((i) => `${i.path.join(".")}: ${i.message}`) });
  console.error(err);
  res.status(500).json({ error: (err as Error).message?.slice(0, 300) ?? "Server error" });
});

// ---------- web app ----------
const dist = join(process.cwd(), "dist");
if (existsSync(dist)) {
  app.use(express.static(dist, { index: false, maxAge: "1h" }));
  app.get(/^(?!\/api).*/, (_req, res) => res.sendFile(join(dist, "index.html")));
}

seed();
setInterval(() => void B.tick().catch((e) => console.error("tick", e)), 60_000);
setInterval(() => void B.reconcile().catch((e) => console.error("reconcile", e)), 6 * 3_600_000);

app.listen(config.port, () => console.log(`Pitch In on :${config.port} · PayPal ${paypal.mode} · AI ${config.ai.mode} (${config.ai.model})`));
