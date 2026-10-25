const { chromium } = require('playwright');
const URL = 'file:///tmp/cr2/code/ui/ghost_ledger.html';
const SH = '/home/user/DSProjects/hackathons/hackerrank-orchestrate-oct26/review/screens_final/';
const EMAIL = /[A-Za-z0-9._%+-]{3,}@[A-Za-z0-9.-]+\.[a-z]{2,}/;
const out = []; const log = (...a) => { const s = a.map(x => typeof x === 'string' ? x : JSON.stringify(x)).join(' '); out.push(s); console.log(s); };
const h2 = p => p.$eval('#dossier h2', e => e.textContent).catch(() => '(no h2)');
(async () => {
  const b = await chromium.launch();
  for (const [w, h] of [[1440, 900], [400, 860]]) for (const scheme of ['light', 'dark']) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, colorScheme: scheme }); const p = await ctx.newPage(); const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push(String(e)));
    await p.goto(URL); await p.waitForTimeout(400);
    let ov = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
    await p.goto(URL + '#case_35'); await p.reload(); await p.waitForTimeout(300);
    for (const btn of await p.$$('#dossier .step > button')) await btn.click();
    const ov2 = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
    log(`[${w} ${scheme}] overflow home=${ov[0] > ov[1]} dossier-expanded=${ov2[0] > ov2[1]} (${ov2}) bg=${await p.evaluate(() => getComputedStyle(document.body).backgroundColor)} errors=${JSON.stringify(errs)}`);
    await p.screenshot({ path: `${SH}${w}_${scheme}.png` }); await ctx.close();
  }
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(URL); await p.waitForTimeout(300);
  // bug 1 hashchange
  await p.evaluate(() => { location.hash = '#case_35'; }); await p.waitForTimeout(200); log('B1 hashchange -> ', await h2(p));
  // bug 2 unknown hash
  await p.evaluate(() => { location.hash = '#case_999'; }); await p.waitForTimeout(200);
  log('B2 unknown hash ->', await p.$eval('#dossier', e => e.innerText.slice(0, 90)));
  // bug 5 masked search oracle
  await p.evaluate(() => { location.hash = '#case_63'; }); await p.waitForTimeout(200);
  const cnt = () => p.$$eval('#list .item', a => a.length);
  for (const q of ['gmail', 'proton.me', 'case_63', 'search_428']) { await p.fill('#q', q); await p.waitForTimeout(100); log(`B5 masked search "${q}" ->`, await cnt()); }
  await p.fill('#q', '');
  for (const btn of await p.$$('#dossier .step > button')) await btn.click(); await p.click('#rawbtn');
  log('mask: emails in innerText', (await p.evaluate(() => document.body.innerText)).match(new RegExp(EMAIL.source, 'g'))?.slice(0, 3) || []);
  // bug 6 persistence
  await p.click('#maskbtn'); log('unmasked -> emails visible', EMAIL.test(await p.evaluate(() => document.body.innerText)));
  await p.fill('#q', 'gmail'); await p.waitForTimeout(100); log('B5 unmasked search "gmail" ->', await cnt()); await p.fill('#q', '');
  await p.reload(); await p.waitForTimeout(300); log('B6 after reload mask aria-pressed', await p.getAttribute('#maskbtn', 'aria-pressed'), 'emails visible', EMAIL.test(await p.evaluate(() => document.body.innerText)));
  // bug 7 copy label
  await p.click('#copybtn'); await p.waitForTimeout(100); const l1 = await p.textContent('#copybtn'); await p.waitForTimeout(3500); log('B7 copy label', l1, '-> after 3.5s', await p.textContent('#copybtn'));
  // theme
  const th = []; for (let i = 0; i < 3; i++) { await p.click('#themebtn'); th.push(await p.evaluate(() => document.documentElement.dataset.theme || 'system')); } log('theme cycle', th);
  // bug 3 keyboard
  await p.goto(URL + '#case_33'); await p.reload(); await p.waitForTimeout(300); await p.evaluate(() => document.activeElement.blur());
  const path = []; let atCase = null;
  for (let i = 0; i < 40; i++) { await p.keyboard.press('Tab'); const a = await p.evaluate(() => { const e = document.activeElement; return e.id || (e.dataset && e.dataset.id) || e.className || e.tagName; }); path.push(a); if (/^case_/.test(a)) { atCase = i + 1; break; } }
  log('B3 tab path to first case', path, 'tabs', atCase);
  await p.keyboard.press('ArrowDown'); log('ArrowDown focus ->', await p.evaluate(() => document.activeElement.dataset.id));
  await p.keyboard.press('Enter'); await p.waitForTimeout(200); log('Enter opened', await h2(p));
  let n = null; for (let i = 0; i < 60; i++) { await p.keyboard.press('Tab'); if (await p.evaluate(() => !!document.activeElement.closest('.step'))) { n = i + 1; break; } } log('B3 tabs from case to first step', n);
  if (n) { await p.keyboard.press('Enter'); log('step Enter aria-expanded', await p.evaluate(() => document.activeElement.getAttribute('aria-expanded'))); }
  // skip link
  await p.goto(URL); await p.reload(); await p.waitForTimeout(300); await p.evaluate(() => document.activeElement.blur()); await p.keyboard.press('Tab');
  log('first Tab focuses', await p.evaluate(() => document.activeElement.id || document.activeElement.textContent.trim()));
  await p.keyboard.press('Enter'); await p.waitForTimeout(100); log('skip link -> focus', await p.evaluate(() => document.activeElement.id));
  // bug 4 phone
  const ph = await (await b.newContext({ viewport: { width: 400, height: 860 } })).newPage();
  await ph.goto(URL + '#case_63'); await ph.waitForTimeout(400);
  log('B4 phone deep link dossier top', await ph.evaluate(() => Math.round(document.getElementById('dossier').getBoundingClientRect().top)));
  await ph.screenshot({ path: SH + '400_deeplink_case63.png' });
  await ph.evaluate(() => scrollTo(0, 0)); await ph.fill('#q', 'case_35'); await ph.click('#list .item'); await ph.waitForTimeout(400);
  log('B4 phone tap dossier top', await ph.evaluate(() => Math.round(document.getElementById('dossier').getBoundingClientRect().top)));
  await ph.screenshot({ path: SH + '400_after_tap_case35.png' });
  log('page errors', errs);
  require('fs').writeFileSync('/home/user/DSProjects/hackathons/hackerrank-orchestrate-oct26/review/ui_log_final.txt', out.join('\n') + '\n');
  await b.close();
})();
