// Product -> YouCam Makeup Virtual Try-On effect. The product's own hex colour and finish go into the request.
import type { Product } from './types';

type Effect = Record<string, unknown>;

const LIP_TEXTURE: Record<string, string> = { matte: 'matte', satin: 'satin', gloss: 'gloss', shimmer: 'shimmer', dewy: 'sheer', cream: 'satin' };

export function effectFor(p: Product): Effect | undefined {
  if (!p.shade) return undefined;
  const color = p.shade.hex.toUpperCase();
  switch (p.category) {
    case 'foundation':
      return {
        category: 'foundation',
        palettes: [
          {
            color,
            colorIntensity: 60,
            glowIntensity: p.finish === 'dewy' ? 70 : p.finish === 'satin' ? 35 : 5,
            coverageIntensity: p.finish === 'matte' ? 70 : 50,
          },
        ],
      };
    case 'concealer':
      return {
        category: 'concealer',
        palettes: [{ color, colorIntensity: 60, colorUnderEyeIntensity: 60, coverageLevel: p.finish === 'matte' ? 75 : 55 }],
      };
    case 'blush': {
      const texture = p.finish === 'shimmer' ? 'shimmer' : 'matte';
      return {
        category: 'blush',
        pattern: { name: '1color1' },
        palettes: [
          texture === 'shimmer'
            ? { color, texture, shimmerColor: '#F6D7B0', shimmerDensity: 60, colorIntensity: 55 }
            : { color, texture, colorIntensity: 55 },
        ],
      };
    }
    case 'highlighter':
      return {
        category: 'highlighter',
        pattern: { name: 'OvalFace2' },
        palettes: [
          p.finish === 'shimmer'
            ? { color, glowIntensity: 60, shimmerIntensity: 80, shimmerDensity: 70, shimmerSize: 60, colorIntensity: 60 }
            : { color, glowIntensity: 55, shimmerIntensity: 0, shimmerDensity: 0, shimmerSize: 0, colorIntensity: 50 },
        ],
      };
    case 'lip_color': {
      const texture = LIP_TEXTURE[p.finish ?? 'satin'] ?? 'satin';
      const palette: Record<string, unknown> = { color, texture, colorIntensity: 70 };
      if (['gloss', 'sheer', 'shimmer'].includes(texture)) {
        palette.gloss = 70;
        palette.transparencyIntensity = 30;
      }
      if (texture === 'shimmer') Object.assign(palette, { shimmerColor: '#FFFFFF', shimmerIntensity: 50, shimmerDensity: 50, shimmerSize: 40 });
      return { category: 'lip_color', shape: { name: 'original' }, style: { type: 'full' }, palettes: [palette] };
    }
    default:
      return undefined;
  }
}

/** Request body for POST /s2s/v2.0/task/makeup-vto. One effect per call, so each try-on costs 1 unit. */
export function makeupRequest(src: { fileId?: string; url?: string }, p: Product) {
  const effect = effectFor(p);
  if (!effect) throw new Error(`${p.category} can't be tried on`);
  return {
    ...(src.fileId ? { src_file_id: src.fileId } : { src_file_url: src.url }),
    effects: [effect],
    version: '1.0',
  };
}
