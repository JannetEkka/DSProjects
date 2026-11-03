// Builds Jannet's FDE résumé as a .docx in the same layout as her Word version:
// name + contact in the page header, then one bordered table with grey section bars,
// a label column for skills, numbered builds and ❖ bullets.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, AlignmentType, Header, ExternalHyperlink, LevelFormat, VerticalAlign, TableLayoutType,
} = require('docx');

const OUT = process.argv[2] || require('path').join(__dirname, '..', 'resumes', 'Jannet_Ekka_Resume_FDE.docx');
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
const rows = [];
rows.push(section('PROFESSIONAL SUMMARY'));
rows.push(full(para([
  ["I put AI systems into other people's environments and keep them working there.", { b: true }],
  " For about four years at Deloitte, I was the engineer on the calls with Fortune 500 client teams (AT&T, Hewlett Packard Enterprise), running demos and requirement sessions in US, UK and India hours and leading a 6-person QA team. Since 2024, alongside the Post Graduate Program and full-time family care, I have built and run a live AI trading agent on my own as a side project; when its cloud billing closed, I moved it to a new stack in two days and it picked its open positions back up from committed state. Between Oct 12 and Nov 2, 2026 I built and submitted 13 working products to 14 hackathons, each on its sponsor's platform (GitLab Duo, Fire TV, NVIDIA Nemotron, Qloo, FalkorDB, Solana Mobile, Monad and others), each with its code, a working build and a demo. Rank 1 in the UT Austin McCombs Post Graduate Program in AI/ML.",
], { align: AlignmentType.JUSTIFIED })));

rows.push(section('TECHNICAL SKILLS'));
rows.push(skill('Client Delivery', 'Demos, working sessions and requirement calls with client teams across US, UK and India hours; scoping a build to a fixed deadline; defect triage with client engineers; weekend on-call; writing for the people who will use the system: READMEs, technical reports, demo videos, blog posts'));
rows.push(skill('AI & Agents', 'Gemini (Vertex AI, AI Studio), Claude, NVIDIA Nemotron, Google ADK, GitLab Duo flows, Mozaik concurrent agents, MCP (servers written from scratch), tool calling, structured output, RAG with measured retrieval, FalkorDB graph agents (Cypher), llama.cpp (Apertus 1.5 8B)'));
rows.push(skill('Integrations', 'GitHub API and sign-in, GitLab CI and Flows API, Gmail and Calendar via MCP, BigQuery and Maps MCP, Qloo, YouCam, Zetaris, Solana Mobile Wallet Adapter, EVM contracts with RedStone oracles and Envio, Fire TV (Vega OS), AWS Textract'));
rows.push(skill('Deployment', 'Oracle Cloud (free VM, systemd), Cloudflare Workers, Pages and KV, Render, GitHub Actions; GCP: Cloud Run, Compute Engine, Vertex AI, BigQuery, AlloyDB & pgvector, Firestore, Workload Identity Federation; AWS: S3, EC2, RDS; Docker, including offline networks'));
rows.push(skill('Engineering', 'Python, SQL, TypeScript and JavaScript. Kotlin and Jetpack Compose for one shipped Android app. FastAPI, Flask, Streamlit, Django, React, Next.js, Postgres, DuckDB, Solidity'));
rows.push(skill('Testing', 'Test strategy, pytest (3,000+ tests on one system), Selenium, Katalon Studio, Jenkins, LLM evals (held-out sets, paired bootstrap, baselines), production log checks before a fix is called done'));

rows.push(section('PRODUCTION SYSTEM'));
rows.push(head(['Smart Money Trading (SMT) — Explainable AI Trading Agent · Side project, sole engineer | Jan 2024 – Present']));
rows.push(sub([['Patent pending: Indian provisional application No. 202631090789, filed myself in July 2026', { b: true, i: true }]]));
rows.push(links([['Live', 'SMT World', 'https://smt-weex-trading-bot.jannet-ekka.workers.dev/'], ['Public layer', 'github.com/JannetEkka/smt-apac', GH + 'smt-apac'], [null, 'WEEX feature', 'https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641']]));
rows.push(bullets([
  ["Runs 24/7 and places real orders on WEEX's exchange-granted simulated account (about $10K). Built alone by specifying the work and directing AI coding agents: ", ['about 88,000 lines of Python, 3,152 tests, 362 merged pull requests', { b: true }], ', each reviewed by me before merge.'],
  ['When the GCP billing account closed, I ', ['moved the live system to a zero-cost stack in two days', { b: true }], ": an Oracle free-tier VM under systemd, Cloudflare Workers and GitHub Actions. It re-adopted its three open positions from committed state."],
  ['Audited 98 AI-written merges line by line and found two failures the green test suite missed: an order-format bug that had ', ['rejected 1,137 live orders over three months', { b: true }], ', and a memory freeze that kept the daemon down 60% of the time for ten days. A fix now counts as done only when the production log shows it.'],
  ['Any substituted default must log a warning and a liveness flag, a rule written after four multi-week data bugs ran silently; the September audit found and logged 17 more silent failure paths.'],
  ['Graded my own six AI agents on independent market data and found all six called direction at a coin flip. So written rules now open every trade, the agents are advisors graded on every call, and every explanation passes a counterfactual test.'],
  ['Built ', ['SMT World', { b: true }], ', the product for users: a Three.js/WebGL world on Cloudflare Workers where people watch the agent trade and ask it why, answered by Gemini from the live book.'],
]));
rows.push(sub([['Stack: ', { b: true }], 'Python, pandas, Optuna, scikit-learn, Gemini, Oracle Cloud, Cloudflare Workers, DuckDB, systemd, pytest, Three.js']));

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
    ['A GitLab Duo flow reads production logs when a bug is filed and writes a proof contract into the issue; after deploy, the pipeline judges the shipped build on its own logs and closes the issue with a receipt, or keeps it open. All nine DevSecOps stages.'],
    ['Real run: a fix that passed the tests, the contract gate and Duo Code Review cut failures only ', ['from 32% to 9%', { b: true }], ", so the issue stayed open; the Duo Developer flow's second fix reached ", ['0 failures on 875 requests', { b: true }], '.'],
  ]);
build('Chithi: official Indian letters explained, every number checked', 'Meta Global AI Developer Hackathon (Cerebral Valley)', 'Nov 2026',
  [['Live', 'chithi-oprj.onrender.com', 'https://chithi-oprj.onrender.com'], ['Code', 'github.com/JannetEkka/chithi', GH + 'chithi'], [null, 'Demo video', 'https://youtu.be/wlRwfQghgOw']],
  [
    ['A phone photo of a bill or notice, explained in Bengali, Hindi or English: SAM 3.1 finds the page and its tables, Muse Spark reads it twice and explains it, Muse Voice Transcribe takes spoken questions. A check with no model requires every date and amount to be in the quote and in the second reading; 28 live explanations, ', ['0 of 114 values shown wrong', { b: true }], '.'],
  ]);
build('Spona: concurrent agents that match researchers with companies', 'NTP Novi Sad Hackathon (JigJoy × Mozaik)', 'Oct 2026',
  [['Live', 'jannetekka.github.io/spona', 'https://jannetekka.github.io/spona/'], ['Code', 'github.com/JannetEkka/spona', GH + 'spona']],
  [
    ['12 agents on one Mozaik runtime read 1,047 researchers, 10,779 papers and 489 company challenges (~7M tokens) and gave every challenge an outcome in ', ['5 min 48 s', { b: true }], ', up to 19 loops at once, for $1.52. A critic checks every claim against its source while the others work; it sent back 33.'],
  ]);
build('Footfall: a taste agent for small local shops', 'Qloo Agentic + Nebius × NVIDIA hackathons', 'Oct 2026',
  [['Live', 'footfall-zz9v.onrender.com', 'https://footfall-zz9v.onrender.com'], ['Code', 'github.com/JannetEkka/footfall', GH + 'footfall'], [null, 'Demo video', 'https://youtu.be/Smw3hQl3CB0']],
  [
    ["Qloo place data becomes the signal for what a street listens to, reads and buys; NVIDIA Nemotron on Nebius Token Factory makes its own Qloo calls and writes a plan, and a checker deletes anything Qloo didn't return. About $0.013 a run."],
    ['The demo is public and the LLM account has a card on file, so each run reserves its worst case in a durable ledger first and the demo stops at $15 ', ['(total spend so far $0.45)', { b: true }], "; replay mode survives the sponsor key expiring."],
  ]);
build('Aside: a Fire TV companion that never spoils the film', 'Amazon Build, Ship, Shape, Fire TV track', 'Oct 2026',
  [['Live', 'aside-tv.onrender.com/tv', 'https://aside-tv.onrender.com/tv/'], ['Code', 'github.com/JannetEkka/aside-tv', GH + 'aside-tv'], [null, 'Demo video', 'https://youtu.be/8459XKUURhs']],
  [
    ["Answers only from what the viewer has seen, with a second model checking against the rest of the film: on 16 questions written to pry out the future, a whole-film prompt leaked 6 and ", ['Aside leaked 0', { b: true }], ', helpful on 8 of 8. Rebuilt overnight for a real Vega OS Fire TV Stick that would not run Android APKs.'],
  ]);
build('Lore: a company brain for open-source projects', 'Graph Hacks, FalkorDB × WeMakeDevs', 'Oct 2026 · 4 days',
  [['Live', 'lore-gh5y.onrender.com', 'https://lore-gh5y.onrender.com/'], ['Code', 'github.com/JannetEkka/lore', GH + 'lore'], [null, 'Demo video', 'https://youtu.be/V-Ifwi_jxhg'], [null, 'Blog post', 'https://medium.com/@jannetaekka/i-built-a-company-brain-for-open-source-projects-on-falkordb-47f519f9ce08']],
  [
    ['1,357 of the sponsor\'s own PRs in a FalkorDB graph; a Gemini agent answers "who knows this code?" through 12 Cypher tools and cites the PRs behind every answer. Backtested on 300 real PRs: a real reviewer in the top three ', ['90%', { b: true }], ' of the time, against 88% for the obvious baseline.'],
  ]);
build('Klarbrief: official Swiss letters explained offline', 'Hack Apertus, Track 2B', 'Oct 2026',
  [['Code', 'github.com/JannetEkka/klarbrief', GH + 'klarbrief']],
  [
    ["Apertus 1.5 8B explains an official letter in the reader's language, fully offline in llama.cpp on an internal Docker network on a 4-core CPU. Every point is checked against the letter before it is shown: on 48 explanations, ", ['0 wrong CHF amounts', { b: true }], " reached the reader and the check stopped 6 of the model's 7 wrong dates."],
  ]);
rows.push(full(para([
  ['Also shipped, Oct–Nov 2026: ', { b: true }],
  'Wiretrap (adversarial testing for AI agents) · SmartDesk (multi-agent assistant, evaluated RAG) · SMT Receipts (Monad) · SMT World: Clock In (native Android, Solana Mobile) · SQL Noir (Zetaris + Nemotron) · Afterburn (Sentinel-2 burn scars) · Recourse (Web3 for Social Good, Round 2) · Beauty Within (YouCam) · Ghost Ledger (HackerRank Orchestrate). All at ',
  ['jannetekka.github.io/DSProjects', { link: 'https://jannetekka.github.io/DSProjects/' }],
])));

rows.push(section('PROFESSIONAL EXPERIENCE'));
rows.push(head(['AutoKorrekt — Lead Frontend Developer (EdTech startup MVP) | May 2023 – Jan 2024']));
rows.push(bullets([['Led the Next.js frontend of an AI answer-evaluation platform for teachers: OCR validation flows, JWT auth, bulk answer-sheet upload and per-student status, over a backend using ', ['AWS Textract', { b: true }], ', Amazon Comprehend, S3, RDS and SageMaker.']]));
rows.push(head(['Deloitte Consulting LLP · Test Automation Engineer (Analyst) | Aug 2019 – Jan 2023 · Bangalore']));
rows.push(bullets([
  [['Client-facing throughout', { b: true }], ': demos, working sessions and requirement calls in US, UK and India hours for Fortune 500 accounts including AT&T Consumer Connect, Hewlett Packard Enterprise and The Dental Supply Company; weekend on-call.'],
  [['Led a 6-member QA engineering team', { b: true }], ' on automated testing for those clients.'],
  ['Built Selenium and Katalon Studio automation that ', ['improved test execution efficiency by 83%;', { b: true }], ' Jenkins-based reporting cut manual analysis time by ', ['75%', { b: true }], '.'],
  ['Wrote Python analysis and Tableau dashboards tracking quality across ', ['343 business components', { b: true }], ', cutting test failures by 25%; analysed ', ['50,000+ SAP Hybris transactions', { b: true }], ' to isolate performance bottlenecks for the client.'],
  ['Joined as a QA automation intern in Jan 2019 (North Dakota Health and Human Services website, POEDI XML testing); converted to analyst after six months. 2 Spot Awards and an Applause Award.'],
]));
rows.push(sub([['Tech: ', { b: true }], 'Selenium, Katalon Studio, Python, JavaScript, Jenkins, Salesforce, SAP Hybris, Tableau, JIRA, Git']));

rows.push(section('EDUCATION'));
rows.push(sub([['Post Graduate Program (PGP) in AI/ML | UT Austin / Great Lakes Executive Learning (Feb 2024 – Mar 2025)', { b: true, i: true }]]));
rows.push(sub(['RANK 1 HONORS / COHORT TOPPER (Specialization in Deep Learning, NLP, and Data Modeling): GPA 4.09/5']));
rows.push(sub([['Bachelor of Technology (B.Tech), Information Technology | Graduated 2019', { b: true, i: true }]]));
rows.push(sub(['Kalinga Institute of Industrial Technology University, Bhubaneswar: CGPA 7.17/10']));

rows.push(section('CERTIFICATIONS & ACHIEVEMENTS'));
rows.push(full([
  [['Provisional patent filed', { b: true }], ', India, App. No. 202631090789 (Jul 2026), covering the SMT decision and verification architecture.'],
  [['WEEX AI Wars I: #1 on the preliminary leaderboard', { b: true }], ' of 230+ teams, then one of 37 finalists in the live AI trading competition; featured in ', ["WEEX's coverage", { link: 'https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641' }], ' and two live AMAs.'],
  [['Winner, Best DeFi Application', { b: true }], ', OpenServ × Hack2skill hackathon; runner-up, Best Website Application.'],
  [['Top 101 of 1,500+ teams', { b: true }], ', Google Cloud Gen AI Academy APAC 2026 Cohort 1 hackathon (SmartDesk); Round 2, Web3 for Social Good 2026 (Recourse).'],
  [['Google Cloud Gen AI Academy', { b: true }], ' 2025 (ID 2025H2S04GENAI-A01917) and APAC 2026 Cohorts 1, 2 and 3; Gen AI Exchange Hackathon 2025; Agentic AI Day; Asha AI Hackathon 2025.'],
  [['CPSAT', { b: true }], ', Certified Professional Selenium Automation Testing, 2022. All credentials on ', ['Credly', { link: 'https://www.credly.com/users/jannet-akanksha-ekka/badges' }], ' and ', ['Google Skills', { link: 'https://www.skills.google/public_profiles/2a91b2f0-31d3-467e-ba45-3ba1888a908e' }], '.'],
].map(t => para(t, { bullet: 'dot' }))));

// --- header (repeats on every page) ---------------------------------------------------
const header = new Header({ children: [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [new TextRun({ text: 'JANNET AKANKSHA EKKA', font: 'Calibri Light', size: 44 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: runs([
    'jannetekka96@gmail.com | +91 90788 02572 | ',
    ['LinkedIn', { link: 'https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/' }], ' | ',
    ['GitHub', { link: 'https://github.com/JannetEkka' }], ' | ',
    ['Portfolio', { link: 'https://jannetekka.github.io/DSProjects/' }], ' | Kolkata, India',
  ], { size: 21 }) }),
]});

const doc = new Document({
  creator: 'Jannet Ekka', title: 'Jannet Akanksha Ekka - Resume (Forward Deployed Engineer)',
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
