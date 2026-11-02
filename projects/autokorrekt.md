# AutoKorrekt: AI answer-evaluation platform for teachers (EdTech startup MVP)

**Lead Frontend Developer, May 2024 – Jan 2025** (by the repo, Jannet's own commits run **Jun 11 – Dec 31, 2024** on branch `dev_Jannet`, merged through PRs #27 and #29). A team project: 8 contributors appear in the history.
**Code (frontend):** [github.com/AnshumaanS/autokorrekt_frontend](https://github.com/AnshumaanS/autokorrekt_frontend) · screenshots in `assets/autokorrekt/` of this repo.

> ⚠️ **Date check for the résumé:** your Word résumé says "May 2023 – Jan 2024". The repo shows your commits from Jun 2024 to Dec 2024, and the portfolio says May 2024 – Jan 2025. A public repo contradicts the 2023 dates, so use 2024–2025.
>
> ⚠️ **What this repo can and can't prove:** it's the **frontend**. The portfolio's backend claims (AWS Textract coordinate-based extraction, Amazon Comprehend for the bilingual EN/DE feedback, the ML data flow across S3, RDS and SageMaker, "scaled to 1,000+ concurrent submissions") **aren't visible in this repo**. Be ready to explain your part in each: you designed the data flow and integrated the APIs, and the backend team built the services. If you can't back "1,000+ concurrent", soften it to what you measured or remember.

## The 30-second version

Teachers go from sign-up to graded scripts: create a class (a 3-step wizard: class → course → test), upload a roster (CSV) and the question paper, bulk-upload scanned answer sheets, then track each student through OCR → AI evaluation → validation. I led the frontend: the validation flows for question paper (QP), reference answer (RA) and student answer (SA), where the teacher selects an area on the PDF, the text is extracted via OCR and then validated; the evaluation and report pages; the API integration; authentication; per-student status.

## 1. Architectural reasoning
- **Frontend stack:** it started as a React (CRA) app with AWS Amplify auth stubs (commented out in `main`), then became **Next.js + TypeScript + React Context + Tailwind + shadcn/ui** on my branch. Why Next.js: routing and environment-specific config (`NEXT_PUBLIC_API_BASE_URL`, added Dec 17), and a typed service layer per domain (`classService`, `courseService`, `testService`, `studentService`, `validationService`).
- **Database / compute:** the backend's (Django per the portfolio; RDS, S3, SageMaker per the claims). The frontend talks to it over REST via an axios instance.

## 2. Data & security pipelines
- **Authentication:** JWT access and refresh tokens. An axios **request interceptor** adds `Authorization: Bearer <token>`, and a **response interceptor** handles 401s. A `withAuth` higher-order component guards pages. Fixed on Nov 13: "refresh issue after sign in".
- **A weak spot to own:** `authUtils.ts` stores tokens in **localStorage, sessionStorage and a JS-set cookie** (`Secure; SameSite=Strict`, but not HttpOnly, because JavaScript sets it). Any XSS could read the tokens. If asked how I'd do it now: HttpOnly, Secure, SameSite cookies set by the server, short-lived access tokens, and refresh-token rotation on the server.
- **Data flow:** files (question paper, reference answers, student answer sheets) upload through the API (Dec 14: "answer document upload functionality"). Per-student status updates (Dec 23) drive the pipeline view.
- **Privacy:** student answer sheets are children's data. The frontend never stored them locally. Retention and consent sat with the backend and the school. I'd raise that in a real deployment.

## 3. Reliability & failure operations
- Real bugs fixed on my branch: a refresh loop after sign-in; the file-validation page landing on the wrong route; class switching; table styling; the existing-classes display (Dec 24–25). Environment-specific config so dev and prod hit the right API.
- No offline queue for uploads, and no retry with backoff seen in the frontend.

## 4. Evaluation & optimisation metrics
- **Nothing measured in the repo:** no grading-accuracy figure (AI score vs teacher score) and no load test. If asked: agreement between AI and teacher marks (Cohen's kappa or MAE per question), the OCR character error rate on handwriting, and time saved per script vs manual marking, measured on a pilot class.
- **"1,000+ concurrent submissions":** only quote it if you can say how it was measured.

## What the history shows
- Jan 2024: other developers scaffolded the React app (navbar, routing, palette). Jun 2024: my React app replaced a submodule and built the homepage and students page → Jun–Jul: the validation highlight, validation flow, evaluation page skeleton and design → Sep–Oct: report page, API service config, QP/RA/SA validation flows → Nov: auth API integration, modals → Dec: upload, status, environment config, fixes, README with the full flow diagram.

## Sources
`autokorrekt_frontend` git history (all branches; `--author=Jannet`), `dev_Jannet` branch files `src/utils/authUtils.ts`, `src/services/api.ts`, `README.md`; `_portfolio_src/data.py` (card); the uploaded Word résumé (dates).
