// Photo storage and the fraud checks that don't need AI: reused photos, unchanged photos,
// location and live capture. Each check is a signal; none of them pays or blocks money by itself
// except through rules.ts.

import sharp from "sharp";
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { config } from "./config.ts";
import { clock } from "./clock.ts";
import { db, listDocs, newId } from "./db.ts";
import type { Bounty, FraudFlag, Photo, PhotoKind } from "./types.ts";

const PHOTO_DIR = join(config.dataDir, "photos");
mkdirSync(PHOTO_DIR, { recursive: true });

// 64-bit difference hash: robust to resizing and recompression, so a re-uploaded or re-shot copy of a photo still matches.
export async function dhash(img: Buffer): Promise<string> {
  const px = await sharp(img).rotate().grayscale().resize(9, 8, { fit: "fill" }).raw().toBuffer();
  let bits = "";
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) bits += px[y * 9 + x] > px[y * 9 + x + 1] ? "1" : "0";
  return BigInt(`0b${bits}`).toString(16).padStart(16, "0");
}

export function hamming(a: string, b: string): number {
  let x = BigInt(`0x${a}`) ^ BigInt(`0x${b}`);
  let n = 0;
  while (x) {
    n += Number(x & 1n);
    x >>= 1n;
  }
  return n;
}

export function metersBetween(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6_371_000;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

// Re-encode every photo: strips EXIF (including the uploader's exact GPS) and caps the size.
export async function storePhoto(input: {
  bounty_id: string;
  user_id: string;
  kind: PhotoKind;
  image: Buffer;
  lat: number | null;
  lng: number | null;
  accuracy: number | null;
  live_capture: boolean;
}): Promise<Photo> {
  const clean = await sharp(input.image).rotate().resize(1600, 1600, { fit: "inside", withoutEnlargement: true }).jpeg({ quality: 82 }).toBuffer();
  const id = newId("ph");
  const path = join(PHOTO_DIR, `${id}.jpg`);
  writeFileSync(path, clean);
  const photo: Photo = {
    id,
    bounty_id: input.bounty_id,
    user_id: input.user_id,
    kind: input.kind,
    path,
    dhash: await dhash(clean),
    lat: input.lat,
    lng: input.lng,
    accuracy: input.accuracy,
    live_capture: input.live_capture,
    taken_at: clock.iso(), // server time; the phone's own timestamp is never trusted
  };
  db.prepare("INSERT INTO photos (id, bounty_id, kind, data) VALUES (?, ?, ?, ?)").run(id, input.bounty_id, input.kind, JSON.stringify(photo));
  return photo;
}

export function readPhoto(p: Photo): Buffer {
  return readFileSync(p.path);
}

export function photosFor(bountyId: string, kind?: PhotoKind): Photo[] {
  const all = listDocs<Photo>("photos", "bounty_id = ?", bountyId).sort((a, b) => a.taken_at.localeCompare(b.taken_at));
  return kind ? all.filter((p) => p.kind === kind) : all;
}

const REUSE_BITS = 5; // near-identical
const UNCHANGED_BITS = 2; // after photo is essentially the before photo

export function fraudFlags(b: Bounty, photo: Photo, compareTo: Photo | null, allPhotos: Photo[]): FraudFlag[] {
  const flags: FraudFlag[] = [];
  for (const other of allPhotos) {
    if (other.id === photo.id) continue;
    const sameBounty = other.bounty_id === b.id;
    // Within one bounty, the report/before/after are meant to look alike; reuse across bounties or within the same kind is not.
    if ((!sameBounty || other.kind === photo.kind) && hamming(other.dhash, photo.dhash) <= REUSE_BITS) {
      flags.push({
        code: "reused_photo",
        detail: `This photo matches an earlier ${other.kind} photo${sameBounty ? "" : " from another bounty"} (${other.id}).`,
        blocking: true,
      });
      break;
    }
  }
  if (compareTo && hamming(compareTo.dhash, photo.dhash) <= UNCHANGED_BITS)
    flags.push({ code: "no_visible_change", detail: `The ${photo.kind} photo is practically identical to the ${compareTo.kind} photo.`, blocking: true });
  if (photo.lat == null || photo.lng == null) flags.push({ code: "location_missing", detail: "No location came with the photo.", blocking: false });
  else {
    const d = metersBetween(photo.lat, photo.lng, b.lat, b.lng);
    if (d > config.limits.nearbyMeters || (photo.accuracy ?? 999) > config.limits.maxAccuracyMeters)
      flags.push({
        code: "location_far",
        detail: `Taken ${Math.round(d)} m from the bounty (accuracy ±${Math.round(photo.accuracy ?? 0)} m); it must be within ${config.limits.nearbyMeters} m.`,
        blocking: !config.demo,
      });
  }
  if (!photo.live_capture) flags.push({ code: "not_live_capture", detail: "Uploaded from a file, not taken with the in-app camera.", blocking: !config.demo });
  return flags;
}

// Same reporter and doer pairing again and again in one area is a staging signal.
export function repeatPairFlag(b: Bounty, doerId: string, allBounties: Bounty[]): FraudFlag | null {
  const n = allBounties.filter((x) => x.id !== b.id && x.reporter_id === b.reporter_id && x.doer_id === doerId && x.area === b.area).length;
  return n >= 2 ? { code: "repeat_pair", detail: `This reporter and doer have paired on ${n} other bounties in ${b.area}.`, blocking: false } : null;
}
