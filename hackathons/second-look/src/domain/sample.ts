// The sample shopper: a scan and a basket judges can open without spending any API units.
import skin from '../../fixtures/synthetic-skin-analysis.json';
import tone from '../../fixtures/synthetic-skin-tone.json';
import { getProduct } from './catalog';
import type { BasketLine } from './check';
import { buildScan } from './scan';

export const SAMPLE_SCAN = buildScan('sample', 'sample', skin, tone);

export const SAMPLE_BASKET: BasketLine[] = [
  { where: 'cart', product: getProduct('oddleaf-dew-skin-foundation-130c') },
  { where: 'cart', product: getProduct('oddleaf-starlit-highlighter-champagne') },
  { where: 'cart', product: getProduct('oddleaf-glow-peel-serum') },
  { where: 'cart', product: getProduct('saltmoss-velvet-lip-bare-biscuit') },
  { where: 'cart', product: getProduct('fernhalo-cheek-tint-peach-hour') },
  { where: 'home', product: getProduct('oddleaf-butter-rich-night-cream') },
  { where: 'home', product: getProduct('saltmoss-deep-foam-cleanser') },
  { where: 'home', product: getProduct('fernhalo-satin-light-highlighter-soft-pearl') },
];
