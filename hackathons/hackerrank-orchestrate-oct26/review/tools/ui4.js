const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
  await p.goto('file:///tmp/cr2/code/ui/ghost_ledger.html'); await p.waitForTimeout(300);
  for (const q of ['amara-okeke', 'amara-okeke@proton.me', 'okeke', 'haruka.s1838']) { await p.fill('#q', q); await p.waitForTimeout(100);
    console.log(`masked "${q}" ->`, await p.$$eval('#list .item', a => a.map(x => x.dataset.id).slice(0, 3)), 'msg:', await p.$eval('#list', e => e.innerText.slice(0, 120).replace(/\n/g, ' '))); }
  await b.close(); })();
