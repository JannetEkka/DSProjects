// The demo store's catalogue. Every brand and product here is made up (hackathon rule: no real trademarks).
import { labToHex, undertoneOf, type Undertone } from './color';
import type { Category, Finish, Product, Trait } from './types';

export const STORE_NAME = 'Counterline Beauty';
export const BRANDS = ['Saltmoss', 'Oddleaf', 'Fernhalo'] as const;

// Nine depths from fair to deep, three undertones each.
const DEPTHS = [82, 76, 70, 64, 58, 52, 46, 40, 34];
const UNDERTONE_AB: Record<Undertone, [number, number]> = {
  cool: [11, 13],
  neutral: [10, 16],
  warm: [9, 21],
};
const UT_LETTER: Record<Undertone, string> = { cool: 'C', neutral: 'N', warm: 'W' };

/** A shade ladder in LAB: deeper shades carry more chroma, as real skin does. */
export function shadeLadder(lift = 0) {
  const out: { name: string; hex: string; undertone: Undertone; depth: number }[] = [];
  DEPTHS.forEach((L, i) => {
    const chroma = 1 + (82 - L) / 60;
    for (const ut of ['cool', 'neutral', 'warm'] as Undertone[]) {
      const [a, b] = UNDERTONE_AB[ut];
      const hex = labToHex({ L: L + lift, a: a * chroma, b: b * chroma });
      out.push({ name: `${(i + 1) * 10 + 100}${UT_LETTER[ut]}`, hex, undertone: undertoneOf(hex), depth: i });
    }
  });
  return out;
}

const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

function line(
  brand: string,
  name: string,
  category: Category,
  price: number,
  finish: Finish,
  traits: Trait[],
  lift = 0,
): Product[] {
  return shadeLadder(lift).map((s) => ({
    id: `${slug(brand)}-${slug(name)}-${s.name.toLowerCase()}`,
    brand,
    name,
    category,
    price,
    finish,
    shade: { name: s.name, hex: s.hex, undertone: s.undertone },
    traits,
  }));
}

function one(
  brand: string,
  name: string,
  category: Category,
  price: number,
  traits: Trait[],
  extra: Partial<Product> = {},
): Product {
  return { id: `${slug(brand)}-${slug(name)}${extra.shade ? '-' + slug(extra.shade.name) : ''}`, brand, name, category, price, traits, ...extra };
}

const shade = (name: string, hex: string) => ({ name, hex, undertone: undertoneOf(hex) });

export const CATALOG: Product[] = [
  // Base
  ...line('Saltmoss', 'Stay Matte Foundation', 'foundation', 1450, 'matte', ['mattifying', 'long_wear', 'oil_control', 'non_comedogenic']),
  ...line('Oddleaf', 'Dew Skin Foundation', 'foundation', 1290, 'dewy', ['hydrating', 'glow', 'rich']),
  ...line('Fernhalo', 'Soft Satin Foundation', 'foundation', 1350, 'satin', ['hydrating', 'non_comedogenic', 'fragrance_free']),
  ...line('Fernhalo', 'Bright Eye Concealer', 'concealer', 790, 'satin', ['hydrating', 'fragrance_free'], 4),
  ...line('Saltmoss', 'Full Cover Concealer', 'concealer', 850, 'matte', ['long_wear', 'mattifying'], 4),
  one('Saltmoss', 'Pore Blur Primer', 'primer', 990, ['mattifying', 'oil_control', 'non_comedogenic'], { finish: 'matte' }),
  one('Oddleaf', 'Glow Grip Primer', 'primer', 950, ['hydrating', 'glow', 'fragrance'], { finish: 'dewy' }),
  one('Fernhalo', 'Calm Base Primer', 'primer', 920, ['hydrating', 'fragrance_free', 'non_comedogenic'], { finish: 'satin' }),

  // Cheeks
  one('Oddleaf', 'Starlit Highlighter', 'highlighter', 890, ['glow'], { finish: 'shimmer', shade: shade('Champagne', '#E8C9A0') }),
  one('Fernhalo', 'Satin Light Highlighter', 'highlighter', 840, ['glow', 'fragrance_free'], { finish: 'satin', shade: shade('Soft Pearl', '#E4C4AA') }),
  one('Oddleaf', 'Flush Blush', 'blush', 690, ['fragrance'], { finish: 'shimmer', shade: shade('Rose Riot', '#D2475E') }),
  one('Fernhalo', 'Cheek Tint', 'blush', 650, ['fragrance_free'], { finish: 'matte', shade: shade('Peach Hour', '#E0896A') }),
  one('Fernhalo', 'Cheek Tint', 'blush', 650, ['fragrance_free'], { finish: 'matte', shade: shade('Clay Rose', '#B5655E') }),

  // Lips
  one('Saltmoss', 'Velvet Lip', 'lip_color', 750, ['long_wear'], { finish: 'matte', shade: shade('Bare Biscuit', '#C99A85') }),
  one('Saltmoss', 'Velvet Lip', 'lip_color', 750, ['long_wear'], { finish: 'matte', shade: shade('Cinnamon Stick', '#9C5A48') }),
  one('Saltmoss', 'Velvet Lip', 'lip_color', 750, ['long_wear'], { finish: 'matte', shade: shade('Brick Lane', '#8E3B32') }),
  one('Oddleaf', 'Jelly Gloss', 'lip_color', 590, ['hydrating'], { finish: 'gloss', shade: shade('Guava', '#D9616B') }),
  one('Oddleaf', 'Jelly Gloss', 'lip_color', 590, ['hydrating'], { finish: 'gloss', shade: shade('Mulberry', '#7E2F48') }),
  one('Fernhalo', 'Balm Stain', 'lip_color', 620, ['hydrating', 'fragrance_free'], { finish: 'satin', shade: shade('Rosewood', '#A2575A') }),
  one('Fernhalo', 'Balm Stain', 'lip_color', 620, ['hydrating', 'fragrance_free'], { finish: 'satin', shade: shade('Toffee', '#A86A50') }),

  // Skincare
  one('Oddleaf', 'Butter Rich Night Cream', 'moisturiser', 1190, ['rich', 'hydrating', 'fragrance']),
  one('Saltmoss', 'Water Gel Moisturiser', 'moisturiser', 990, ['gel', 'hydrating', 'non_comedogenic', 'oil_control']),
  one('Fernhalo', 'Barrier Milk Moisturiser', 'moisturiser', 1090, ['hydrating', 'fragrance_free', 'non_comedogenic']),
  one('Saltmoss', 'Deep Foam Cleanser', 'cleanser', 540, ['foaming', 'oil_control', 'fragrance']),
  one('Fernhalo', 'Cream Cleanser', 'cleanser', 560, ['cream_cleanser', 'hydrating', 'fragrance_free']),
  one('Oddleaf', 'Glow Peel Serum', 'serum', 1390, ['exfoliating', 'glow', 'fragrance']),
  one('Fernhalo', 'Plump Water Serum', 'serum', 1290, ['hydrating', 'fragrance_free', 'non_comedogenic']),
  one('Saltmoss', 'Clear Days Serum', 'serum', 1250, ['oil_control', 'non_comedogenic', 'fragrance_free']),
  one('Saltmoss', 'Invisible Matte SPF 50', 'sunscreen', 790, ['spf', 'mattifying', 'non_comedogenic'], { finish: 'matte' }),
  one('Oddleaf', 'Dewy Shield SPF 50', 'sunscreen', 750, ['spf', 'hydrating', 'glow'], { finish: 'dewy' }),
];

export const byId = new Map(CATALOG.map((p) => [p.id, p]));

export function getProduct(id: string): Product {
  const p = byId.get(id);
  if (!p) throw new Error(`unknown product ${id}`);
  return p;
}

export const CATEGORY_LABEL: Record<Category, string> = {
  foundation: 'Foundation',
  concealer: 'Concealer',
  primer: 'Primer',
  highlighter: 'Highlighter',
  blush: 'Blush',
  lip_color: 'Lip colour',
  moisturiser: 'Moisturiser',
  cleanser: 'Cleanser',
  serum: 'Serum',
  sunscreen: 'Sunscreen',
};

/** Categories the YouCam Makeup Virtual Try-On can render. */
export const TRY_ON_CATEGORIES: Category[] = ['foundation', 'concealer', 'highlighter', 'blush', 'lip_color'];
