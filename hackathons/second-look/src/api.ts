// Browser side of the API. The YouCam key never reaches the browser; everything goes through /api.
import type { Scan } from './domain/types';

export interface Status {
  live: boolean;
  unitsLeft?: number;
  reason?: string;
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, init);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error ?? `Request failed (${res.status})`);
  return body as T;
}

export const getStatus = () => call<Status>('/status');
export const sampleScan = () => call<{ scan: Scan; imageUrl?: string }>('/scan/sample');

export function scanPhoto(photo: Blob) {
  const form = new FormData();
  form.append('photo', photo, 'selfie.jpg');
  return call<{ scan: Scan; imageUrl?: string }>('/scan', { method: 'POST', body: form });
}

export async function tryOn(scanId: string, productId: string): Promise<string> {
  const r = await call<{ imageUrl: string }>('/tryon', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scanId, productId }),
  });
  return r.imageUrl;
}

/** Fits the photo to what all three YouCam features accept: long side 1080–1900px, short side ≥ 480px, JPEG. */
export async function prepPhoto(file: File): Promise<Blob> {
  const bmp = await createImageBitmap(file);
  const long = Math.max(bmp.width, bmp.height);
  const short = Math.min(bmp.width, bmp.height);
  if (short < 480) throw new Error('That photo is too small. Use one at least 480 pixels on the short side.');
  const scale = Math.min(1, 1900 / long);
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(bmp.width * scale);
  canvas.height = Math.round(bmp.height * scale);
  canvas.getContext('2d')!.drawImage(bmp, 0, 0, canvas.width, canvas.height);
  return new Promise((resolve, reject) => canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('could not read photo'))), 'image/jpeg', 0.9));
}
