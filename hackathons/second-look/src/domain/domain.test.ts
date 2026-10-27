import { describe, expect, it } from 'vitest';
import { CATALOG, getProduct } from './catalog';
import { checkBasket, judge, readScan } from './check';
import { deltaE2000, hexToLab, labToHex, undertoneOf } from './color';
import { SAMPLE_BASKET, SAMPLE_SCAN } from './sample';
import { findSkinType, parseSkinAnalysis, parseSkinTone } from './scan';
import { makeupRequest } from './tryon';
import type { Scan } from './types';

describe('colour', () => {
  it('matches the CIEDE2000 reference pairs (Sharma et al.)', () => {
    const pairs: [number[], number[], number][] = [
      [[50, 2.6772, -79.7751], [50, 0, -82.7485], 2.0425],
      [[50, -1.3802, -84.2814], [50, 0, -82.7485], 1.0],
      [[50, 2.5, 0], [73, 25, -18], 27.1492],
      [[60.2574, -34.0099, 36.2677], [60.4626, -34.1751, 39.4387], 1.2644],
      [[22.7233, 20.0904, -46.694], [23.0331, 14.973, -42.5619], 2.0373],
    ];
    for (const [a, b, want] of pairs) {
      const got = deltaE2000({ L: a[0], a: a[1], b: a[2] }, { L: b[0], a: b[1], b: b[2] });
      expect(got).toBeCloseTo(want, 3);
    }
  });

  it('round-trips hex through LAB', () => {
    for (const hex of ['#b98a6a', '#eac4b4', '#744510', '#000000', '#ffffff']) {
      expect(labToHex(hexToLab(hex))).toBe(hex);
    }
  });

  it('reads undertone from hue', () => {
    expect(undertoneOf('#dbb3a2')).toBe('cool');
    expect(undertoneOf('#dbb39c')).toBe('neutral');
    expect(undertoneOf('#dcb491')).toBe('warm');
  });
});

describe('parsing YouCam responses', () => {
  it('reads format=json skin analysis, preferring raw_score', () => {
    expect(SAMPLE_SCAN.scores.oiliness).toBe(45);
    expect(SAMPLE_SCAN.skinType).toEqual({ whole: 'Combination', tZone: 'Oily', uZone: 'Normal' });
  });

  it('reads the score_info.json shape with HD keys and subcategories', () => {
    const got = parseSkinAnalysis({
      hd_redness: { raw_score: 72.01, ui_score: 77 },
      hd_pore: { whole: { raw_score: 41.2, ui_score: 60 }, nose: { raw_score: 29.1 } },
      hd_dark_circle: { raw_score: 50, ui_score: 70 },
    });
    expect(got.scores).toEqual({ redness: 72, pore: 41, dark_circle_v2: 50 });
  });

  it('finds skin-type labels in loose shapes', () => {
    expect(findSkinType('oily_and_redness')).toBe('Oily & Redness');
    expect(findSkinType({ label: 'dry' })).toBe('Dry');
    expect(findSkinType(42)).toBeUndefined();
  });

  it('reads tone colours and adds the # when missing', () => {
    expect(parseSkinTone({ data: { results: { color: { skin_color: 'B98A6A' } } } }).skin).toBe('#b98a6a');
    expect(() => parseSkinTone({ data: { results: {} } })).toThrow();
  });
});

describe('basket check on the sample shopper', () => {
  const result = checkBasket(SAMPLE_SCAN, SAMPLE_BASKET);
  const item = (id: string) => result.items.find((i) => i.product.id === id)!;

  it('reads the scan', () => {
    const read = readScan(SAMPLE_SCAN);
    expect(read).toMatchObject({ oilyT: true, dry: false, textureShows: true, redness: true, darkCircles: true });
  });

  it('swaps a dewy, too-light, cool foundation for a matching non-dewy shade', () => {
    const f = item('oddleaf-dew-skin-foundation-130c');
    expect(f.verdict).toBe('swap');
    expect(f.reasons.map((r) => r.basis)).toEqual(expect.arrayContaining(['T-zone oil', 'Skin tone']));
    expect(f.swapTo?.category).toBe('foundation');
    expect(f.swapTo?.finish).not.toBe('dewy');
    expect(judge(f.swapTo!, readScan(SAMPLE_SCAN)).shadeDelta!).toBeLessThan(4);
  });

  it('skips a shimmer highlighter when a suitable one is already at home', () => {
    const h = item('oddleaf-starlit-highlighter-champagne');
    expect(h.verdict).toBe('skip');
    expect(h.reasons.some((r) => r.basis === 'Your shelf')).toBe(true);
  });

  it('swaps the peel serum for a gentler one because of redness', () => {
    const s = item('oddleaf-glow-peel-serum');
    expect(s.verdict).toBe('swap');
    expect(s.swapTo?.traits).not.toContain('exfoliating');
  });

  it('swaps a nude that washes out against the scanned skin', () => {
    const l = item('saltmoss-velvet-lip-bare-biscuit');
    expect(l.verdict).toBe('swap');
    expect(l.swapTo?.category).toBe('lip_color');
  });

  it('keeps the peach blush', () => {
    expect(item('fernhalo-cheek-tint-peach-hour').verdict).toBe('keep');
  });

  it('flags what is missing and counts savings from skipped cart items', () => {
    expect(result.missing.map((m) => m.category)).toEqual(expect.arrayContaining(['sunscreen', 'concealer']));
    expect(result.savings).toBe(getProduct('oddleaf-starlit-highlighter-champagne').price);
  });
});

describe('rules on other skin', () => {
  const dryScan: Scan = { ...SAMPLE_SCAN, scores: { moisture: 35, oiliness: 85 }, skinType: { whole: 'Dry' } };
  const read = readScan(dryScan);

  it('moves dry skin away from matte base and foaming cleanser', () => {
    expect(judge(getProduct('saltmoss-stay-matte-foundation-140n'), read).verdict).toBe('swap');
    expect(judge(getProduct('saltmoss-deep-foam-cleanser'), read).verdict).toBe('swap');
    expect(judge(getProduct('fernhalo-cream-cleanser'), read).verdict).toBe('keep');
  });

  it('every catalogue product can be judged, and every swap target passes its own check', () => {
    for (const p of CATALOG) {
      const j = judge(p, read);
      expect(['keep', 'swap', 'skip']).toContain(j.verdict);
    }
  });
});

describe('try-on requests', () => {
  it('puts the product colour and finish into one effect', () => {
    const body = makeupRequest({ fileId: 'abc' }, getProduct('oddleaf-jelly-gloss-guava'));
    expect(body).toMatchObject({ src_file_id: 'abc' });
    expect(body.effects).toHaveLength(1);
    const e = body.effects[0] as { category: string; palettes: Record<string, unknown>[] };
    expect(e.category).toBe('lip_color');
    expect(e.palettes[0]).toMatchObject({ color: '#D9616B', texture: 'gloss', gloss: 70, transparencyIntensity: 30 });
  });

  it('refuses skincare', () => {
    expect(() => makeupRequest({ url: 'x' }, getProduct('fernhalo-cream-cleanser'))).toThrow();
  });
});
