// Builds Jannet's résumé (the one the portfolio links) as a .docx in her Word layout:
// name + contact in the page header, then one bordered table with grey section bars,
// a label column for skills, numbered builds and ❖ bullets. One generic version for
// forward deployed, applied AI/ML and data roles (Jannet, 11-19). LibreOffice renders the PDF.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, AlignmentType, Header, ExternalHyperlink, LevelFormat, VerticalAlign, TableLayoutType,
} = require('docx');

const OUT = process.argv[2] || require('path').join(__dirname, '..', 'resumes', 'Jannet_Ekka_Resume.docx');
const FONT = 'Calibri';
const SZ = 19;            // body 9.5 pt (half-points)
const W = 11906 - 2 * 454; // A4 width minus 0.8 cm margins
const LBL = 1500, VAL = W - LBL;
const GREY = 'E7E6E6', LIGHT = 'F2F2F2';
const B = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
const BORDERS = { top: B, bottom: B, left: B, right: B };
const MARG = { top: 10, bottom: 10, left: 90, right: 90 };

// --- inline text: [text, {b,i,link}] pieces -----------------------------------------
function runs(parts, base = {}) {
  return parts.map(p => {
    if (typeof p === 'string') p = [p, {}];
    const [text, o] = p;
    const r = { text, font: FONT, size: o.size || base.size || SZ, bold: o.b ?? base.b, italics: o.i ?? base.i };
    if (o.link) return new ExternalHyperlink({ link: o.link, children: [new TextRun({ ...r, style: 'Hyperlink' })] });
    return new TextRun(r);
  });
}
const para = (parts, o = {}) => new Paragraph({
  children: runs(parts, o), alignment: o.align, keepNext: o.keep, keepLines: true, spacing: { before: 0, after: 0, line: o.line || 238 },
  numbering: o.bullet ? { reference: o.bullet, level: 0 } : undefined,
});
function cell(children, o = {}) {
  return new TableCell({
    children: Array.isArray(children) ? children : [children],
    columnSpan: o.span, width: { size: o.w || W, type: WidthType.DXA }, borders: BORDERS, margins: MARG,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    verticalAlign: o.v || VerticalAlign.TOP,
  });
}
const full = (children, o = {}) => new TableRow({ cantSplit: true, children: [cell(children, { ...o, span: 2, w: W })] });
const section = t => full(para([[t, { b: true, size: 21 }]], { keep: true }), { fill: GREY });
const head = parts => full(para(parts.map(p => typeof p === 'string' ? [p, { b: true }] : [p[0], { b: true, ...p[1] }]), { keep: true }), { fill: GREY });
const sub = parts => full(para(parts), {});
const bullets = items => full(items.map(t => para(t, { bullet: 'diamond' })));
const skill = (k, v) => new TableRow({ cantSplit: true, children: [
  cell(para([[k, { b: true, i: true }]], { align: AlignmentType.CENTER }), { w: LBL, v: VerticalAlign.CENTER }),
  cell(para([v]), { w: VAL }),
]});
// a "Live: … · Code: …" row
function links(items) {
  const parts = [];
  items.forEach(([lbl, text, url], i) => {
    if (i) parts.push(' · ');
    if (lbl) parts.push([lbl + ': ', { b: true, i: true }]);
    parts.push([text, { link: url }]);
  });
  return full(para(parts, { keep: true }));
}
const GH = 'https://github.com/JannetEkka/';


// Where Jannet will work from.
const LOCATION = 'Kolkata, India · remote or relocation';

// --- content ----------------------------------------------------------------------------
const rows = [];
rows.push(section('PROFESSIONAL SUMMARY'));
rows.push(full(para([
  ['I build AI and ML systems, test them against the obvious baseline, and keep them working where other people use them.', { b: true }],
  " For about four years at Deloitte I was the engineer on the calls with Fortune 500 client teams (AT&T, Hewlett Packard Enterprise), in US, UK and India hours, and led a 6-person QA team. Rank 1 in the UT Austin McCombs Post Graduate Program in AI/ML (GPA 4.09/5). Since 2024 I have built and run a live AI trading system alone; when I graded its six AI agents on independent data, all six called direction at a coin flip, so I rebuilt it around written rules and a statistical gate every model change must pass. Between Oct 12 and Nov 15, 2026 I built and submitted 19 working products and a paper to 21 hackathons, each on its sponsor's platform (GitLab Duo, Meta, NVIDIA Nemotron, Fire TV, FalkorDB, Mozaik and others). Python and SQL every day.",
], { align: AlignmentType.JUSTIFIED })));

rows.push(section('TECHNICAL SKILLS'));
rows.push(skill('Client Delivery', 'Demos, working sessions and requirement calls with client teams across US, UK and India hours; scoping a build to a fixed deadline; defect triage with client engineers; weekend on-call; READMEs, technical reports and demo videos for the people who use the system'));
rows.push(skill('AI & Agents', 'Gemini (Vertex AI, AI Studio), Claude, NVIDIA Nemotron, Meta Muse, Google ADK, GitLab Duo flows, Mozaik concurrent agents, MCP (servers written from scratch), tool calling, structured output, RAG with measured retrieval, FalkorDB graph agents (Cypher), llama.cpp'));
rows.push(skill('ML & Evaluation', 'scikit-learn, XGBoost, CatBoost, Random Forest and boosting, SMOTE, Optuna, TensorFlow, PyTorch, Hugging Face; held-out and forward tests, paired bootstrap confidence intervals, ROC-AUC, recall@k and MRR, event studies against base rates, CPCV, Deflated Sharpe, PBO, FDR control, leakage checks'));
rows.push(skill('Data', 'SQL (window functions, joins), BigQuery, DuckDB, Postgres, Firestore, pandas; pipelines over public APIs that rebuild byte for byte from a snapshot; GitHub Actions schedules. Not used yet: dbt, Trino, Databricks'));
rows.push(skill('Deployment', 'Oracle Cloud (free VM, systemd), Cloudflare Workers, Pages and KV, Render, GitHub Actions; GCP: Cloud Run, Compute Engine, Vertex AI, BigQuery, AlloyDB & pgvector; AWS: S3, EC2, RDS; Docker, including offline networks'));
rows.push(skill('Engineering', 'Python, SQL, TypeScript and JavaScript; Kotlin for one shipped Android app. FastAPI, Flask, Streamlit, React, Next.js, Solidity. Test strategy, pytest (3,000+ tests on one system), Selenium, Jenkins'));

rows.push(section('PRODUCTION SYSTEM'));
rows.push(head(['Smart Money Trading (SMT): an explainable AI trading agent · Founder & sole engineer | Jan 2024 – Present']));
rows.push(sub([['Patent pending: Indian provisional application No. 202631090789, filed myself in July 2026. Shortlisted for the Google AI Startup Buildathon India 2026', { b: true, i: true }]]));
rows.push(links([['Live', 'SMT World', 'https://smt-weex-trading-bot.jannet-ekka.workers.dev/'], ['Public layer', 'github.com/JannetEkka/smt-apac', GH + 'smt-apac'], [null, 'WEEX feature', 'https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641']]));
rows.push(bullets([
  ["Runs 24/7 and places real orders on WEEX's exchange-granted simulated account (about $10K). Built alone by specifying the work and directing AI coding agents: ", ['about 88,000 lines of Python, 3,152 tests, 362 merged pull requests', { b: true }], ', each reviewed by me before merge.'],
  ['Graded my own six AI agents on independent market data: ', ['all six called direction at a coin flip', { b: true }], '. So written rules now open every trade, the agents are advisors graded on every call, and every explanation passes a counterfactual test.'],
  ['A model change reaches the live system only through a CPCV + Deflated Sharpe + PBO + FDR gate. A forecaster that scored ', ['AUC 0.723', { b: true }], ' on a BTC forward test over 27 non-overlapping windows is still held in shadow because it has not passed.'],
  ['When the GCP billing account closed, I ', ['moved the live system to a zero-cost stack in two days', { b: true }], ': an Oracle free-tier VM under systemd, Cloudflare Workers and GitHub Actions. It re-adopted its three open positions from committed state.'],
  ['Audited 98 AI-written merges line by line and found an order-format bug that had ', ['rejected 1,137 live orders over three months', { b: true }], ' while every test passed. A fix now counts as done only when the production log shows it.'],
  ['Built ', ['SMT World', { b: true }], ', the product for users: a Three.js world on Cloudflare Workers where people watch the agent trade and ask it why, answered by Gemini from the live book.'],
]));

rows.push(section('SELECTED BUILDS'));
let n = 0;
const build = (title, org, when, linkItems, items) => {
  n += 1;
  rows.push(head([`${n}.  ${title} · ${org} | ${when}`]));
  if (linkItems) rows.push(links(linkItems));
  rows.push(bullets(items));
};
build('Proof of Fix: issues close on production evidence, not on merge', 'GitLab AI Hackathon (Duo Agent Platform)', 'Oct 2026',
  [['Live', 'the real run on GitLab', 'https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase/-/work_items/2'], ['Code', 'GitLab project', 'https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase'], [null, 'Demo video', 'https://youtu.be/tec52HoWT5A']],
  [
    ['A GitLab Duo flow reads production logs when a bug is filed and writes a proof contract into the issue; after deploy, the pipeline judges the shipped build on its own logs. Real run: a fix that passed the tests and Duo Code Review cut failures only ', ['from 32% to 9%', { b: true }], ", so the issue stayed open; the Duo Developer flow's second fix reached ", ['0 failures on 875 requests', { b: true }], '.'],
  ]);
build('Chithi: official Indian letters explained, every number checked', 'Meta Global AI Developer Hackathon (Cerebral Valley)', 'Nov 2026',
  [['Live', 'chithi-oprj.onrender.com', 'https://chithi-oprj.onrender.com'], ['Code', 'github.com/JannetEkka/chithi', GH + 'chithi'], [null, 'Demo video', 'https://youtu.be/wlRwfQghgOw']],
  [
    ['A phone photo of a bill or notice, explained in Bengali, Hindi or English on SAM 3.1 and Muse Spark. A check with no model requires every date and amount to be in the quote and in a second reading; 28 live explanations, ', ['0 of 114 values shown wrong', { b: true }], '.'],
  ]);
build('Lore: backtesting an agent against the obvious baseline', 'Graph Hacks, FalkorDB × WeMakeDevs', 'Oct 2026 · 4 days',
  [['Live', 'lore-gh5y.onrender.com', 'https://lore-gh5y.onrender.com/'], ['Code', 'github.com/JannetEkka/lore', GH + 'lore']],
  [
    ['1,357 of the sponsor\'s own PRs in a FalkorDB graph; a Gemini agent answers "who should review this?" through 12 Cypher tools and cites the PRs. Backtested on 300 real PRs: a real reviewer in its top three ', ['90%', { b: true }], ' of the time, against 88% for "the most frequent reviewer". On the single top pick the baseline wins, and the write-up says so.'],
  ]);
build('SmartDesk: a measured comparison that kept the baseline', 'Google Cloud Gen AI Academy APAC, top 101 of 1,500+', '2026',
  [['Code', 'github.com/JannetEkka/smartdesk', GH + 'smartdesk']],
  [
    ['Built the eval set before touching retrieval: 40 labelled questions, paired bootstrap at 10,000 resamples. A reranker won on the development embedder (MRR@10 +0.094, p=0.04), then fell to +0.028 with a CI spanning zero in production, while search went from 29 ms to 2,382 ms. ', ['The baseline shipped.', { b: true }]],
  ]);
build('Aftershock: does news move real usage? An event study', 'NEAR Hackathon, Investment Thesis track', 'Nov 2026',
  [['Live', 'jannetekka.github.io/aftershock', 'https://jannetekka.github.io/aftershock/'], ['Code', 'github.com/JannetEkka/aftershock', GH + 'aftershock']],
  [
    ['Joined 2,305 days of NearBlocks chain data, DefiLlama and GDELT news counts into one snapshot that rebuilds byte for byte. Of 74 news spikes, 8 moved the price (10.8%, against 5.1% of ordinary days) and 10 moved usage (13.5%, against 16.5%): ', ['usage did not follow the headlines', { b: true }], ', and the thesis says so.'],
  ]);
build('Spona: concurrent agents that match researchers with companies', 'NTP Novi Sad Hackathon (JigJoy × Mozaik)', 'Oct 2026',
  [['Live', 'jannetekka.github.io/spona', 'https://jannetekka.github.io/spona/'], ['Code', 'github.com/JannetEkka/spona', GH + 'spona']],
  [
    ['12 agents read 1,047 researchers, 10,779 papers and 489 company challenges in English and Serbian (Latin and Cyrillic) and gave every challenge an outcome in ', ['5 min 48 s for $1.52', { b: true }], '. A critic checked every claim against its source while the others worked and sent back 33.'],
  ]);
build('Lights Out: a Hermes Agent plugin that asks before spending', 'Nous Research Hermes Agent Plugin Hackathon', 'Nov 2026',
  [['Code', 'github.com/JannetEkka/lights-out', GH + 'lights-out'], [null, 'Merged into the official Hermes plugin catalog (PR #153822)', 'https://github.com/NousResearch/hermes-agent/pull/153822']],
  [
    ['Measured on 10 tasks × 3 arms: without the plugin the agent ran 13 and 14 billable AWS creates that no person approved; with it, ', ['0', { b: true }], '. One command then left 0 resources running, keeping the 2 marked to stay.'],
  ]);
rows.push(full(para([
  ['Portfolio models (UT Austin PGP, 2024–25): ', { b: true }],
  'telecom churn, Random Forest 81.48% test accuracy (for a retention budget I would report recall on churners and lift); NBFC loan default; semiconductor yield on 591 sensor signals, where I later found SMOTE applied before the split, so the reported 99.2% is inflated; SVHN digits, 87.1% on 18,000 images; financial-news sentiment.',
])));
rows.push(full(para([
  ['Also shipped, Oct–Nov 2026: ', { b: true }],
  'Footfall (Qloo + Nemotron, a $15 spend cap, $0.45 spent) · Aside (Fire TV, spoilers 6 of 16 → 0 of 16) · Klarbrief (Swiss letters offline on a 4-core CPU, 0 wrong CHF amounts on 48) · Orbit (Catalyst, one-day solo build, top 8.2% of 391) · Countersign (41 of 60 planted errors caught) · Pitch In (PayPal) · a Kaggle paper on Gemma 4 coding agents · Wiretrap · SMT Receipts · SMT World: Clock In (Android) · SQL Noir · Afterburn · Recourse (Round 2) · Beauty Within · Ghost Ledger. All at ',
  ['jannetekka.cv', { link: 'https://jannetekka.cv/' }],
])));

rows.push(section('PROFESSIONAL EXPERIENCE'));
rows.push(head(['Deloitte Consulting LLP · Test Automation Engineer (Analyst) | Aug 2019 – Jan 2023 · Bangalore']));
rows.push(bullets([
  [['Client-facing throughout', { b: true }], ': demos, working sessions and requirement calls in US, UK and India hours for Fortune 500 accounts including AT&T Consumer Connect, Hewlett Packard Enterprise and The Dental Supply Company; weekend on-call. ', ['Led a 6-member QA engineering team', { b: true }], '.'],
  ['Built Selenium and Katalon Studio automation that ', ['improved test execution efficiency by 83%;', { b: true }], ' Jenkins-based reporting cut manual analysis time by ', ['75%', { b: true }], '.'],
  ['Wrote Python analysis and Tableau dashboards tracking quality across ', ['343 business components', { b: true }], ', cutting test failures by 25%; analysed ', ['50,000+ SAP Hybris transactions', { b: true }], ' to isolate performance bottlenecks for the client.'],
  ['Joined as a QA automation intern in Jan 2019; converted to analyst after six months. 2 Spot Awards and an Applause Award.'],
]));
rows.push(head(['AutoKorrekt · Lead Frontend Developer (EdTech startup MVP) | May 2023 – Jan 2024']));
rows.push(bullets([['Led the Next.js frontend of an AI answer-evaluation platform for teachers: OCR validation flows, JWT auth, bulk answer-sheet upload, over a backend using ', ['AWS Textract', { b: true }], ', Amazon Comprehend, S3, RDS and SageMaker.']]));
rows.push(head(['JTech Solutions (pre-incorporation) · Founder & AI Engineer | Jan 2024 – Present · Kolkata']));
rows.push(bullets([['Building SMT (above) as the first product, while a full-time family carer and alongside the PGP in AI/ML.']]));

rows.push(section('EDUCATION'));
rows.push(sub([['Post Graduate Program (PGP) in AI/ML | UT Austin McCombs / Great Lakes Executive Learning (Feb 2024 – Mar 2025)', { b: true, i: true }]]));
rows.push(sub(['RANK 1 / COHORT TOPPER (Specialization in Deep Learning, NLP, and Data Modeling): GPA 4.09/5']));
rows.push(sub([['Bachelor of Technology (B.Tech), Information Technology | Graduated 2019', { b: true, i: true }]]));
rows.push(sub(['Kalinga Institute of Industrial Technology University, Bhubaneswar: CGPA 7.17/10']));

rows.push(section('CERTIFICATIONS & ACHIEVEMENTS'));
rows.push(full([
  [['WEEX AI Wars I: #1 on the preliminary leaderboard', { b: true }], ' of 230+ teams, then one of 37 finalists in the live AI trading competition; featured in ', ["WEEX's coverage", { link: 'https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641' }], '.'],
  [['Winner, Best DeFi Application', { b: true }], ', OpenServ × Hack2skill hackathon; ', ['top 101 of 1,500+ teams', { b: true }], ', Google Cloud Gen AI Academy APAC 2026 Cohort 1 (SmartDesk).'],
  [['Kaggle RSNA Knee Abnormality Detection', { b: true }], ' (5,900+ teams, not placed): scored two candidate label sets against 58 radiologist labels (macro AUC 0.894 against 0.870) before retraining on the better one.'],
  [['Google Cloud Gen AI Academy', { b: true }], ' 2025 and APAC 2026 Cohorts 1–3; CPSAT (Selenium), 2022. All on ', ['Credly', { link: 'https://www.credly.com/users/jannet-akanksha-ekka/badges' }], ' and ', ['Google Skills', { link: 'https://www.skills.google/public_profiles/2a91b2f0-31d3-467e-ba45-3ba1888a908e' }], '.'],
].map(t => para(t, { bullet: 'dot' }))));

// --- header (repeats on every page) ---------------------------------------------------
const header = new Header({ children: [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [new TextRun({ text: 'JANNET AKANKSHA EKKA', font: 'Calibri Light', size: 44 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: runs([
    'jannetekka96@gmail.com | +91 90788 02572 | ',
    ['LinkedIn', { link: 'https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/' }], ' | ',
    ['GitHub', { link: 'https://github.com/JannetEkka' }], ' | ',
    ['Portfolio', { link: 'https://jannetekka.cv/' }], ' | ' + LOCATION,
  ], { size: 21 }) }),
]});

const doc = new Document({
  creator: 'Jannet Ekka', title: 'Jannet Akanksha Ekka - Resume',
  styles: { default: { document: { run: { font: FONT, size: SZ } } } },
  numbering: { config: [
    { reference: 'diamond', levels: [{ level: 0, format: LevelFormat.BULLET, text: '❖', alignment: AlignmentType.LEFT,
      style: { run: { font: 'Segoe UI Symbol', size: 16 }, paragraph: { indent: { left: 300, hanging: 260 } } } }] },
    { reference: 'dot', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 300, hanging: 260 } } } }] },
  ]},
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 380, left: 454, right: 454, header: 280, footer: 200 } } },
    headers: { default: header },
    children: [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [LBL, VAL], layout: TableLayoutType.FIXED, rows })],
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('wrote', OUT); });
