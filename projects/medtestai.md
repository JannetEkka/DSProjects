# MedTestAI: test-case generation for healthcare software

**Gen AI Exchange Hackathon 2025** (Google Cloud × Hack2skill; problem statement "Automating Test Case Generation with AI"; certificate of participation dated 14 Jan 2026, ID 2025H2S08GH-P100275). Built Sep 17–21, 2025; CORS and deploy fixes Oct 3; refactor and export fixes Oct 29 – Nov 5, 2025.
**Code:** [github.com/JannetEkka/MedTestAI](https://github.com/JannetEkka/MedTestAI) · was live on Firebase Hosting + Cloud Run (GCP project `pro-variety-472211-b9`). That GCP billing account closed on 10-02, so **check the live links before quoting them**.

> ⚠️ **The portfolio card describes this wrongly.** It says MedTestAI handles "protected health information under the access, auditing and data-handling rules". It doesn't. It **generates test cases** for healthcare software from requirements documents, with HIPAA and other compliance frameworks as *test content*. The README itself says "No databases. Stateless architecture." The card is corrected in this update.

## The 30-second version

QA teams writing test cases for regulated healthcare software have to cover functional behaviour *and* compliance controls. MedTestAI takes a requirements document (PDF, TXT, MD) or typed requirements, lets you edit the extracted requirements, and has **Gemini 2.0 Flash** generate structured test cases (ID, name, category, priority, preconditions, steps, expected results, compliance requirement, risk level) aware of **8 frameworks** (HIPAA, FDA 21 CFR Part 11, GDPR, HITRUST, SOC 2, ISO 13485, ISO 27001, ABDM), for Agile, Waterfall or Hybrid teams. Exports to CSV, JSON and Excel.

**This connects to my four years of QA at Deloitte:** test-case design is the job I did by hand. **Impact caution:** the README's problem statement says "Manual test case creation consumes 60–80% of QA time" with no source. Don't repeat that number unless you can cite it. Nothing here measures generated-test quality or time saved.

## 1. Architectural reasoning
- **Database:** none, by design. Each request is document in → test cases out → download. With no stored requirements there's no PHI-at-rest problem, which matters for a healthcare-adjacent tool.
- **Compute:** **Node 18 + Express on Cloud Run** (serverless, scales to zero; a stateless request/response API is the textbook fit) and a **React 18 frontend on Firebase Hosting** (CDN + TLS). Terraform files in `infrastructure/terraform`; environment configs per stage (`config/development|staging|production.json`).
- **Frameworks:** Multer for uploads, Gemini 2.0 Flash for generation (commits also mention Document AI and Vertex AI during the build), a Chrome extension folder (an experiment).

## 2. Data & security pipelines
- **CI/CD auth: Workload Identity Federation** from GitHub Actions to GCP (`google-github-actions/auth@v2` with a `WORKLOAD_IDENTITY_PROVIDER` secret), so **no long-lived service-account key in GitHub**. Two days of commits (Sep 17–18) went into getting that right ("Test: new workload identity provider v2"). That's a strong FDE talking point.
- **App auth:** a `googleAuth.js` module exists; the deployed backend was `--allow-unauthenticated`. Be ready to say the API was public for the demo and protected by rate limits.
- **Rate limiting** (`middleware/rateLimiter.js`): 100 requests per 15 minutes per IP overall, and **5 test generations per minute**, which protects the Gemini quota. Input validation and a central error handler are in `middleware/`.
- **CORS** locked to the Firebase frontend for production (Oct 3 fixes).
- **Privacy:** requirements documents go to Gemini and aren't stored. For real customer documents you'd want a data-processing agreement and region pinning. A stated limit.
- **Repo hygiene to fix:** `cloud-sql-proxy.exe`, `firebase-debug.log` and `bash.exe.stackdump` are committed. I checked the debug log: it has no raw tokens (bodies are "[omitted]"), but those files shouldn't be in git.

## 3. Reliability & failure operations
- Stateless: a crashed request is retried by the user; nothing to recover. A `/health` endpoint on the backend.
- Rate limits stop one user from exhausting the model quota.
- No model fallback ladder (unlike the later projects).

## 4. Evaluation & optimisation metrics
- **Not measured:** generated-test correctness, coverage of requirements, or time saved. If asked: requirement-to-test traceability coverage (every requirement has ≥1 test), reviewer acceptance rate on a sample, and minutes per test case vs manual authoring, which is exactly what my Deloitte metrics would have been.
- **Cost:** Cloud Run scale-to-zero + Firebase Hosting free tier + Gemini per call, capped by the generation rate limit.

## Weak spots to own before they ask
- The portfolio card overstated it (fixed). The unsourced "60–80%" line. Public API. Committed binaries and logs.

## Sources
`README.md`, `middleware/rateLimiter.js`, `.github/workflows/*` (WIF), `config/`, `infrastructure/terraform/`, git log Sep 17 – Nov 5, 2025 (22 commits); `_portfolio_src/data.py` credentials (Gen AI Exchange Hackathon 2025 certificate).
