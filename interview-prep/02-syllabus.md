# Part 2 — Syllabus

Ten modules. Each one is taught from code I have written, then drilled with
questions at three levels in [Part 3](03-questions.md).

Work them in this order. Modules 1–4 are the ones that get asked in an AI
engineering interview. Modules 5–7 are supporting. Modules 8–10 are where I
have something most candidates do not, so they are worth as much as 1–4.

| # | Module | Taught from | Why it matters |
|---|---|---|---|
| 1 | **Agents and orchestration** | SMT `personas/` + `judge.py`; SmartDesk `agent.py` | The central question in every AI-engineering interview right now |
| 2 | **Tools, function calling and MCP** | SmartDesk `mcp_servers/`, `tools.py` | MCP is vendor-neutral and I have written servers, not just used them |
| 3 | **RAG and retrieval** | SmartDesk `rag/` | Asked in nearly every interview; most candidates cannot go past "I used a vector DB" |
| 4 | **Evaluation** | `evals/`, SMT `learning/validation/` | The rarest thing I have. Almost nobody interviewing can measure what they built |
| 5 | **LLM fundamentals** | Vertex/Gemini call sites, prompts | Tokens, context, temperature, structured output, cost |
| 6 | **Cloud and deployment** | Cloud Run, Functions, BigQuery, systemd | "How would you deploy this" follows every design question |
| 7 | **Classical ML** | `DSProjects/`, SMT learning loop | Still asked, and I have 13 projects of it |
| 8 | **Testing → AI evaluation** | Deloitte work + `validation/` | My actual differentiator. Bridges 4 years of QA into the newest problem in AI |
| 9 | **GPU acceleration** | cuDF benchmark | Concrete, measured, and unusual for a non-infra candidate |
| 10 | **Tools I have not used** | — | Being able to say "no, but here is what I built instead" without flinching |

---

## The four sentences to have ready

Before any of the detail, these four answers cover most of a first-round
screen. Everything in Part 3 is elaboration on them.

**"Tell me about yourself."**
> I build production agentic systems. My flagship is a patent-pending
> multi-agent trading platform on Google Cloud — six specialist agents voting
> into a learned judge, retrained weekly behind a statistical overfitting
> gate. Before AI I led QA automation at Deloitte for four years, which is why
> I build evaluation in from the start rather than bolting it on.

**"What is your strongest technical skill?"**
> Knowing whether the thing I built actually works. I build the measurement
> before the feature. On SmartDesk that harness killed the change it was built
> to justify — a reranker that looked significant on one embedder and
> collapsed on the production one.

**"What is your biggest weakness?"**
> Depth in the JavaScript backend stack. I have shipped React, Next.js and
> TypeScript, but Node and Express are ramp-up for me, not lead. I would not
> take a role that is mostly that. Where I am strong is Python, agents,
> retrieval and knowing when a system is wrong.

**"Why should we hire you over someone with more AI experience?"**
> Most people shipping agents right now cannot tell you when one is wrong. I
> spent four years finding how enterprise systems fail before customers did,
> and I have carried that into every system I have built since. My trading
> agent refuses to act on data it cannot verify, and no fallback value passes
> without a warning.

---

## How to use Part 3

Each module has **basics → intermediate → advanced**.

- **Basics** — definitions. If I cannot answer these cleanly the rest does not land.
- **Intermediate** — "how does it work" and "why did you choose that". This is where most interviews actually live.
- **Advanced** — trade-offs, failure modes, and the questions with no clean answer. These separate a candidate from a strong candidate.

For every question the model answer names a specific file, number or decision
from my own work. **Generic answers are forgettable. Specific ones are not.**
