const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
  await p.goto('file:///tmp/cr2/code/ui/ghost_ledger.html'); await p.waitForTimeout(300); await p.click('#maskbtn');
  await p.fill('#q', 'haruka.s1838'); await p.waitForTimeout(100); console.log('unmasked haruka.s1838 ->', await p.$$eval('#list .item', a => a.map(x => x.dataset.id)));
  await b.close(); })();
