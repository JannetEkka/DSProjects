// The app's API, independent of the host. Cloudflare Pages Functions call handle(); tests call it with fakes.
// Every YouCam result is cached by content hash, and live calls stop while the account is below UNIT_FLOOR.
import { getProduct, TRY_ON_CATEGORIES } from '../domain/catalog';
import { buildScan } from '../domain/scan';
import { SAMPLE_SCAN } from '../domain/sample';
import { makeupRequest } from '../domain/tryon';
import { CONCERNS, type Scan } from '../domain/types';
import { resultImageUrl, YouCam, YouCamError } from './youcam';

export interface Store {
  get(key: string, type: 'json'): Promise<unknown>;
  get(key: string, type: 'arrayBuffer'): Promise<ArrayBuffer | null>;
  put(key: string, value: string | ArrayBuffer, opts?: { expirationTtl?: number; metadata?: unknown }): Promise<void>;
}

export interface Env {
  YOUCAM_HACK_API_KEY?: string;
  YOUCAM_API_BASE?: string;
  /** Live calls stop when the account has fewer units than this. */
  UNIT_FLOOR?: string;
  /** Live scans per visitor per day. */
  LIVE_SCANS_PER_DAY?: string;
  CACHE: Store;
}

const DEFAULT_BASE = 'https://yce-api-01.makeupar.com';
const DAY = 86_400;
const LIVE_TTL = 2 * DAY; // shoppers' selfies and results are dropped after two days

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

async function sha256(data: ArrayBuffer | string): Promise<string> {
  const bytes = typeof data === 'string' ? new TextEncoder().encode(data) : data;
  const h = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(h)].map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 32);
}

function client(env: Env) {
  if (!env.YOUCAM_HACK_API_KEY) return undefined;
  return new YouCam({ apiKey: env.YOUCAM_HACK_API_KEY, baseUrl: env.YOUCAM_API_BASE || DEFAULT_BASE });
}

async function liveAllowed(env: Env, yc: YouCam, cost: number): Promise<{ ok: true } | { ok: false; why: string }> {
  const floor = Number(env.UNIT_FLOOR ?? 150);
  const left = await yc.unitsLeft();
  if (left - cost < floor) return { ok: false, why: `The demo's free API units are reserved (${Math.floor(left)} left). The sample shopper still works.` };
  return { ok: true };
}

async function underDailyLimit(env: Env, who: string): Promise<boolean> {
  const key = `rate:${new Date().toISOString().slice(0, 10)}:${await sha256(who)}`;
  const n = Number((await env.CACHE.get(key, 'json')) ?? 0);
  if (n >= Number(env.LIVE_SCANS_PER_DAY ?? 3)) return false;
  await env.CACHE.put(key, JSON.stringify(n + 1), { expirationTtl: DAY });
  return true;
}

async function ledger(env: Env, entry: Record<string, unknown>) {
  const key = `ledger:${new Date().toISOString()}:${Math.random().toString(36).slice(2, 8)}`;
  await env.CACHE.put(key, JSON.stringify(entry), { expirationTtl: 90 * DAY });
}

interface StoredScan {
  scan: Scan;
  fileId?: string;
  fileIdAt?: number;
  imageKey?: string;
  imageUrl?: string;
}

/** The sample shopper's photo, recorded once with the key (fixtures/sample-*.json). Falls back to synthetic data. */
async function sampleScan(env: Env): Promise<StoredScan> {
  const recorded = (await env.CACHE.get('scan:sample', 'json')) as StoredScan | null;
  return recorded ?? { scan: SAMPLE_SCAN };
}

export async function handle(req: Request, env: Env): Promise<Response> {
  const url = new URL(req.url);
  const path = url.pathname.replace(/^\/api/, '');
  try {
    if (req.method === 'GET' && path === '/status') {
      const yc = client(env);
      if (!yc) return json({ live: false, reason: 'No API key on this deployment; sample shopper only.' });
      const left = await yc.unitsLeft().catch(() => undefined);
      return json({ live: left !== undefined && left > Number(env.UNIT_FLOOR ?? 150) + 34, unitsLeft: left !== undefined ? Math.floor(left) : undefined });
    }

    if (req.method === 'GET' && path === '/scan/sample') {
      const s = await sampleScan(env);
      return json({ scan: s.scan, imageUrl: s.imageUrl });
    }

    if (req.method === 'POST' && path === '/scan') return await scan(req, env);
    if (req.method === 'POST' && path === '/tryon') return await tryOn(req, env);

    const img = /^\/img\/([a-z0-9:_-]+)$/i.exec(path);
    if (req.method === 'GET' && img) {
      const bytes = await env.CACHE.get(`img:${img[1]}`, 'arrayBuffer');
      if (!bytes) return json({ error: 'not found' }, 404);
      return new Response(bytes, { headers: { 'Content-Type': 'image/jpeg', 'Cache-Control': 'private, max-age=86400' } });
    }
    return json({ error: 'not found' }, 404);
  } catch (e) {
    const status = e instanceof YouCamError ? (e.status >= 400 && e.status < 600 ? e.status : 502) : 500;
    return json({ error: e instanceof Error ? e.message : 'unexpected error', code: e instanceof YouCamError ? e.code : undefined }, status);
  }
}

async function scan(req: Request, env: Env): Promise<Response> {
  const yc = client(env);
  if (!yc) return json({ error: 'Live scans need the API key. Use the sample shopper.' }, 503);
  const form = await req.formData();
  const file = form.get('photo') as unknown as File | string | null;
  if (!file || typeof file === 'string') return json({ error: 'photo missing' }, 400);
  const bytes = await file.arrayBuffer();
  if (bytes.byteLength > 8 * 1024 * 1024) return json({ error: 'photo too large' }, 413);
  const type = file.type === 'image/png' ? 'image/png' : 'image/jpeg';

  const hash = await sha256(bytes);
  const cached = (await env.CACHE.get(`scan:${hash}`, 'json')) as StoredScan | null;
  if (cached) return json({ scan: cached.scan, imageUrl: cached.imageUrl, cached: true });

  const cost = 14 + 20;
  const gate = await liveAllowed(env, yc, cost);
  if (!gate.ok) return json({ error: gate.why }, 429);
  if (!(await underDailyLimit(env, req.headers.get('CF-Connecting-IP') ?? 'local')))
    return json({ error: 'Daily live-scan limit reached for this device. The sample shopper still works.' }, 429);

  const fileId = await yc.upload(bytes, type, `selfie.${type === 'image/png' ? 'png' : 'jpg'}`);
  const dst_actions = [...CONCERNS];
  const [skin, tone] = await Promise.all([
    yc.run('skin-analysis', { src_file_id: fileId, dst_actions, format: 'json', miniserver_args: { enable_mask_overlay: true } }),
    yc.run('skin-tone-analysis', { src_file_id: fileId, face_angle_strictness_level: 'medium' }),
  ]);
  const s = buildScan(hash, 'live', skin, tone);
  await env.CACHE.put(`img:selfie-${hash}`, bytes, { expirationTtl: LIVE_TTL });
  const stored: StoredScan = { scan: s, fileId, fileIdAt: Date.now(), imageKey: `selfie-${hash}`, imageUrl: `/api/img/selfie-${hash}` };
  await env.CACHE.put(`scan:${hash}`, JSON.stringify(stored), { expirationTtl: LIVE_TTL });
  await env.CACHE.put(`raw:${hash}`, JSON.stringify({ skin, tone }), { expirationTtl: LIVE_TTL });
  await ledger(env, { kind: 'scan', units: cost, scan: hash });
  return json({ scan: s, imageUrl: stored.imageUrl });
}

async function tryOn(req: Request, env: Env): Promise<Response> {
  const { scanId, productId } = (await req.json()) as { scanId?: string; productId?: string };
  if (!scanId || !productId) return json({ error: 'scanId and productId required' }, 400);
  const product = getProduct(productId);
  if (!TRY_ON_CATEGORIES.includes(product.category)) return json({ error: `${product.category} can't be tried on` }, 400);

  const key = `tryon-${await sha256(`${scanId}|${productId}`)}`;
  if (await env.CACHE.get(`img:${key}`, 'arrayBuffer')) return json({ imageUrl: `/api/img/${key}`, cached: true });

  const stored = scanId === 'sample' ? await sampleScan(env) : ((await env.CACHE.get(`scan:${scanId}`, 'json')) as StoredScan | null);
  if (!stored) return json({ error: 'scan expired; scan again' }, 404);

  const yc = client(env);
  if (!yc) return json({ error: 'Try-on needs the API key on this deployment.' }, 503);
  const gate = await liveAllowed(env, yc, 1);
  if (!gate.ok) return json({ error: gate.why }, 429);

  // File IDs from the File API are short-lived; re-upload the selfie when the old one is stale.
  let fileId = stored.fileId && stored.fileIdAt && Date.now() - stored.fileIdAt < 20 * 60_000 ? stored.fileId : undefined;
  if (!fileId && stored.imageKey) {
    const bytes = await env.CACHE.get(`img:${stored.imageKey}`, 'arrayBuffer');
    if (bytes) fileId = await yc.upload(bytes, 'image/jpeg');
  }
  if (!fileId) return json({ error: 'scan photo expired; scan again' }, 404);

  const body = await yc.run('makeup-vto', makeupRequest({ fileId }, product));
  const out = resultImageUrl(body);
  if (!out) return json({ error: 'try-on returned no image' }, 502);
  const img = await fetch(out);
  if (!img.ok) return json({ error: 'could not fetch try-on image' }, 502);
  const ttl = scanId === 'sample' ? undefined : LIVE_TTL;
  await env.CACHE.put(`img:${key}`, await img.arrayBuffer(), ttl ? { expirationTtl: ttl } : undefined);
  await ledger(env, { kind: 'tryon', units: 1, scan: scanId, product: productId });
  return json({ imageUrl: `/api/img/${key}` });
}
