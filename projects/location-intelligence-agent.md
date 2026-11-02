# Location Intelligence Agent: an ADK agent over BigQuery and Google Maps MCP servers

**Google Cloud Gen AI Academy APAC 2026 (Cohort 1 track material).** Built Mar 28, 2026, in one day.
**Code:** [github.com/JannetEkka/bakery-growth-agent](https://github.com/JannetEkka/bakery-growth-agent) (3 commits)

## The 30-second version

An ADK agent (Gemini) for a bakery chain, wired to **two remote MCP servers that Google hosts**: **BigQuery** (`https://bigquery.googleapis.com/mcp`) over a demographics / foot-traffic / prices / weekly-sales dataset, and **Google Maps** (`https://mapstools.googleapis.com/mcp`, Grounding Lite) for places, directions and geocoding. Two jobs: a **delivery-zone optimiser** (score LA zip codes by foot traffic and demographics, then check competitor density on Maps) and a **sales-trend forecaster** (flag underperforming stores week over week, project next month, and check whether nearby competition explains the gap).

It's codelab-level work built on the codelab's dataset (`mcp_bakery`). In interviews I call it that, then pivot to SmartDesk, where I wrote the MCP servers myself.

## 1. Architectural reasoning

### Database / storage
- **BigQuery**, because that's where the business data lived in the exercise, and the agent queries it through the BigQuery MCP server rather than custom SQL tools. Why that's interesting: the agent writes SQL against a warehouse it discovers through MCP, with no hand-written tool per question.
- ADK's local session store (`.adk/session.db`, SQLite) holds chat sessions. **It was committed to the repo**, a mistake I'd own: session history shouldn't be in git.

### Compute & hosting
- `adk web` locally; `Dockerfile` + `deploy.sh` for **Cloud Run**. The compute is light (the agent orchestrates and BigQuery does the heavy lifting), so scale-to-zero containers fit.

### Frameworks & libraries
- **Google ADK** with `MCPToolset` over **`StreamableHTTPConnectionParams`** (remote MCP over HTTP, not stdio). That's the contrast with SmartDesk, which used stdio subprocesses for servers I wrote.

## 2. Data & security pipelines

### Authentication & access control
- **BigQuery MCP:** Application Default Credentials with the BigQuery scope; the code refreshes once at startup and sends `Authorization: Bearer <token>` plus `x-goog-user-project`. **Weak spot:** the token is fetched once, and Google access tokens expire after about an hour, so a long-running deployment would start failing without a refresh. The fix: refresh per request, or a header provider callback.
- **Maps MCP:** an API key in the `X-Goog-Api-Key` header from `.env`. **Weak spot:** the default is the string `'no_api_found'`, a silent fallback that turns a missing key into a confusing 4xx later. Today I'd fail fast at startup.

### Data ingestion & flows
- Request/response: prompt → agent plans → MCP tool calls (BigQuery SQL, Maps searches) → answer. Timeouts were tuned in the "fixed MCP session time out" commit (BigQuery 60 s with a 600 s SSE read; Maps 30 s with a 300 s SSE read).

### Privacy & compliance
- Synthetic codelab data, and no personal data. A real chain's sales data would stay in its own BigQuery project, and the MCP server respects the caller's IAM, which is the point of using Google's hosted MCP with user credentials.

## 3. Reliability & failure operations
- **State:** ADK sessions in SQLite.
- **Fallbacks:** none beyond MCP timeouts. One fix was a model ID change ("fixed gemini model"). No retries or ladder, unlike the later projects.
- **Observability:** console prints of toolset configuration; ADK's dev UI trace.

## 4. Evaluation & optimisation metrics
- **Nothing measured:** no accuracy check on the revenue projection and no comparison with a naive forecast. If asked: backtest the forecaster on held-out weeks against "same as last week" and a moving average, before trusting "projects next-month revenue".
- **Cost:** BigQuery on-demand pricing per query plus the Maps API. Fine for a codelab; a real deployment would need query caps.
- **Constraints:** remote MCP availability, token lifetime, Maps quotas.

## Weak spots to own before they ask
- Codelab dataset and pattern; the session DB committed; token refresh missing; no evaluation. Its value is that it's the first time I wired remote MCP servers, and it's a clean contrast with stdio MCP in SmartDesk.

## Sources
`README.md`, `bakery_growth_app/tools.py`, the 3 commits of Mar 28, 2026; `interview-prep/01-inventory.md` (depth "Used" for remote MCP).
