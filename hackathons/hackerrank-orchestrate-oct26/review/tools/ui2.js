const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const id of ['case_63', 'case_550', 'case_999']) { const p = await (await b.newContext()).newPage();
    await p.goto('file:///tmp/cr/code/ui/ghost_ledger.html#' + id); await p.waitForTimeout(300);
    console.log('fresh deep link', id, '->', await p.$eval('#dossier h2', e => e.textContent), 'list aria-current visible:', await p.$$eval('#list .item[aria-current="true"]', a => a.map(x => x.dataset.id))); }
  const p = await (await b.newContext({ viewport: { width: 400, height: 860 } })).newPage();
  await p.goto('file:///tmp/cr/code/ui/ghost_ledger.html#case_63'); await p.waitForTimeout(300);
  await p.screenshot({ path: '/home/user/DSProjects/hackathons/hackerrank-orchestrate-oct26/review/screens/400_deeplink_case63.png' });
  console.log('phone deep link: dossier top', await p.evaluate(() => Math.round(document.getElementById('dossier').getBoundingClientRect().top)), 'docHeight', await p.evaluate(() => document.documentElement.scrollHeight));
  await b.close(); })();
