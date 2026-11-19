// Builds Jannet's Data Scientist résumé (insurtech data roles, first sent to Ominimo via JigJoy, 11-2026)
// as a .docx in the same layout as her Word FDE version:
// name + contact in the page header, then one bordered table with grey section bars,
// a label column for skills, numbered builds and ❖ bullets.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, AlignmentType, Header, ExternalHyperlink, LevelFormat, VerticalAlign, TableLayoutType,
} = require('docx');

const OUT = process.argv[2] || require('path').join(__dirname, '..', 'resumes', 'Jannet_Ekka_Resume_Data_Science.docx');
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

// --- content ----------------------------------------------------------------------------
// Where Jannet will work from. Set from her answer before sending (remote only, or relocation).
const LOCATION = 'Kolkata, India · remote or relocation';
const rows = [];
rows.push(section('PROFESSIONAL SUMMARY'));
rows.push(full(para([
  ['I build predictive models on tabular data and then try to break them before anyone relies on them.', { b: true }],
  ' Rank 1 in the UT Austin McCombs Post Graduate Program in AI/ML (GPA 4.09/5). Since 2024 I have built and run a live trading system alone: when I graded its six AI agents on independent data, all six called direction at a coin flip, so I rebuilt it around rules and a statistical gate that every model change must pass. Before that, four years at Deloitte leading test automation for Fortune 500 clients. I work in Python and SQL, from raw public data to a pipeline someone else can rerun. The questions an insurer\'s data team asks (who will claim, who will leave, did the change help) are the ones I have practised: default and churn models, tests against the obvious baseline, and comparisons with confidence intervals.',
], { align: AlignmentType.JUSTIFIED })));

rows.push(section('TECHNICAL SKILLS'));
rows.push(skill('Modelling', 'Classification and regression on tabular data: Random Forest, gradient boosting, XGBoost, CatBoost, AdaBoost, SVM, K-Means and PCA; class imbalance (SMOTE, SMOTETomek); tuning with GridSearchCV and Optuna; neural nets in TensorFlow and PyTorch'));
rows.push(skill('Statistics & Evaluation', 'Hypothesis tests, paired bootstrap confidence intervals, held-out and forward tests, event studies against base rates, ROC-AUC, recall@k and MRR, CPCV, Deflated Sharpe, PBO, FDR control, leakage checks, monitoring a model from production logs'));
rows.push(skill('Data Engineering', 'SQL (window functions, joins, result-set comparison), BigQuery (through Google\'s BigQuery MCP server), DuckDB, Postgres, Firestore, pandas; pipelines over public APIs that rebuild byte for byte from a snapshot; GitHub Actions schedules; Docker. I have not used dbt, Trino or Databricks yet'));
rows.push(skill('ML & AI Stack', 'scikit-learn, imbalanced-learn, Hugging Face, Gemini (Vertex AI), Claude, NVIDIA Nemotron, LLM agents with tool calling, RAG with measured retrieval, MCP; GCP (Cloud Run, Vertex AI, BigQuery), AWS (S3, EC2, RDS)'));
rows.push(skill('Languages', 'Python and SQL every day. TypeScript and JavaScript shipped in several projects'));

rows.push(section('QUANT MODELLING IN PRODUCTION'));
rows.push(head(['Smart Money Trading (SMT): an explainable AI trading agent · Founder & sole engineer | Jan 2024 – Present']));
rows.push(sub([['Patent pending: Indian provisional application No. 202631090789, filed myself in July 2026', { b: true, i: true }]]));
rows.push(links([['Live', 'SMT World', 'https://smt-weex-trading-bot.jannet-ekka.workers.dev/'], ['Public layer', 'github.com/JannetEkka/smt-apac', GH + 'smt-apac']]));
rows.push(bullets([
  ["Runs 24/7 and places real orders on WEEX's exchange-granted simulated account (about $10K). Built alone, directing AI coding agents: ", ['about 88,000 lines of Python and 3,152 tests', { b: true }], '.'],
  ['Graded my own six AI agents on independent market data: ', ['all six called direction at a coin flip', { b: true }], '. So written rules now open every trade, and the agents became advisors graded on every call.'],
  ['A model change reaches the live system only through a CPCV + Deflated Sharpe + PBO + FDR gate. A forecaster that scored ', ['AUC 0.723', { b: true }], ' on a BTC forward test over 27 non-overlapping windows is still held in shadow because it has not passed.'],
  ['Tested ', ['1,800 strategy variants, 36 million simulated trades', { b: true }], " (2020–2026, six exchanges' published fees), replayed through the production code. Nothing holding a position under four hours cleared its fees, so none of those strategies went live."],
  ['Data quality: any substituted default must log a warning and a liveness flag, a rule written after four multi-week data bugs ran silently; a September audit found 17 more silent failure paths. An audit of 98 AI-written merges found an order-format bug that had ', ['rejected 1,137 live orders', { b: true }], ' while every test passed.'],
]));
rows.push(sub([['Stack: ', { b: true }], 'Python, pandas, scikit-learn, CatBoost, Optuna, DuckDB, Gemini, Oracle Cloud, Cloudflare Workers, GitHub Actions, pytest']));

rows.push(section('SELECTED DATA SCIENCE WORK'));
let n = 0;
const build = (title, org, when, linkItems, items) => {
  n += 1;
  rows.push(head([`${n}.  ${title} · ${org} | ${when}`]));
  if (linkItems) rows.push(links(linkItems));
  rows.push(bullets(items));
};
build('Aftershock: does news move real usage? An event study', 'NEAR Hackathon, Investment Thesis track', 'Nov 2026 · submitted',
  [['Live', 'jannetekka.github.io/aftershock', 'https://jannetekka.github.io/aftershock/'], ['Code', 'github.com/JannetEkka/aftershock', GH + 'aftershock']],
  [
    ['Joined three free public sources (2,305 days of NearBlocks chain data, DefiLlama, GDELT news counts) into one snapshot that rebuilds byte for byte with no keys and no network.'],
    ['Tested 74 news spikes against ordinary days: 8 moved the price (10.8%, against 5.1% of ordinary days), 10 moved usage (13.5%, against 16.5%). ', ['Usage did not follow the headlines', { b: true }], ', and the published thesis says so. Every claim is recomputed and checked by a second model: 14 of 20 kept. Asked alone, the model got 1 of 20 numbers right.'],
  ]);
build('Portfolio models', 'UT Austin McCombs PGP in AI/ML and Great Learning', '2024 – 2025',
  [['Code', 'jannetekka.cv', 'https://jannetekka.cv/']],
  [
    [['Customer churn (telecom retention):', { b: true }], ' Decision Tree, Random Forest, AdaBoost and gradient boosting, tuned with grid search; Random Forest best at 81.48% test accuracy. Churners are the minority, so for a retention budget I would report recall on churners and lift over random targeting, and the write-up says so.'],
    [['NBFC loan default (credit risk, Great Learning hackathon):', { b: true }], ' a default classifier on lender data, a TensorFlow network with early stopping. Today I would benchmark gradient-boosted trees first, since they usually win on tabular credit data.'],
    [['Semiconductor yield (1,567 runs, 591 sensor signals):', { b: true }], ' feature selection, SMOTE and PCA. Reviewing it later, I found SMOTE applied before the train/test split, so the reported 99.2% is inflated; the fix is resampling inside the training fold only.'],
    [['Also:', { b: true }], ' SVHN digits, 87.1% test accuracy on 18,000 images; financial-news sentiment, XGBoost test F1 0.378 where validation had shown 0.46–0.52; YouTube ad-view regression on 15,000+ videos; quarter-over-quarter revenue analysis in SQL.'],
  ]);
build('Lore: backtesting an agent against the obvious baseline', 'Graph Hacks, FalkorDB × WeMakeDevs', 'Oct 2026',
  [['Live', 'lore-gh5y.onrender.com', 'https://lore-gh5y.onrender.com/'], ['Code', 'github.com/JannetEkka/lore', GH + 'lore']],
  [
    ['A Gemini agent answers "who should review this?" from a graph of 1,357 pull requests. Backtested on 300 real PRs: a real reviewer in its top three ', ['90%', { b: true }], ' of the time, against 88% for "the most frequent reviewer". On the single top pick the baseline wins, and the write-up says so. Ported to the Anna app store; Anna\'s review called the concept "fantastic" and asked for one fix, now resubmitted.'],
  ]);
build('SmartDesk: a measured comparison that kept the baseline', 'Google Cloud Gen AI Academy APAC, top 101 of 1,500+', '2026',
  [['Code', 'github.com/JannetEkka/smartdesk', GH + 'smartdesk']],
  [
    ['Built the eval set before touching retrieval: 40 labelled questions, paired bootstrap at 10,000 resamples. A reranker won on the development embedder (MRR@10 +0.094, p=0.04), then fell to +0.028 with a CI spanning zero in production, while search went from 29 ms to 2,382 ms. ', ['The baseline shipped.', { b: true }]],
  ]);
build('Lights Out: a Hermes Agent plugin that asks before spending', 'Nous Research Hermes Agent Plugin Hackathon', 'Nov 2026 · submitted',
  [['Code', 'github.com/JannetEkka/lights-out', GH + 'lights-out'], [null, 'Merged into the official Hermes plugin catalog (PR #153822)', 'https://github.com/NousResearch/hermes-agent/pull/153822']],
  [
    ['Measured on 10 tasks × 3 arms against a local AWS emulator: in the two arms without the plugin, the agent ran 13 and 14 billable creates that no person approved; with it, ', ['0', { b: true }], '. One command then left 0 resources running, keeping the 2 marked to stay. A clean-up prompt alone also cleaned up well, and the README says that too.'],
  ]);
build('Spona: matching researchers with companies', 'NTP Novi Sad Hackathon (JigJoy × Mozaik)', 'Oct 2026 · not placed',
  [['Live', 'jannetekka.github.io/spona', 'https://jannetekka.github.io/spona/'], ['Code', 'github.com/JannetEkka/spona', GH + 'spona']],
  [
    ['12 concurrent agents read 1,047 researchers, 10,779 papers and 489 company challenges in English, Serbian Latin and Cyrillic, and gave every challenge an outcome in ', ['5 min 48 s for $1.52', { b: true }], '. BM25 matching with the two scripts folded together; a critic checked every claim against its source and sent back 33.'],
  ]);
rows.push(full(para([
  ['Also in Nov 2026: ', { b: true }],
  'Catalyst Solo AI Hackathon (one-day solo build): Orbit, an elder-care medication app, top 8.2% (33rd of 391 scored entries; 96.64 against the winner\'s 97.21), not placed · Chithi (Meta): 0 of 114 dates and amounts shown wrong on 28 live runs · Pitch In (PayPal AI), Countersign (Mozilla Otari) and Beauty Within (YouCam): submitted, results pending. All at ',
  ['jannetekka.cv', { link: 'https://jannetekka.cv/' }],
])));

rows.push(section('PROFESSIONAL EXPERIENCE'));
rows.push(head(['Deloitte Consulting LLP · Test Automation Engineer (Analyst) | Aug 2019 – Jan 2023 · Bangalore']));
rows.push(bullets([
  [['Led a 6-member QA engineering team', { b: true }], ' on automated testing for Fortune 500 clients including AT&T Consumer Connect and Hewlett Packard Enterprise; demos and requirement calls in US, UK and India hours.'],
  ['Wrote Python analysis and Tableau dashboards tracking quality across ', ['343 business components', { b: true }], ', cutting test failures by 25%; analysed ', ['50,000+ SAP Hybris transactions', { b: true }], ' to find performance bottlenecks.'],
  ['Selenium and Katalon Studio automation ', ['improved test execution efficiency by 83%;', { b: true }], ' Jenkins reporting cut manual analysis time by ', ['75%', { b: true }], '. 2 Spot Awards and an Applause Award.'],
]));
rows.push(head(['AutoKorrekt · Lead Frontend Developer (EdTech startup MVP) | May 2023 – Jan 2024']));
rows.push(bullets([['Led the Next.js frontend of an AI answer-evaluation platform for teachers, over AWS Textract, Amazon Comprehend, S3, RDS and SageMaker.']]));
rows.push(head(['JTech Solutions (pre-incorporation) · Founder & AI Engineer | Jan 2024 – Present · Kolkata']));
rows.push(bullets([['Building SMT (above) as the first product, while a full-time family carer and alongside the PGP in AI/ML.']]));

rows.push(section('EDUCATION'));
rows.push(sub([['Post Graduate Program (PGP) in AI/ML | UT Austin McCombs / Great Lakes Executive Learning (Feb 2024 – Mar 2025)', { b: true, i: true }]]));
rows.push(sub(['RANK 1 / COHORT TOPPER (Specialization in Deep Learning, NLP, and Data Modeling): GPA 4.09/5']));
rows.push(sub([['Bachelor of Technology (B.Tech), Information Technology | Graduated 2019', { b: true, i: true }]]));
rows.push(sub(['Kalinga Institute of Industrial Technology University, Bhubaneswar: CGPA 7.17/10']));

rows.push(section('CERTIFICATIONS & ACHIEVEMENTS'));
rows.push(full([
  [['WEEX AI Wars I: #1 on the preliminary leaderboard', { b: true }], ' of 230+ teams, then one of 37 finalists in the live AI trading competition.'],
  [['Winner, Best DeFi Application', { b: true }], ', OpenServ × Hack2skill hackathon; ', ['top 101 of 1,500+ teams', { b: true }], ', Google Cloud Gen AI Academy APAC 2026 Cohort 1.'],
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
  creator: 'Jannet Ekka', title: 'Jannet Akanksha Ekka - Resume (Data Scientist)',
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
