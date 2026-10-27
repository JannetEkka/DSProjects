import type { Undertone } from './color';

/** Concerns we ask YouCam Skin Analysis for (SD set, 12 concerns = 14 units). */
export const CONCERNS = [
  'moisture',
  'oiliness',
  'pore',
  'texture',
  'redness',
  'acne',
  'radiance',
  'dark_circle_v2',
  'age_spot',
  'wrinkle',
  'firmness',
  'skin_type',
] as const;
export type Concern = (typeof CONCERNS)[number];
export type ScoredConcern = Exclude<Concern, 'skin_type'>;

export type SkinTypeLabel =
  | 'Normal'
  | 'Oily'
  | 'Dry'
  | 'Combination'
  | 'Redness'
  | 'Dry & Redness'
  | 'Oily & Redness'
  | 'Combination & Redness';

/** One shopper's counter scan, normalised from the two YouCam calls. */
export interface Scan {
  id: string;
  source: 'sample' | 'live' | 'fixture';
  /** YouCam ui_score, 1–100, higher is better. */
  scores: Partial<Record<ScoredConcern, number>>;
  skinType: { whole?: SkinTypeLabel; tZone?: SkinTypeLabel; uZone?: SkinTypeLabel };
  /** From the Facial Color Tones Analyzer. */
  tone: {
    skin: string;
    lip?: string;
    eye?: string;
    eyeName?: string;
    hair?: string;
    hairName?: string;
  };
  /** Combined mask image from Skin Analysis, if any. */
  maskUrl?: string;
}

export type Category =
  | 'foundation'
  | 'concealer'
  | 'primer'
  | 'highlighter'
  | 'blush'
  | 'lip_color'
  | 'moisturiser'
  | 'cleanser'
  | 'serum'
  | 'sunscreen';

export type Finish = 'matte' | 'satin' | 'dewy' | 'shimmer' | 'gloss' | 'cream';

export type Trait =
  | 'mattifying'
  | 'oil_control'
  | 'rich'
  | 'gel'
  | 'hydrating'
  | 'glow'
  | 'fragrance'
  | 'fragrance_free'
  | 'exfoliating'
  | 'foaming'
  | 'cream_cleanser'
  | 'non_comedogenic'
  | 'long_wear'
  | 'spf';

export interface Product {
  id: string;
  brand: string;
  name: string;
  category: Category;
  /** Price in rupees. */
  price: number;
  finish?: Finish;
  shade?: { name: string; hex: string; undertone: Undertone };
  traits: Trait[];
}

export type Verdict = 'keep' | 'swap' | 'skip';

export interface Reason {
  /** Which part of the scan this reason rests on, shown as a chip. */
  basis: string;
  text: string;
  /** Pushes towards this verdict. 'good' reasons support keeping. */
  weight: 'good' | 'swap' | 'skip';
}

export interface ItemCheck {
  product: Product;
  where: 'cart' | 'home';
  verdict: Verdict;
  reasons: Reason[];
  swapTo?: Product;
  /** Shade distance (CIEDE2000) to the scanned skin, for base products. */
  shadeDelta?: number;
}

export interface BasketCheck {
  items: ItemCheck[];
  missing: { category: Category; text: string; suggestion?: Product }[];
  /** Rupees not spent on skipped cart items, less the price difference of swaps. */
  savings: number;
}
