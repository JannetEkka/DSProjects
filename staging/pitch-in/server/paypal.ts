// PayPal REST client (sandbox only), plus a stand-in with the same interface for running without keys.
// Every POST carries a PayPal-Request-Id, so a retried call can never charge or pay twice.

import { randomUUID } from "node:crypto";
import { config } from "./config.ts";
import { clock } from "./clock.ts";

const money = (cents: number) => ({ currency_code: config.paypal.currency, value: (cents / 100).toFixed(2) });
export const toCents = (value: string) => Math.round(Number(value) * 100);

export interface Authorization {
  id: string;
  status: string; // CREATED | CAPTURED | PARTIALLY_CAPTURED | VOIDED | EXPIRED ...
  amount_cents: number;
  expires_at: string;
}
export interface Capture {
  id: string;
  status: string;
  amount_cents: number;
}
export interface PayoutResult {
  payout_batch_id: string;
  status: string;
}

export interface PayPalApi {
  mode: "sandbox" | "mock";
  createOrder(p: { amount_cents: number; bounty_id: string; pledge_id: string; description: string }, requestId: string): Promise<{ id: string; status: string }>;
  getOrder(id: string): Promise<{ id: string; status: string; amount_cents: number; custom_id?: string; payer_email?: string }>;
  authorizeOrder(orderId: string, requestId: string): Promise<Authorization>;
  getAuthorization(id: string): Promise<Authorization>;
  captureAuthorization(id: string, amount_cents: number, final: boolean, requestId: string, invoiceId: string): Promise<Capture>;
  voidAuthorization(id: string, requestId: string): Promise<void>;
  reauthorize(id: string, amount_cents: number, requestId: string): Promise<Authorization>;
  refundCapture(captureId: string, amount_cents: number, requestId: string, note: string): Promise<{ id: string; status: string }>;
  createPayout(batchId: string, item: { email: string; amount_cents: number; note: string; item_id: string }): Promise<PayoutResult>;
  getPayout(paypalBatchId: string): Promise<{ status: string; items: { transaction_status: string; payout_item_id: string }[] }>;
  verifyWebhook(headers: Record<string, string | undefined>, body: unknown): Promise<boolean>;
}

// ---------------- real sandbox client ----------------

class SandboxPayPal implements PayPalApi {
  mode = "sandbox" as const;
  private token: { value: string; expires: number } | null = null;

  private async accessToken(): Promise<string> {
    if (this.token && this.token.expires > Date.now() + 60_000) return this.token.value;
    const res = await fetch(`${config.paypal.base}/v1/oauth2/token`, {
      method: "POST",
      headers: {
        Authorization: `Basic ${Buffer.from(`${config.paypal.clientId}:${config.paypal.clientSecret}`).toString("base64")}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
    });
    if (!res.ok) throw new PayPalError("oauth", res.status, await res.text());
    const j = (await res.json()) as { access_token: string; expires_in: number };
    this.token = { value: j.access_token, expires: Date.now() + j.expires_in * 1000 };
    return j.access_token;
  }

  private async call<T>(method: "GET" | "POST", path: string, body?: unknown, requestId?: string): Promise<T> {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${await this.accessToken()}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
    };
    if (requestId) headers["PayPal-Request-Id"] = requestId;
    const res = await fetch(`${config.paypal.base}${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    const text = await res.text();
    if (!res.ok) throw new PayPalError(path, res.status, text);
    return (text ? JSON.parse(text) : {}) as T;
  }

  async createOrder(p: { amount_cents: number; bounty_id: string; pledge_id: string; description: string }, requestId: string) {
    const o = await this.call<{ id: string; status: string }>(
      "POST",
      "/v2/checkout/orders",
      {
        intent: "AUTHORIZE",
        purchase_units: [{ reference_id: p.pledge_id, custom_id: p.bounty_id, description: p.description.slice(0, 127), amount: money(p.amount_cents) }],
        payment_source: {
          paypal: { experience_context: { shipping_preference: "NO_SHIPPING", user_action: "CONTINUE", brand_name: "Pitch In (sandbox)" } },
        },
      },
      requestId,
    );
    return { id: o.id, status: o.status };
  }

  async getOrder(id: string) {
    const o = await this.call<any>("GET", `/v2/checkout/orders/${id}`);
    const pu = o.purchase_units?.[0];
    return { id: o.id, status: o.status, amount_cents: toCents(pu?.amount?.value ?? "0"), custom_id: pu?.custom_id, payer_email: o.payer?.email_address };
  }

  async authorizeOrder(orderId: string, requestId: string): Promise<Authorization> {
    const o = await this.call<any>("POST", `/v2/checkout/orders/${orderId}/authorize`, {}, requestId);
    const a = o.purchase_units?.[0]?.payments?.authorizations?.[0];
    if (!a) throw new PayPalError("authorize", 500, "no authorization in response");
    return { id: a.id, status: a.status, amount_cents: toCents(a.amount.value), expires_at: a.expiration_time };
  }

  async getAuthorization(id: string): Promise<Authorization> {
    const a = await this.call<any>("GET", `/v2/payments/authorizations/${id}`);
    return { id: a.id, status: a.status, amount_cents: toCents(a.amount.value), expires_at: a.expiration_time };
  }

  async captureAuthorization(id: string, amount_cents: number, final: boolean, requestId: string, invoiceId: string): Promise<Capture> {
    const c = await this.call<any>("POST", `/v2/payments/authorizations/${id}/capture`, { amount: money(amount_cents), final_capture: final, invoice_id: invoiceId }, requestId);
    return { id: c.id, status: c.status, amount_cents: toCents(c.amount?.value ?? (amount_cents / 100).toString()) };
  }

  async voidAuthorization(id: string, requestId: string) {
    await this.call("POST", `/v2/payments/authorizations/${id}/void`, undefined, requestId);
  }

  async reauthorize(id: string, amount_cents: number, requestId: string): Promise<Authorization> {
    const a = await this.call<any>("POST", `/v2/payments/authorizations/${id}/reauthorize`, { amount: money(amount_cents) }, requestId);
    return { id: a.id, status: a.status, amount_cents: toCents(a.amount?.value ?? "0"), expires_at: a.expiration_time };
  }

  async refundCapture(captureId: string, amount_cents: number, requestId: string, note: string) {
    const r = await this.call<any>("POST", `/v2/payments/captures/${captureId}/refund`, { amount: money(amount_cents), note_to_payer: note.slice(0, 255) }, requestId);
    return { id: r.id, status: r.status };
  }

  async createPayout(batchId: string, item: { email: string; amount_cents: number; note: string; item_id: string }): Promise<PayoutResult> {
    const r = await this.call<any>("POST", "/v1/payments/payouts", {
      sender_batch_header: { sender_batch_id: batchId, email_subject: "You've been paid for a Pitch In fix", email_message: item.note.slice(0, 1000) },
      items: [
        {
          recipient_type: "EMAIL",
          amount: { value: (item.amount_cents / 100).toFixed(2), currency: config.paypal.currency },
          receiver: item.email,
          note: item.note.slice(0, 4000),
          sender_item_id: item.item_id,
        },
      ],
    }, batchId);
    return { payout_batch_id: r.batch_header.payout_batch_id, status: r.batch_header.batch_status };
  }

  async getPayout(paypalBatchId: string) {
    const r = await this.call<any>("GET", `/v1/payments/payouts/${paypalBatchId}`);
    return { status: r.batch_header.batch_status, items: (r.items ?? []).map((i: any) => ({ transaction_status: i.transaction_status, payout_item_id: i.payout_item_id })) };
  }

  async verifyWebhook(headers: Record<string, string | undefined>, body: unknown): Promise<boolean> {
    if (!config.paypal.webhookId) return false;
    const r = await this.call<{ verification_status: string }>("POST", "/v1/notifications/verify-webhook-signature", {
      auth_algo: headers["paypal-auth-algo"],
      cert_url: headers["paypal-cert-url"],
      transmission_id: headers["paypal-transmission-id"],
      transmission_sig: headers["paypal-transmission-sig"],
      transmission_time: headers["paypal-transmission-time"],
      webhook_id: config.paypal.webhookId,
      webhook_event: body,
    });
    return r.verification_status === "SUCCESS";
  }
}

export class PayPalError extends Error {
  constructor(public where: string, public status: number, public body: string) {
    super(`PayPal ${where} failed (${status}): ${body.slice(0, 400)}`);
  }
}

// ---------------- stand-in (no keys) ----------------
// Same interface and the same idempotency behaviour, kept in memory. Used for tests and keyless runs.

export class MockPayPal implements PayPalApi {
  mode = "mock" as const;
  orders = new Map<string, { id: string; status: string; amount_cents: number; custom_id: string }>();
  auths = new Map<string, Authorization & { captured: number }>();
  captures = new Map<string, Capture & { refunded: number }>();
  payouts = new Map<string, PayoutResult & { amount_cents: number }>();
  private seen = new Map<string, unknown>();
  private once<T>(requestId: string, fn: () => T): T {
    if (this.seen.has(requestId)) return this.seen.get(requestId) as T;
    const v = fn();
    this.seen.set(requestId, v);
    return v;
  }
  private id(p: string) {
    return `${p}-${randomUUID().slice(0, 8).toUpperCase()}`;
  }
  async createOrder(p: { amount_cents: number; bounty_id: string }, requestId: string) {
    return this.once(requestId, () => {
      const o = { id: this.id("MOCKORDER"), status: "APPROVED", amount_cents: p.amount_cents, custom_id: p.bounty_id };
      this.orders.set(o.id, o);
      return { id: o.id, status: "CREATED" };
    });
  }
  async getOrder(id: string) {
    const o = this.orders.get(id);
    if (!o) throw new PayPalError("getOrder", 404, "no such order");
    return { ...o, payer_email: "sandbox-buyer@example.com" };
  }
  async authorizeOrder(orderId: string, requestId: string) {
    return this.once(requestId, () => {
      const o = this.orders.get(orderId);
      if (!o) throw new PayPalError("authorize", 404, "no such order");
      if (o.status === "COMPLETED") throw new PayPalError("authorize", 422, "ORDER_ALREADY_AUTHORIZED");
      o.status = "COMPLETED";
      const a = { id: this.id("MOCKAUTH"), status: "CREATED", amount_cents: o.amount_cents, expires_at: new Date(clock.now().getTime() + 29 * 86_400_000).toISOString(), captured: 0 };
      this.auths.set(a.id, a);
      return { id: a.id, status: a.status, amount_cents: a.amount_cents, expires_at: a.expires_at };
    });
  }
  async getAuthorization(id: string) {
    const a = this.auths.get(id);
    if (!a) throw new PayPalError("getAuthorization", 404, "no such authorization");
    if (a.status === "CREATED" && new Date(a.expires_at) < clock.now()) a.status = "EXPIRED";
    return { id: a.id, status: a.status, amount_cents: a.amount_cents, expires_at: a.expires_at };
  }
  async captureAuthorization(id: string, amount_cents: number, final: boolean, requestId: string) {
    return this.once(requestId, () => {
      const a = this.auths.get(id);
      if (!a) throw new PayPalError("capture", 404, "no such authorization");
      if (new Date(a.expires_at) < clock.now()) throw new PayPalError("capture", 422, "AUTHORIZATION_EXPIRED");
      if (!["CREATED", "PARTIALLY_CAPTURED"].includes(a.status)) throw new PayPalError("capture", 422, `AUTHORIZATION_ALREADY_${a.status}`);
      if (a.captured + amount_cents > a.amount_cents) throw new PayPalError("capture", 422, "MAX_CAPTURE_AMOUNT_EXCEEDED");
      a.captured += amount_cents;
      a.status = final || a.captured === a.amount_cents ? "CAPTURED" : "PARTIALLY_CAPTURED";
      const c = { id: this.id("MOCKCAP"), status: "COMPLETED", amount_cents, refunded: 0 };
      this.captures.set(c.id, c);
      return { id: c.id, status: c.status, amount_cents };
    });
  }
  async voidAuthorization(id: string, requestId: string) {
    this.once(requestId, () => {
      const a = this.auths.get(id);
      if (!a) throw new PayPalError("void", 404, "no such authorization");
      if (a.status !== "CREATED") throw new PayPalError("void", 422, `CANNOT_VOID_${a.status}`);
      a.status = "VOIDED";
    });
  }
  async reauthorize(id: string, amount_cents: number, requestId: string) {
    return this.once(requestId, () => {
      const a = this.auths.get(id);
      if (!a) throw new PayPalError("reauthorize", 404, "no such authorization");
      const n = { ...a, id: this.id("MOCKAUTH"), amount_cents, status: "CREATED", captured: 0, expires_at: new Date(clock.now().getTime() + 29 * 86_400_000).toISOString() };
      a.status = "VOIDED";
      this.auths.set(n.id, n);
      return { id: n.id, status: n.status, amount_cents, expires_at: n.expires_at };
    });
  }
  async refundCapture(captureId: string, amount_cents: number, requestId: string) {
    return this.once(requestId, () => {
      const c = this.captures.get(captureId);
      if (!c) throw new PayPalError("refund", 404, "no such capture");
      if (c.refunded + amount_cents > c.amount_cents) throw new PayPalError("refund", 422, "REFUND_AMOUNT_EXCEEDED");
      c.refunded += amount_cents;
      return { id: this.id("MOCKREFUND"), status: "COMPLETED" };
    });
  }
  async createPayout(batchId: string, item: { amount_cents: number }) {
    return this.once(batchId, () => {
      const p = { payout_batch_id: this.id("MOCKPAYOUT"), status: "SUCCESS", amount_cents: item.amount_cents };
      this.payouts.set(p.payout_batch_id, p);
      return { payout_batch_id: p.payout_batch_id, status: p.status };
    });
  }
  async getPayout(id: string) {
    const p = this.payouts.get(id);
    return { status: p?.status ?? "DENIED", items: p ? [{ transaction_status: "SUCCESS", payout_item_id: `${id}-1` }] : [] };
  }
  async verifyWebhook() {
    return false;
  }
}

export const paypal: PayPalApi = config.paypal.mode === "sandbox" ? new SandboxPayPal() : new MockPayPal();
