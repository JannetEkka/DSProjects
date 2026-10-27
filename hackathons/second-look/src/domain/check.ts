// The basket check: every product the shopper is buying or already owns, read against one counter scan.
// Cosmetic guidance only. Nothing here diagnoses or treats anything.
import { deltaE, deltaE2000, hexToLab, hueAngle, undertoneOf } from './color';
import { CATALOG, CATEGORY_LABEL } from './catalog';
import type { BasketCheck, Category, ItemCheck, Product, Reason, Scan, Verdict } from './types';

/** What the scan says, in the terms the rules use. Scores are 1–100, higher is better. */
export interface SkinRead {
  oilyT: boolean;
  dry: boolean;
  textureShows: boolean;
  redness: boolean;
  breakouts: boolean;
  darkCircles: boolean;
  dull: boolean;
  undertone: ReturnType<typeof undertoneOf>;
  skin: string;
}

const CONCERN_AT = 60;

export function readScan(scan: Scan): SkinRead {
  const s = scan.scores;
  const low = (v: number | undefined, at = CONCERN_AT) => v !== undefined && v < at;
  const types = [scan.skinType.whole, scan.skinType.tZone, scan.skinType.uZone].filter(Boolean).join(' ');
  return {
    oilyT: /Oily|Combination/.test(types) || low(s.oiliness, 55),
    dry: /Dry/.test(types) || low(s.moisture, 55),
    textureShows: low(s.pore) || low(s.texture),
    redness: /Redness/.test(types) || low(s.redness, 55),
    breakouts: low(s.acne),
    darkCircles: low(s.dark_circle_v2),
    dull: low(s.radiance),
    undertone: undertoneOf(scan.tone.skin),
    skin: scan.tone.skin,
  };
}

const has = (p: Product, t: Product['traits'][number]) => p.traits.includes(t);
const r = (basis: string, text: string, weight: Reason['weight']): Reason => ({ basis, text, weight });

/** Lift a hex in lightness, for the concealer target (about one shade brighter than skin). */
function lighten(hex: string, dL: number) {
  const lab = hexToLab(hex);
  return { ...lab, L: lab.L + dL };
}

function shadeReasons(p: Product, read: SkinRead): { reasons: Reason[]; delta?: number } {
  if (!p.shade || (p.category !== 'foundation' && p.category !== 'concealer')) return { reasons: [] };
  const reasons: Reason[] = [];
  const target = p.category === 'concealer' ? lighten(read.skin, 4) : hexToLab(read.skin);
  const shadeLab = hexToLab(p.shade.hex);
  const delta = deltaE2000(shadeLab, target);
  const dL = shadeLab.L - target.L;
  const dir = dL > 2 ? 'lighter' : dL < -2 ? 'deeper' : '';
  const what = p.category === 'concealer' ? 'one step brighter than your skin' : 'your scanned skin colour';
  if (delta <= 4) {
    reasons.push(r('Skin tone', `Shade ${p.shade.name} is a close match to ${what} (ΔE ${delta.toFixed(1)}).`, 'good'));
  } else {
    const how = delta > 7 ? 'clearly off' : 'a step off';
    reasons.push(
      r('Skin tone', `Shade ${p.shade.name} is ${dir ? `${dir} than` : 'off from'} ${what}: ΔE ${delta.toFixed(1)}, ${how}.`, 'swap'),
    );
  }
  if (p.shade.undertone !== read.undertone && p.shade.undertone !== 'neutral' && read.undertone !== 'neutral') {
    reasons.push(
      r('Undertone', `Your skin reads ${read.undertone}; this shade is ${p.shade.undertone}, so it can look ${p.shade.undertone === 'cool' ? 'ashy or pink' : 'orange'} on you.`, 'swap'),
    );
  }
  return { reasons, delta };
}

/** Reasons that come from the skin scan alone, before shade. */
export function scanReasons(p: Product, read: SkinRead): Reason[] {
  const out: Reason[] = [];
  const oily = 'T-zone oil';
  const dry = 'Moisture';
  switch (p.category) {
    case 'foundation':
      if (read.oilyT && p.finish === 'dewy') out.push(r(oily, 'A dewy finish on an oily T-zone tends to look greasy by midday. Same shade in satin or matte.', 'swap'));
      if (read.oilyT && has(p, 'mattifying')) out.push(r(oily, 'Matte, long-wear base suits the shine your scan picked up.', 'good'));
      if (read.dry && p.finish === 'matte' && !read.oilyT) out.push(r(dry, 'Matte long-wear base clings to dry patches. A satin finish sits better.', 'swap'));
      if (read.breakouts && has(p, 'rich') && !has(p, 'non_comedogenic')) out.push(r('Breakouts', 'Your scan shows breakouts; a heavy, rich base isn’t the one to add. Pick a non-comedogenic formula.', 'swap'));
      break;
    case 'concealer':
      if (read.darkCircles) out.push(r('Dark circles', 'Your scan flags under-eye shadow, so a concealer earns its place.', 'good'));
      if (read.dry && p.finish === 'matte') out.push(r(dry, 'Full-cover matte concealer settles into lines on drier skin.', 'swap'));
      break;
    case 'primer':
      if (read.oilyT && has(p, 'mattifying')) out.push(r(oily, 'A blurring, mattifying primer is the right one for your T-zone.', 'good'));
      if (read.oilyT && has(p, 'glow')) out.push(r(oily, 'A glow primer adds shine where your scan already shows oil.', 'swap'));
      if (read.dry && has(p, 'mattifying') && !read.oilyT) out.push(r(dry, 'A mattifying primer pulls more moisture from skin that’s already dry.', 'swap'));
      if (read.textureShows && has(p, 'mattifying')) out.push(r('Pores & texture', 'Blurring primer softens the texture your scan picked up.', 'good'));
      break;
    case 'highlighter':
      if (read.textureShows && p.finish === 'shimmer') out.push(r('Pores & texture', 'Shimmer catches on texture and makes pores look bigger. A satin highlighter gives glow without it.', 'swap'));
      if (read.dull && p.finish !== 'shimmer') out.push(r('Radiance', 'Your scan reads a little dull; a soft satin glow helps.', 'good'));
      break;
    case 'blush':
      if (read.redness && p.shade && hueAngle(p.shade.hex) < 30) out.push(r('Redness', 'A rose-red blush stacks on the redness your scan shows. A peach tone balances it.', 'swap'));
      if (read.textureShows && p.finish === 'shimmer') out.push(r('Pores & texture', 'Shimmer blush shows texture on the cheeks. A matte tint sits flatter.', 'swap'));
      if (read.redness && p.shade && hueAngle(p.shade.hex) >= 30) out.push(r('Redness', 'A peach or neutral tone doesn’t add to the redness your scan shows.', 'good'));
      break;
    case 'lip_color':
      if (p.shade) {
        const d = deltaE(p.shade.hex, read.skin);
        if (d < 12) out.push(r('Skin tone', `This nude is very close to your skin colour (ΔE ${d.toFixed(1)}), so it can wash you out. One step deeper reads as a lip colour.`, 'swap'));
        else out.push(r('Skin tone', 'Enough contrast with your skin to read as a colour.', 'good'));
      }
      break;
    case 'moisturiser':
      if (read.oilyT && has(p, 'rich')) out.push(r(oily, 'A rich night cream is a lot for an oily T-zone. A water-gel gives the hydration without the weight.', 'swap'));
      if (read.dry && has(p, 'hydrating') && !has(p, 'gel')) out.push(r(dry, 'Your scan reads dry; this one adds moisture.', 'good'));
      if (read.oilyT && has(p, 'gel')) out.push(r(oily, 'A light water-gel hydrates without adding shine.', 'good'));
      if (read.dry && has(p, 'gel') && !read.oilyT) out.push(r(dry, 'A light gel may not be enough for skin this dry.', 'swap'));
      break;
    case 'cleanser':
      if (read.dry && has(p, 'foaming')) out.push(r(dry, 'A deep-foaming cleanser strips skin your scan already reads as dry. A cream cleanser is gentler.', 'swap'));
      if (read.oilyT && has(p, 'foaming') && !read.dry) out.push(r(oily, 'A foaming cleanser suits an oily T-zone.', 'good'));
      break;
    case 'serum':
      if (read.redness && has(p, 'exfoliating')) out.push(r('Redness', 'With the redness your scan shows, an exfoliating peel serum isn’t the one to add now. A fragrance-free serum without acids is the gentler pick.', 'swap'));
      if (read.dull && has(p, 'exfoliating') && !read.redness) out.push(r('Radiance', 'Your scan reads dull; an exfoliating serum helps with glow.', 'good'));
      if (read.dry && has(p, 'hydrating')) out.push(r(dry, 'A hydrating serum suits what your scan shows.', 'good'));
      if (read.oilyT && has(p, 'oil_control')) out.push(r(oily, 'An oil-balancing serum suits your T-zone.', 'good'));
      break;
    case 'sunscreen':
      out.push(r('Daily', 'Daily SPF belongs in every routine.', 'good'));
      if (read.oilyT && p.finish === 'dewy') out.push(r(oily, 'A dewy SPF adds shine on an oily T-zone. The matte one wears better under makeup.', 'swap'));
      break;
  }
  if (read.redness && has(p, 'fragrance') && !out.some((x) => x.basis === 'Redness' && x.weight === 'swap')) {
    out.push(r('Redness', 'Contains added fragrance; with visible redness, the fragrance-free option is the gentler pick.', 'swap'));
  }
  if (read.breakouts && has(p, 'non_comedogenic') && p.category !== 'foundation') {
    out.push(r('Breakouts', 'Labelled non-comedogenic, which suits breakout-prone skin.', 'good'));
  }
  return out;
}

export function judge(p: Product, read: SkinRead): { verdict: Verdict; reasons: Reason[]; shadeDelta?: number } {
  const shade = shadeReasons(p, read);
  const reasons = [...scanReasons(p, read), ...shade.reasons];
  const verdict: Verdict = reasons.some((x) => x.weight === 'skip')
    ? 'skip'
    : reasons.some((x) => x.weight === 'swap')
      ? 'swap'
      : 'keep';
  return { verdict, reasons, shadeDelta: shade.delta };
}

/** The best product in the same category that passes every rule, closest in shade and price to the original. */
export function bestSwap(p: Product, read: SkinRead, catalog: Product[] = CATALOG): Product | undefined {
  const candidates = catalog
    .filter((c) => c.category === p.category && c.id !== p.id)
    .map((c) => ({ c, j: judge(c, read) }))
    .filter(({ j }) => j.verdict === 'keep');
  if (!candidates.length) return undefined;
  const score = ({ c, j }: (typeof candidates)[number]) => {
    let s = -20 * j.reasons.filter((x) => x.weight === 'good').length; // most reasons to keep it
    if (j.shadeDelta !== undefined) s += j.shadeDelta * 10; // shade first
    else if (p.shade && c.shade) s += deltaE(p.shade.hex, c.shade.hex); // stay near the colour they picked
    if (c.brand === p.brand && c.name === p.name) s -= 15; // same line, new shade is the easiest change
    s += Math.abs(c.price - p.price) / 100;
    return s;
  };
  return candidates.sort((a, b) => score(a) - score(b))[0].c;
}

export interface BasketLine {
  product: Product;
  where: 'cart' | 'home';
}

export function checkBasket(scan: Scan, lines: BasketLine[], catalog: Product[] = CATALOG): BasketCheck {
  const read = readScan(scan);
  const items: ItemCheck[] = lines.map(({ product, where }) => {
    const j = judge(product, read);
    return {
      product,
      where,
      verdict: j.verdict,
      reasons: j.reasons,
      shadeDelta: j.shadeDelta,
      swapTo: j.verdict === 'swap' ? bestSwap(product, read, catalog) : undefined,
    };
  });

  // Duplicates: a cart item that does the same job as something already at home that suits.
  for (const item of items) {
    if (item.where !== 'cart') continue;
    const twin = items.find(
      (o) =>
        o !== item &&
        o.where === 'home' &&
        o.verdict === 'keep' &&
        o.product.category === item.product.category &&
        (!item.product.shade || !o.product.shade || deltaE(item.product.shade.hex, o.product.shade.hex) < 8),
    );
    if (twin) {
      item.reasons.push(
        r('Your shelf', `You already own ${twin.product.brand} ${twin.product.name}${twin.product.shade ? ` in ${twin.product.shade.name}` : ''}, which suits you. This one does the same job.`, 'skip'),
      );
      item.verdict = 'skip';
      item.swapTo = undefined;
    }
  }

  const owned = (c: Category) => items.some((i) => i.product.category === c && i.verdict !== 'skip');
  const missing: BasketCheck['missing'] = [];
  const suggest = (c: Category) => {
    const pool = catalog.filter((p) => p.category === c).map((p) => ({ p, j: judge(p, read) }));
    const ok = pool.filter((x) => x.j.verdict === 'keep');
    const goods = (x: (typeof ok)[number]) => x.j.reasons.filter((y) => y.weight === 'good').length;
    ok.sort((a, b) => goods(b) - goods(a) || (a.j.shadeDelta ?? 0) - (b.j.shadeDelta ?? 0) || a.p.price - b.p.price);
    return ok[0]?.p;
  };
  if (!owned('sunscreen')) missing.push({ category: 'sunscreen', text: 'No daily SPF in your basket or on your shelf.', suggestion: suggest('sunscreen') });
  if (read.dry && !owned('moisturiser') && !items.some((i) => i.product.category === 'serum' && i.product.traits.includes('hydrating')))
    missing.push({ category: 'moisturiser', text: 'Your scan reads dry and nothing here adds moisture.', suggestion: suggest('moisturiser') });
  if (read.darkCircles && !owned('concealer'))
    missing.push({ category: 'concealer', text: 'Your scan flags under-eye shadow and there’s no concealer.', suggestion: suggest('concealer') });
  if (read.oilyT && owned('foundation') && !owned('primer'))
    missing.push({ category: 'primer', text: 'With an oily T-zone, a mattifying primer keeps base in place.', suggestion: suggest('primer') });

  const savings = items.filter((i) => i.where === 'cart' && i.verdict === 'skip').reduce((s, i) => s + i.product.price, 0);
  return { items, missing, savings };
}

export const categoryLabel = (c: Category) => CATEGORY_LABEL[c];
