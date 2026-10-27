import { useEffect, useMemo, useState } from 'react';
import { CATALOG, CATEGORY_LABEL, STORE_NAME, TRY_ON_CATEGORIES } from './domain/catalog';
import { checkBasket, readScan, type BasketLine } from './domain/check';
import { undertoneOf } from './domain/color';
import { SAMPLE_BASKET } from './domain/sample';
import type { ItemCheck, Product, Scan, ScoredConcern } from './domain/types';
import { getStatus, prepPhoto, scanPhoto, sampleScan, tryOn, type Status } from './api';

const CONCERN_LABEL: Record<ScoredConcern, string> = {
  moisture: 'Moisture',
  oiliness: 'Oil balance',
  pore: 'Pores',
  texture: 'Texture',
  redness: 'Redness',
  acne: 'Breakouts',
  radiance: 'Radiance',
  dark_circle_v2: 'Under-eye',
  age_spot: 'Spots',
  wrinkle: 'Fine lines',
  firmness: 'Firmness',
};

const rupees = (n: number) => `₹${n.toLocaleString('en-IN')}`;
const productName = (p: Product) => `${p.brand} ${p.name}${p.shade ? ` · ${p.shade.name}` : ''}`;

export default function App() {
  const [status, setStatus] = useState<Status>();
  const [scan, setScan] = useState<Scan>();
  const [photo, setPhoto] = useState<string>();
  const [basket, setBasket] = useState<BasketLine[]>([]);
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [busy, setBusy] = useState<string>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    getStatus().then(setStatus).catch(() => setStatus({ live: false }));
  }, []);

  const result = useMemo(() => (scan ? checkBasket(scan, basket) : undefined), [scan, basket]);

  async function loadSample() {
    setError(undefined);
    setBusy('Loading the sample shopper…');
    try {
      const s = await sampleScan();
      setScan(s.scan);
      setPhoto(s.imageUrl);
      setBasket(SAMPLE_BASKET);
      setStep(1);
    } catch (e) {
      setError(String((e as Error).message));
    } finally {
      setBusy(undefined);
    }
  }

  async function scanOwnPhoto(file: File) {
    setError(undefined);
    setBusy('Running the counter scan (skin analysis + colour tones)…');
    try {
      const blob = await prepPhoto(file);
      const s = await scanPhoto(blob);
      setScan(s.scan);
      setPhoto(s.imageUrl ?? URL.createObjectURL(blob));
      if (!basket.length) setBasket(SAMPLE_BASKET);
    } catch (e) {
      setError(String((e as Error).message));
    } finally {
      setBusy(undefined);
    }
  }

  return (
    <div className="page">
      <header className="top">
        <div>
          <div className="store">{STORE_NAME}</div>
          <h1>Second Look</h1>
          <p className="lede">The skin scan you just had at the counter, used to check what you're about to buy and what's already on your shelf.</p>
        </div>
        <nav className="steps" aria-label="Steps">
          {(['Counter scan', 'Your basket', 'Second look'] as const).map((label, i) => (
            <button key={label} className={step === i + 1 ? 'on' : ''} disabled={!scan} onClick={() => setStep((i + 1) as 1 | 2 | 3)}>
              <span>{i + 1}</span> {label}
            </button>
          ))}
        </nav>
      </header>

      {error && <div className="alert" role="alert">{error}</div>}
      {busy && <div className="busy" aria-live="polite">{busy}</div>}

      {step === 1 && (
        <section>
          {!scan && (
            <div className="start">
              <div className="card">
                <h2>Sample shopper</h2>
                <p>A shopper with a combination skin scan and eight products: five in the cart, three at home.</p>
                <button className="primary" onClick={loadSample} disabled={!!busy}>Use the sample shopper</button>
              </div>
              <div className="card">
                <h2>Your own scan</h2>
                <p>A front-facing photo, hair off the face, good light. Runs YouCam AI Skin Analysis and the Facial Color Tones Analyzer.</p>
                <label className={`primary file ${status?.live ? '' : 'disabled'}`}>
                  Take or upload a photo
                  <input type="file" accept="image/jpeg,image/png" capture="user" disabled={!status?.live || !!busy}
                    onChange={(e) => e.target.files?.[0] && scanOwnPhoto(e.target.files[0])} />
                </label>
                {status && !status.live && <p className="muted small">{status.reason ?? 'Live scans are paused on this demo; the sample shopper works.'}</p>}
              </div>
            </div>
          )}
          {scan && <ScanView scan={scan} photo={photo} onNext={() => setStep(2)} onReset={() => { setScan(undefined); setPhoto(undefined); }} />}
        </section>
      )}

      {step === 2 && scan && <BasketView basket={basket} setBasket={setBasket} onNext={() => setStep(3)} />}

      {step === 3 && scan && result && (
        <Verdicts scan={scan} photo={photo} result={result} onAdd={(p) => setBasket((b) => [...b, { product: p, where: 'cart' }])}
          onApplySwap={(item) => setBasket((b) => b.map((l) => (l.product.id === item.product.id && l.where === item.where && item.swapTo ? { ...l, product: item.swapTo } : l)))}
          onDrop={(item) => setBasket((b) => b.filter((l) => !(l.product.id === item.product.id && l.where === item.where)))} />
      )}

      <footer>
        <p>Powered by YouCam API: AI Skin Analysis, AI Facial Color Tones Analyzer, AI Makeup Virtual Try-On. Every brand and product in this demo store is made up.</p>
        <p>Cosmetic guidance for choosing products, not medical advice.</p>
      </footer>
    </div>
  );
}

function Swatch({ hex, size = 20, label }: { hex?: string; size?: number; label?: string }) {
  if (!hex) return null;
  return <span className="swatch" style={{ background: hex, width: size, height: size }} title={label ?? hex} aria-label={label ?? hex} />;
}

function ScanView({ scan, photo, onNext, onReset }: { scan: Scan; photo?: string; onNext: () => void; onReset: () => void }) {
  const read = readScan(scan);
  const entries = (Object.keys(CONCERN_LABEL) as ScoredConcern[]).filter((k) => scan.scores[k] !== undefined);
  return (
    <div className="scan">
      <div className="card who">
        {photo ? <img src={photo} alt="Scanned photo" className="selfie" /> : <div className="selfie placeholder">Sample scan</div>}
        <div className="tones">
          <div><Swatch hex={scan.tone.skin} size={36} label="Skin" /> <b>Skin</b> <span className="muted">{scan.tone.skin} · reads {undertoneOf(scan.tone.skin)}</span></div>
          {scan.tone.lip && <div><Swatch hex={scan.tone.lip} size={24} label="Lips" /> Lips <span className="muted">{scan.tone.lip}</span></div>}
          {scan.tone.eye && <div><Swatch hex={scan.tone.eye} size={24} label="Eyes" /> Eyes <span className="muted">{scan.tone.eyeName ?? scan.tone.eye}</span></div>}
        </div>
        {scan.source !== 'live' && <p className="muted small">Sample data. A live scan replaces it with your own result.</p>}
      </div>
      <div className="card">
        <h2>What the scan says</h2>
        <div className="zones">
          {scan.skinType.whole && <span className="chip">Overall: {scan.skinType.whole}</span>}
          {scan.skinType.tZone && <span className="chip">T-zone: {scan.skinType.tZone}</span>}
          {scan.skinType.uZone && <span className="chip">Cheeks: {scan.skinType.uZone}</span>}
        </div>
        <ul className="bars">
          {entries.map((k) => {
            const v = scan.scores[k]!;
            return (
              <li key={k} className={v < 60 ? 'shows' : ''}>
                <span>{CONCERN_LABEL[k]}</span>
                <span className="bar"><i style={{ width: `${v}%` }} /></span>
                <span className="num">{v}</span>
              </li>
            );
          })}
        </ul>
        <p className="muted small">Higher is better. Below 60 is something the basket check takes into account.</p>
        <p className="small">In short: {[read.oilyT && 'oily T-zone', read.dry && 'dry', read.textureShows && 'visible pores and texture', read.redness && 'some redness', read.darkCircles && 'under-eye shadow', read.breakouts && 'breakouts', read.dull && 'a little dull'].filter(Boolean).join(', ') || 'nothing that changes your choices'}.</p>
        <div className="row">
          <button className="primary" onClick={onNext}>Check my basket</button>
          <button onClick={onReset}>Start over</button>
        </div>
      </div>
    </div>
  );
}

function BasketView({ basket, setBasket, onNext }: { basket: BasketLine[]; setBasket: (f: (b: BasketLine[]) => BasketLine[]) => void; onNext: () => void }) {
  const [q, setQ] = useState('');
  const [where, setWhere] = useState<'cart' | 'home'>('cart');
  const hits = q.length < 2 ? [] : CATALOG.filter((p) => productName(p).toLowerCase().includes(q.toLowerCase()) || CATEGORY_LABEL[p.category].toLowerCase().includes(q.toLowerCase())).slice(0, 8);
  const list = (w: 'cart' | 'home') => basket.filter((l) => l.where === w);
  return (
    <section className="basket">
      {(['cart', 'home'] as const).map((w) => (
        <div className="card" key={w}>
          <h2>{w === 'cart' ? 'In your cart' : 'Already on your shelf'}</h2>
          {!list(w).length && <p className="muted">Nothing yet.</p>}
          <ul className="items">
            {list(w).map((l, i) => (
              <li key={l.product.id + i}>
                <Swatch hex={l.product.shade?.hex} />
                <span className="grow">{productName(l.product)}<br /><span className="muted small">{CATEGORY_LABEL[l.product.category]} · {rupees(l.product.price)}</span></span>
                <button className="link" onClick={() => setBasket((b) => b.filter((x) => x !== l))} aria-label={`Remove ${productName(l.product)}`}>Remove</button>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <div className="card add">
        <h2>Add a product</h2>
        <div className="row">
          <input placeholder="Search the store (e.g. foundation, gloss, 150N)" value={q} onChange={(e) => setQ(e.target.value)} />
          <select value={where} onChange={(e) => setWhere(e.target.value as 'cart' | 'home')} aria-label="Where">
            <option value="cart">to cart</option>
            <option value="home">I own it</option>
          </select>
        </div>
        <ul className="items">
          {hits.map((p) => (
            <li key={p.id}>
              <Swatch hex={p.shade?.hex} />
              <span className="grow">{productName(p)} <span className="muted small">{rupees(p.price)}</span></span>
              <button className="link" onClick={() => { setBasket((b) => [...b, { product: p, where }]); setQ(''); }}>Add</button>
            </li>
          ))}
        </ul>
        <button className="primary" onClick={onNext} disabled={!basket.length}>Give it a second look</button>
      </div>
    </section>
  );
}

const VERDICT_TEXT = { keep: 'Keep', swap: 'Swap', skip: 'Skip' } as const;

function Verdicts({ scan, photo, result, onAdd, onApplySwap, onDrop }: {
  scan: Scan;
  photo?: string;
  result: ReturnType<typeof checkBasket>;
  onAdd: (p: Product) => void;
  onApplySwap: (i: ItemCheck) => void;
  onDrop: (i: ItemCheck) => void;
}) {
  const count = (v: string) => result.items.filter((i) => i.verdict === v).length;
  return (
    <section>
      <div className="summary card">
        <div><b className="keep">{count('keep')}</b> keep</div>
        <div><b className="swap">{count('swap')}</b> swap</div>
        <div><b className="skip">{count('skip')}</b> skip</div>
        <div><b>{rupees(result.savings)}</b> you don't need to spend</div>
      </div>
      {result.items.map((item, i) => <VerdictCard key={item.product.id + i} item={item} scan={scan} photo={photo} onApplySwap={onApplySwap} onDrop={onDrop} />)}
      {!!result.missing.length && (
        <div className="card">
          <h2>Missing from your routine</h2>
          <ul className="items">
            {result.missing.map((m) => (
              <li key={m.category}>
                <Swatch hex={m.suggestion?.shade?.hex} />
                <span className="grow">{m.text}{m.suggestion && <><br /><span className="small">Suggested: {productName(m.suggestion)} · {rupees(m.suggestion.price)}</span></>}</span>
                {m.suggestion && <button className="link" onClick={() => onAdd(m.suggestion!)}>Add to cart</button>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function VerdictCard({ item, scan, photo, onApplySwap, onDrop }: { item: ItemCheck; scan: Scan; photo?: string; onApplySwap: (i: ItemCheck) => void; onDrop: (i: ItemCheck) => void }) {
  const [shots, setShots] = useState<{ before?: string; after?: string; error?: string; busy?: boolean }>({});
  const canTry = TRY_ON_CATEGORIES.includes(item.product.category);
  async function tryBoth() {
    setShots({ busy: true });
    try {
      const [before, after] = await Promise.all([
        tryOn(scan.id, item.product.id),
        item.swapTo ? tryOn(scan.id, item.swapTo.id) : Promise.resolve(undefined),
      ]);
      setShots({ before, after });
    } catch (e) {
      setShots({ error: String((e as Error).message) });
    }
  }
  return (
    <article className={`card verdict ${item.verdict}`}>
      <div className="head">
        <span className={`badge ${item.verdict}`}>{VERDICT_TEXT[item.verdict]}</span>
        <Swatch hex={item.product.shade?.hex} />
        <span className="grow"><b>{productName(item.product)}</b><br /><span className="muted small">{item.where === 'cart' ? 'In your cart' : 'On your shelf'} · {rupees(item.product.price)}</span></span>
      </div>
      <ul className="reasons">
        {item.reasons.map((r, i) => <li key={i} className={r.weight}><span className="chip">{r.basis}</span> {r.text}</li>)}
        {!item.reasons.length && <li className="good">Nothing in your scan argues against it.</li>}
      </ul>
      {item.swapTo && (
        <div className="swapto">
          <Swatch hex={item.swapTo.shade?.hex} />
          <span className="grow">Instead: <b>{productName(item.swapTo)}</b> · {rupees(item.swapTo.price)}</span>
          {item.where === 'cart' && <button onClick={() => onApplySwap(item)}>Swap in cart</button>}
        </div>
      )}
      {item.verdict === 'skip' && item.where === 'cart' && <button className="link" onClick={() => onDrop(item)}>Remove from cart</button>}
      {canTry && (
        <div className="tryon">
          {!shots.before && !shots.busy && <button onClick={tryBoth}>{item.swapTo ? 'Try both on my photo' : 'Try it on my photo'}</button>}
          {shots.busy && <span className="muted">Rendering with YouCam Makeup Virtual Try-On…</span>}
          {shots.error && <span className="alert small">{shots.error}</span>}
          {shots.before && (
            <div className="pair">
              {photo && <figure><img src={photo} alt="Bare" /><figcaption>Bare</figcaption></figure>}
              <figure><img src={shots.before} alt={productName(item.product)} /><figcaption>{item.product.shade?.name ?? item.product.name}</figcaption></figure>
              {shots.after && item.swapTo && <figure><img src={shots.after} alt={productName(item.swapTo)} /><figcaption>{item.swapTo.shade?.name ?? item.swapTo.name} (suggested)</figcaption></figure>}
            </div>
          )}
        </div>
      )}
    </article>
  );
}
