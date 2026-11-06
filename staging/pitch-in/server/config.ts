// Runtime configuration. Pitch In only ever talks to the PayPal sandbox:
// it refuses to start if anything points it at live PayPal.

const SANDBOX_BASE = "https://api-m.sandbox.paypal.com";

const base = process.env.PAYPAL_BASE_URL ?? SANDBOX_BASE;
if (!base.startsWith("https://api-m.sandbox.paypal.com") && !base.startsWith("https://api.sandbox.paypal.com")) {
  throw new Error(`Refusing to start: PAYPAL_BASE_URL (${base}) is not the PayPal sandbox. Pitch In never moves real money.`);
}

const clientId = process.env.PAYPAL_SANDBOX_CLIENT_ID ?? "";
const clientSecret = process.env.PAYPAL_SANDBOX_CLIENT_SECRET ?? "";
const geminiKey = process.env.PAYPAL_HACK_GEMINI_API_KEY ?? "";

export const config = {
  port: Number(process.env.PORT ?? 8080),
  dataDir: process.env.DATA_DIR ?? "data",
  paypal: {
    base,
    clientId,
    clientSecret,
    // Without credentials the app runs against an in-memory stand-in with the same interface.
    mode: clientId && clientSecret ? ("sandbox" as const) : ("mock" as const),
    webhookId: process.env.PAYPAL_WEBHOOK_ID ?? "",
    currency: "USD",
  },
  ai: {
    key: geminiKey,
    model: process.env.GEMINI_MODEL ?? "gemini-2.5-flash",
    mode: geminiKey ? ("gemini" as const) : ("mock" as const),
  },
  // Money limits that the AI cannot change.
  limits: {
    smallBountyCents: 2500, // at or under: paid automatically when every check passes
    largeBountyCents: 10000, // over: also needs a neighbour's on-the-spot confirmation
    objectionWindowHours: 24, // medium and large bounties: funders can object before capture
    doerDailyCapCents: 15000,
    newDoerCapCents: 5000, // until a doer has one bounty that passed its recheck
    minHoldDaysToClaim: 10, // PayPal authorisations last 29 days
    authorizationDays: 29,
    honorDays: 3,
    nearbyMeters: 75,
    maxAccuracyMeters: 60,
    recheckAfterDays: 7,
  },
  demo: process.env.DEMO_MODE !== "0",
};

export type Config = typeof config;
