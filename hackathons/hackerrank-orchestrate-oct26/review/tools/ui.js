const { chromium } = require('playwright');
const URL = 'file:///tmp/cr/code/ui/ghost_ledger.html';
const SHOTS = '/home/user/DSProjects/hackathons/hackerrank-orchestrate-oct26/review/screens/';
const EMAIL = /[A-Za-z0-9._%+-]{3,}@[A-Za-z0-9.-]+\.[a-z]{2,}/g;
const out = [];
const log = (...a) => { const s = a.map(x => typeof x === 'string' ? x : JSON.stringify(x)).join(' '); out.push(s); console.log(s); };
(async () => {
  const browser = await chromium.launch();
  for (const [w, h] of [[1440, 900], [400, 860]]) for (const scheme of ['light', 'dark']) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme });
    const page = await ctx.newPage(); const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); page.on('pageerror', e => errs.push(String(e)));
    await page.goto(URL); await page.waitForTimeout(400);
    const ov = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
      wide: [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > document.documentElement.clientWidth + 1 && r.width > 0 && getComputedStyle(e).position !== 'fixed'; }).slice(0, 5).map(e => e.tagName + '.' + e.className + '#' + e.id + ' right=' + Math.round(e.getBoundingClientRect().right)) }));
    const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    log(`[${w} ${scheme}] scrollWidth=${ov.sw} clientWidth=${ov.cw} overflow=${ov.sw > ov.cw} bg=${bg} errors=${JSON.stringify(errs)} overflowing=${JSON.stringify(ov.wide)}`);
    await page.screenshot({ path: `${SHOTS}${w}_${scheme}.png`, fullPage: false });
    await ctx.close();
  }
  // functional tests at desktop
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await ctx.grantPermissions([]);
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(String(e))); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(URL); await page.waitForTimeout(300);
  const count = () => page.$$eval('#list .item', a => a.length);
  log('initial items', await count(), 'dossier=', await page.$eval('#dossier h2', e => e.textContent).catch(() => null));
  for (const q of ['case_63', 'search_428', 'gmail', 'user_130', 'CASE_63', '  case_63  ', 'zzzz']) {
    await page.fill('#q', q); await page.waitForTimeout(100);
    log(`search "${q}" ->`, await count(), 'first=', await page.$eval('#list .item', e => e.dataset.id).catch(() => '(none)'), 'empty-msg=', await page.$('#list .empty') ? 'yes' : 'no');
  }
  await page.fill('#q', '');
  for (const f of ['INCOMPLETE', 'COMPLETE', 'NOT_APPLICABLE', 'ALL']) { await page.click(`#filters [data-f="${f}"]`); log('filter', f, await count()); }
  const cells = await page.$$eval('#matrix .cell', a => a.map(b => [b.dataset.cell, b.textContent.trim().replace(/\s+/g, ' ')]));
  log('matrix cells', cells);
  if (cells.length) { const c = cells.find(x => x[0] === 'COMPLETE|INCOMPLETE') || cells[0];
    await page.click(`#matrix .cell[data-cell="${c[0]}"]`); log('cell filter', c[0], '->', await count());
    await page.click(`#filters [data-f="COMPLETE"]`); log('cell + status COMPLETE ->', await count(), 'empty msg', !!(await page.$('#list .empty')));
    await page.click(`#filters [data-f="ALL"]`); await page.click(`#matrix .cell[data-cell="${c[0]}"]`); log('cell toggled off ->', await count()); }
  // mask
  const visibleEmails = () => page.evaluate((re) => { const r = new RegExp(re, 'g'); return (document.body.innerText.match(r) || []).slice(0, 5); }, EMAIL.source);
  await page.goto(URL + '#case_63'); await page.waitForTimeout(300);
  log('deep link #case_63 dossier=', await page.$eval('#dossier h2', e => e.textContent));
  for (let i = 0; i < 3; i++) { const b = await page.$$('#dossier .step > button'); if (b[i]) await b[i].click(); }
  await page.click('#rawbtn');
  log('masked: aria-pressed', await page.getAttribute('#maskbtn', 'aria-pressed'), 'emails visible:', await visibleEmails());
  const attrLeak = await page.evaluate((re) => { const r = new RegExp(re); return [...document.querySelectorAll('#list *, #dossier *')].flatMap(e => [...e.attributes].filter(a => r.test(a.value)).map(a => e.tagName + '[' + a.name + ']')).slice(0, 5); }, EMAIL.source);
  log('masked: emails in DOM attributes', attrLeak);
  await page.fill('#q', 'gmail'); log('masked search "gmail" still filters (oracle on hidden PII):', await count()); await page.fill('#q', '');
  await page.screenshot({ path: SHOTS + 'dossier_case63_masked.png', fullPage: true });
  await page.click('#maskbtn'); log('unmasked: emails visible sample', (await visibleEmails()).length > 0);
  await page.reload(); await page.waitForTimeout(300); log('mask persisted after reload:', await page.getAttribute('#maskbtn', 'aria-pressed'));
  await page.click('#maskbtn');
  // theme
  const themes = []; for (let i = 0; i < 3; i++) { await page.click('#themebtn'); themes.push([await page.textContent('#themebtn'), await page.evaluate(() => document.documentElement.dataset.theme || '(none)'), await page.evaluate(() => getComputedStyle(document.body).backgroundColor)]); }
  log('theme cycle', themes);
  // hashchange
  await page.evaluate(() => { location.hash = '#case_35'; }); await page.waitForTimeout(200);
  log('hashchange to #case_35 -> dossier', await page.$eval('#dossier h2', e => e.textContent));
  // copy fallback (no clipboard permission)
  await page.click('#copybtn'); await page.waitForTimeout(200);
  log('copy button text after click', await page.textContent('#copybtn'), 'raw visible', await page.$eval('#raw', e => !e.hidden));
  // keyboard
  await page.goto(URL); await page.waitForTimeout(300); await page.evaluate(() => document.activeElement.blur());
  let path = []; let reached = null;
  for (let i = 0; i < 60; i++) { await page.keyboard.press('Tab'); const a = await page.evaluate(() => { const e = document.activeElement; return { tag: e.tagName, id: e.id, cls: e.className, did: e.dataset && e.dataset.id, txt: (e.textContent || '').trim().slice(0, 25) }; }); path.push(a.id || a.did || a.cls || a.tag); if (a.did && !reached) { reached = { tabs: i + 1, id: a.did }; break; } }
  log('tab path', path.slice(0, 25), 'reached case', reached);
  const ringOk = await page.evaluate(() => { const s = getComputedStyle(document.activeElement); return s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.boxShadow; }); log('focus ring', ringOk);
  if (reached) { await page.keyboard.press('Enter'); await page.waitForTimeout(200); log('Enter opened', await page.$eval('#dossier h2', e => e.textContent)); }
  // can we tab from list into dossier step buttons?
  let stepReached = null; for (let i = 0; i < 700; i++) { await page.keyboard.press('Tab'); const inStep = await page.evaluate(() => !!document.activeElement.closest('.step')); if (inStep) { stepReached = i + 1; break; } }
  log('tabs from case to first step expander', stepReached);
  if (stepReached) { await page.keyboard.press('Enter'); log('step expanded via Enter', await page.evaluate(() => document.activeElement.getAttribute('aria-expanded'))); }
  // phone: does selecting a case scroll to dossier?
  const ph = await (await browser.newContext({ viewport: { width: 400, height: 860 } })).newPage();
  await ph.goto(URL); await ph.waitForTimeout(300); await ph.fill('#q', 'case_63'); await ph.click('#list .item'); await ph.waitForTimeout(300);
  const dy = await ph.evaluate(() => ({ scrollY: scrollY, dossierTop: Math.round(document.getElementById('dossier').getBoundingClientRect().top), vh: innerHeight }));
  log('phone: after tapping case, scrollY/dossierTop', dy);
  await ph.screenshot({ path: SHOTS + '400_after_tap.png' });
  const phov = await ph.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]); log('phone overflow with dossier open', phov);
  await ph.evaluate(() => document.getElementById('dossier').scrollIntoView()); await ph.screenshot({ path: SHOTS + '400_dossier.png', fullPage: false });
  log('page errors', errs);
  require('fs').writeFileSync('/tmp/rv/ui_log.txt', out.join('\n'));
  await browser.close();
})();
