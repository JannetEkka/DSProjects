# Part 3 — Questions and answers

Every answer names a file, a number or a decision from my own work.

---

# Module 1 — Agents and orchestration

## Basics

**What is an AI agent?**
An LLM that can decide to take actions, not just produce text. It gets tools it
can call, it chooses when to call them, and it uses the results to decide what
to do next. The loop is: observe → decide → act → observe.

**What makes a system "multi-agent"?**
More than one agent, each with a narrower job, plus something that routes
between them and combines their output. My SMT system has six persona agents —
order-flow, technical, whale, on-chain, sentiment, regime — and a Judge that
aggregates their votes. SmartDesk has an inbox agent, a planner agent and a
knowledge agent under a root orchestrator.

**Why use multiple agents instead of one big prompt?**
Three reasons I hit in practice. Each agent gets a focused instruction so it
degrades less. They can be tested separately — my personas have their own tests.
And when the output is wrong I can see *which* agent was wrong, which one prompt
does not give you.

**What is an orchestrator?**
The component that decides which agent handles what and in what order. In
SmartDesk it is the root ADK `Agent`; it routes to sub-agents, then a
`SequentialAgent` composes the final reply.

## Intermediate

**Walk me through your multi-agent architecture.**
> SMT. Six personas, each a class implementing one contract: given market
> context, return a `PersonaVote` with direction, confidence and reasoning.
> They run independently and know nothing about each other.
>
> A `JudgePersona` collects those votes and produces a `JudgeDecision`. It
> weights each persona, and the weights are learned rather than hand-set. One
> detail I had to add: the conviction is **quorum-renormalised** — divided by
> the weight mass that actually voted. Without that, one dead data feed drags
> the total down and the confidence floor becomes unreachable, so the system
> silently stops trading. That happened, and that is why the renormalisation
> exists.
>
> Downstream of the Judge is a risk gate and an execution layer, then a
> learning loop that retrains on real outcomes.

**How do agents share state?**
Two patterns I have used. In SMT it is explicit: a context dict built once per
cycle, passed to every persona, and votes returned into a dict the Judge reads.
In SmartDesk it is the framework's: `tool_context.state["USER_REQUEST"]` written
by one tool and read by sub-agents, and `output_key="inbox_data"` so an agent's
result lands in shared state for the next one. Same idea, different syntax —
LangGraph's `StateGraph` is the same concept again.

**How do you stop one agent's failure taking down the system?**
It is a written contract in my persona base class: *a persona that hits a
rate-limit, a 401 or a timeout MUST return NEUTRAL.* It never raises, never
guesses. A neutral vote carries zero weight, so the Judge simply decides on the
personas that did answer — which is exactly what the quorum renormalisation
handles.

**How do you decide sequential vs parallel agents?**
Sequential when there is a real dependency — SmartDesk's formatter cannot run
before the sub-agents have produced anything. Parallel when there is not: my six
SMT personas have no dependency on each other, so serialising them would only
add latency.

## Advanced

**How do you debug a multi-agent system that gives a wrong answer?**
Every decision is logged with the full per-persona vote breakdown, plus the
Judge's weights and the final conviction. So I do not debug "the system was
wrong" — I read which persona was wrong and whether the Judge over-weighted it.
I also built a counterfactual faithfulness check: flip an input, confirm the
stated reason changes accordingly. If the explanation does not move when the
input does, the explanation was decorative.

**Your Judge weights are learned. How do you stop them overfitting?**
The weekly refit only ships if the candidate passes a gate — combinatorial
purged cross-validation, deflated Sharpe, probability of backtest overfitting,
and false discovery rate control. Failing candidates are held in shadow rather
than deployed. The gate has rejected every candidate on some weeks, and I let
it, because a gate you override is not a gate.

**When would you NOT use a multi-agent architecture?**
When one model with one prompt does the job. Multi-agent costs latency, tokens
and debugging complexity. I would only reach for it when the sub-tasks need
genuinely different instructions or tools, or when I need to attribute a failure
to a specific component. For a single-step extraction task it is overhead.

**Trade-off: hand-rolled vs a framework?**
I have done both. Hand-rolled in SMT because I needed control over the voting
maths and wanted the learning loop wired into it. Framework in SmartDesk because
ADK gave me sub-agent routing and shared state without writing them.

The hand-rolled version taught me more — I understand what `StateGraph` is doing
because I built that. The framework version shipped faster. For a production
system with unusual logic I would hand-roll the core and use a framework at the
edges.

---

# Module 2 — Tools, function calling and MCP

## Basics

**What is function calling?**
Giving the model a description of functions it can invoke. The model returns a
structured request — function name plus arguments — your code executes it and
returns the result. The model never runs anything itself.

**What makes a good tool definition?**
A clear name, typed parameters, and a docstring that says what it does and when
to use it — the model reads that docstring to choose. My `search_notes` docstring
says "Search meeting notes and documents using vector similarity", which is what
tells the agent to reach for it on a knowledge question.

**What is MCP?**
Model Context Protocol. An open standard for exposing tools and data to LLM
applications, so a tool server can be written once and used by any compliant
client. It is Anthropic's protocol and is not tied to one vendor.

**Why does MCP matter?**
Before it, every framework had its own tool format. MCP means a Gmail server
works with any MCP client. That is why it is the most portable thing on my CV —
it is not a Google skill.

## Intermediate

**You wrote your own MCP servers. Walk me through one.**
> `gmail_server.py`. I used the low-level protocol SDK — `Server("gmail-mcp-server")`
> — and ran it over stdio with `stdio_server()`. The server declares which tools
> it exposes and handles the call requests. Auth is separated into its own module
> so the server does not own credential handling.
>
> The reason I wrote it rather than using a hosted one was control: I wanted to
> choose exactly which Gmail operations were exposed. A tool surface is an attack
> surface, and "read and draft" is a very different risk profile from "send".

**What is the difference between an MCP server and an MCP client?**
The server exposes tools. The client is the LLM application that discovers and
calls them. SmartDesk is both — it runs `MCPToolset` as a client against my own
servers.

**stdio vs HTTP transport?**
stdio when the server runs as a local subprocess — simple, no network, no auth
layer. HTTP for a remote shared server, which is what the BigQuery and Google
Maps MCP servers were in the Location Intelligence agent. stdio is easier and
safer locally; HTTP is what you need for something multi-tenant.

**How do you handle a tool that fails or rate-limits?**
Never let it propagate as an exception into the agent loop. In the ADK work
there is a `Graceful429Plugin` that catches rate limiting and degrades. In SMT
the rule is stronger: a failing input returns a neutral value *and logs a
warning*. The warning matters — a silent fallback is a bug that looks like
working software, and I have been bitten by exactly that.

## Advanced

**Security concerns with MCP?**
Three I would raise. The tool surface is an attack surface, so expose the
minimum. Prompt injection through tool *results* is real — if a tool returns
attacker-controlled text, the model may act on instructions inside it, so
results need treating as untrusted data rather than instructions. And
credentials: my servers keep auth in a separate module so the tool code never
handles raw tokens.

**How would you test an MCP server?**
Contract-test it directly, without the model: call each tool with valid and
invalid arguments and assert the response shape. Then integration-test through
the agent with a fixed prompt. My SmartDesk repo has 54 tests, including
integration tests for retrieval, so the tools are verified independently of
whether the LLM chooses them correctly.

**When is a tool the wrong abstraction?**
When the operation is deterministic and always needed. If every request needs
the user's timezone, fetch it before the prompt rather than making the model
decide to call a tool. Tools are for when the model needs to *choose*.

---

# Module 3 — RAG and retrieval

## Basics

**What is RAG?**
Retrieval-augmented generation. Retrieve relevant documents for the query, put
them in the prompt, and have the model answer from them. It grounds answers in
data the model was not trained on and lets you cite sources.

**Why not just fine-tune?**
RAG updates by changing data, not weights. For a knowledge base that changes,
retrieval is cheaper, faster to update, and lets you show where an answer came
from. Fine-tuning is for changing *behaviour* — tone, format, task — not for
adding facts.

**What is an embedding?**
A vector representation of text where semantic similarity becomes geometric
closeness. My notes use `text-embedding-005` at 768 dimensions. "Which service
runs the daemon?" lands near a note about Compute Engine even with no shared
words.

**What is a vector database?**
Storage with fast nearest-neighbour search over embeddings. I use Postgres with
pgvector — `VECTOR(768)` columns and the `<=>` cosine distance operator. It is
plain Postgres, so it runs on AlloyDB, Supabase, Neon or RDS.

**Walk me through your RAG pipeline.**
> Ingest: notes are chunked, each chunk embedded with `text-embedding-005`,
> stored in a `note_chunks` table with a foreign key back to the parent note.
> Query: embed the question, cosine search for the top candidates, optionally
> rerank, return the top 5 to the DataAgent, which answers from them. Parent
> links survive so citations resolve back to whole notes.

## Intermediate

**Why chunk at all?**
Two reasons. Embeddings lose fidelity over long text — one vector cannot
represent a 2,000-word document well. And you want to put only relevant passages
in the prompt, not whole documents.

**What chunk size and overlap did you use, and why?**
180 tokens with 40 overlap, sentence-aligned. Overlap stops an answer that
straddles a boundary from being split across two chunks that each look
irrelevant. Sentence alignment avoids cutting mid-thought.

**Did chunking help?**
> Honestly, no — and I can tell you exactly why. MRR@10 moved −0.003, p = 0.59.
> The reason is corpus shape: only 6 of my 120 notes were long enough to split
> into more than one chunk. For the other 113, chunking is a no-op by
> construction.
>
> It did earn its place indirectly: every reranker scored better on chunked
> candidates than on whole-note candidates. It is a better candidate generator
> even when it is not a better retriever.
>
> It also surfaced a real bug — only the first chunk contains the note title, so
> later chunks lost it. Repeating the title on subsequent chunks is now the
> recommended ingest setting.

**What is reranking?**
Retrieve a wider candidate set cheaply, then reorder with something more
accurate and more expensive. I retrieve 25 and rerank to 5. I implemented
reciprocal rank fusion, BM25 hybrid, a local cross-encoder and a Gemini
reranker.

**What is BM25 and why combine it with vectors?**
BM25 is lexical — term frequency and rarity, no semantics. It catches exact
matches that embeddings miss: identifiers, error codes, proper nouns. Reciprocal
rank fusion merges the two ranked lists without needing their scores to be
comparable.

## Advanced

**How do you know your retrieval is any good?**
> I measured it. 40 labelled questions over 120 notes, recall@k and MRR@k at
> k = 1, 3, 5, 10. `search_notes` returns 5, so R@5 is the number that reflects
> production. Significance by paired bootstrap, 10,000 resamples, 95% CI.
>
> Production baseline: **R@5 0.963, MRR@10 0.886.**

**Why bootstrap rather than just comparing averages?**
With 40 questions, one question is worth 0.025 of recall@1. Most differences
between strategies were 1–3 questions. Without a confidence interval they read
as improvements; with one, most are noise. That is the entire reason the harness
was worth building.

**Tell me about a time your data changed your mind.**
> This is the result I am proudest of. I compared six strategies on a
> development embedder because I had no Vertex credentials locally. The
> cross-encoder reranker won clearly: MRR@10 **+0.094**, R@1 +0.138, p = 0.04,
> eight questions better against two worse. It was the only strategy whose
> confidence interval excluded zero.
>
> I flagged it as unconfirmed anyway, for two reasons: p = 0.04 across six
> comparisons does not survive Bonferroni correction, which would need about
> 0.008; and it was the wrong embedder.
>
> Re-run on the production embedder, the advantage fell to **+0.028 with a CI
> spanning zero**, p = 0.44, five better against four worse. Every reranker went
> from helping to hurting. The sign flipped.
>
> The mechanism makes sense in hindsight: a stronger embedder produces better
> candidates, so there is less for a reranker to fix and more for it to break.
> When the top 5 is already right 96% of the time, reordering has more to lose
> than gain.
>
> Shipping it would have added ~190 MB of PyTorch and taken search from 29 ms to
> **2,382 ms** — 82 times slower — in an image I had deliberately cut from
> 1.8 GB to 340 MB to fix cold starts. For an effect indistinguishable from
> zero. The baseline ships, and now on evidence rather than caution.

**What are the failure modes of RAG?**
Retrieval misses and the model answers from parametric memory anyway, confidently
and wrong. Retrieval succeeds but the passage is ambiguous out of context.
Conflicting sources with no recency signal. Chunk boundaries splitting the
answer. And the one people forget — no eval, so none of the above is visible.

**How would you improve your current pipeline?**
In order: real notes rather than notes written for the eval, and reviewed
labels — everything is provisional until then. Then measure the Gemini reranker,
which is implemented but unmeasured; it would likely match the cross-encoder
without putting torch in the image, at about $1.18 per 1,000 queries. Then more
questions — 40 cannot separate the middle strategies; 200–300 would. Tuning
comes last, and on a held-out set, because anything chosen by maximising these
40 is overfitting.

---

# Module 4 — Evaluation

## Basics

**Why evaluate an AI system at all?**
Because without it you cannot tell an improvement from a regression, and LLM
output looks plausible whether or not it is right. Plausible-and-wrong is the
default failure mode, and it is invisible without measurement.

**What is recall@k?**
Of the questions where a correct document exists, the fraction where it appears
in the top k results.

**What is MRR?**
Mean reciprocal rank. If the right answer is at position 1 you score 1, position
2 gives 0.5, position 3 gives 0.33. Unlike recall it rewards ranking the right
answer *higher*, not just including it.

**Why both?**
Recall says "is it in there". MRR says "is it near the top". A change can improve
one and hurt the other — my cross-encoder improved R@1 and R@10 while making R@5
slightly worse.

## Intermediate

**How did you build the labelled set?**
Generated candidate questions from the notes, then treated the labels as
unreviewed until a human checks them. The harness prints a warning while labels
are unreviewed, and `RESULTS.md` lists it as a caveat, because wrong labels
corrupt every number silently.

**What is a paired bootstrap?**
Resample the questions with replacement 10,000 times, computing the delta
between two strategies on each resample. The spread of those deltas gives a
confidence interval. Paired because both strategies are evaluated on the same
questions, which removes question difficulty as a source of variance.

**What is multiple-comparison correction and why did you raise it yourself?**
Testing six strategies against a baseline means six chances for a p < 0.05 to
appear by luck. Bonferroni divides the threshold by the number of tests — about
0.008 here — and my p = 0.04 does not clear it. I raised it because the number
was in my favour and I did not want it believed more than it deserved.

## Advanced

**How do you evaluate a generative system, not just retrieval?**
Retrieval is measurable with recall and MRR because there is a ground truth.
Generation is harder. What I have built is a **faithfulness check**: verify the
stated reason actually corresponds to the decision by perturbing an input and
confirming the explanation changes. It catches explanations that are decorative
rather than causal. For RAG specifically I would add groundedness — is every
claim supported by a retrieved passage — and answer relevance.

**What is CPCV and why not plain cross-validation?**
Combinatorial purged cross-validation. With time series, ordinary k-fold leaks:
a training sample immediately before a test sample carries information about it.
CPCV purges observations around the test boundary and embargoes a window after
it. Without that you get a beautiful backtest and a model that loses money.

**What is deflated Sharpe?**
A Sharpe ratio adjusted for how many strategies you tried. Test enough variants
and one looks brilliant by chance. Deflated Sharpe discounts for the number of
trials, so it answers "is this good *given* I searched this hard" rather than
"is this good".

**Your forward test and your backtest disagreed. What did you do?**
> They did. My P(up) forecaster passed a forward test on BTC — AUC 0.723, 66.7%
> hit rate over 27 **non-overlapping** 4-hour windows, with monotonic
> calibration. The naive per-cycle read would have claimed roughly 100 times the
> sample size through autocorrelation, so the non-overlapping windows matter.
>
> Then the weekly backtest re-gate rejected the same model. The system has an
> interlock: a stale model cannot go live. I did not clear the flag.
>
> The disagreement is the finding, not an obstacle. A forward test the backtest
> gate rejects means one of them is wrong, and overriding the gate to get the
> answer I wanted would have destroyed the only mechanism protecting me from
> myself.

---

# Module 5 — LLM fundamentals

## Basics

**What is a token?** Roughly a word-piece. Billing and context limits are in tokens, not characters.

**What is a context window?** The maximum tokens in one request, prompt plus completion. It is why RAG exists — you cannot paste a knowledge base into every call.

**Temperature?** Randomness in sampling. Low for extraction and classification, higher for creative generation. My trading explanations run low; VerseCanvas prompt synthesis runs higher.

**System prompt vs user prompt?** The system prompt sets persistent role and rules; user messages are the turn-by-turn conversation. My SMT World chat persona — first person, 2–4 sentences, never give financial advice — is entirely system prompt.

## Intermediate

**How do you get structured output?**
Ask for a schema and validate it. The `google-genai` SDK supports a response
schema. The rule I follow is that a parse failure must never crash the caller —
in my sentiment fetcher, any failure returns `None` and the personas stay
neutral.

**How do you control cost?**
Know where the tokens go before optimising. I log per-call usage to
`gemini_usage_*.jsonl` and attribute cost by call site. That log was empty for
months because of an argument-order bug, which is its own lesson: an
observability file that exists but is empty is worse than no file, because it
looks like it is working.

**What is prompt injection?**
Input that contains instructions the model follows. Especially dangerous when it
arrives through a tool result — retrieved documents are data, not instructions,
and should be framed that way in the prompt.

## Advanced

**When do you not use an LLM?**
When a deterministic method is available and sufficient. Most of SMT is
arithmetic and statistics, not generation — the Judge is weighted voting, not a
prompt. LLMs are used for sentiment analysis over news, for explanation, and for
the chat tutor. Using a model where a formula works adds latency, cost and
nondeterminism for nothing.

**How do you make LLM output reproducible?**
Fully, you cannot. What you can do is pin the model version, fix temperature,
log every prompt and response, and build the system so a bad output degrades
rather than propagates. My design rule is that anything unverifiable must
announce itself — no silent fallback.

---

# Module 6 — Cloud and deployment

## Basics

**Cloud Run vs Cloud Functions vs Compute Engine?**
Cloud Run for containers that scale to zero — SmartDesk, SMT World. Cloud
Functions for small event-driven handlers — my budget pause and cost digest.
Compute Engine when you need a long-lived process; my trading daemon runs there
under systemd because it must hold state across cycles and survive reboots.

**How do you handle secrets?**
Secret Manager, resolved at runtime by the service account. Never in env files,
never in the image. And a secret that fails to resolve must log loudly — I had a
module fall back to a stub `get_secret` that returned `None`, which meant no
Discord alert was sent for months while everything looked healthy.

## Intermediate

**How do you keep a long-running service alive?**
systemd for restart-on-failure and start-on-boot, a watchdog for liveness, and a
health check that proves work is happening rather than that the process exists.
The distinction matters: my daemon can be running and doing nothing, so the
check greps for an activation log line, not a PID.

**How do you deploy without downtime?**
Cloud Run does revision-based rollout with instant rollback. For the daemon it is
a systemd restart, and the deploy is not considered done until I grep the log for
the new code's activation line. Merging a PR does not change a running process,
and treating merge as deploy is how you convince yourself a fix shipped when it
did not.

## Advanced

**How do you control cloud cost on a personal budget?**
Budget alerts wired to a Pub/Sub topic and a Cloud Function that can pause
spending automatically, plus a weekly cost digest. On the application side, cost
is a design constraint: I changed a data feed from a 600-second cache to a
4-hour one when I realised the underlying data was daily, cutting 864 calls a day
to 36.

**Tell me about a production incident.**
> Log pushes to the repo stopped for 49 hours. It looked like the daemon had
> died. It had not — 96% cycle uptime, zero errors throughout. Only the hourly
> push had failed.
>
> Cause: the auth token was embedded in the git remote URL, so git looked for a
> credential under the token as a username, found nothing, and fell through to
> an interactive prompt. Cron has no terminal, so it failed with "could not read
> Password".
>
> Two lessons I kept. Never put a credential in a remote URL — git prints the
> full URL in error messages, which leaked the live token into an alert channel.
> And a staleness alert and an auth-failure alert mean different things; reading
> which one fired would have saved 40 hours.

---

# Module 7 — Classical ML

## Basics

**Overfitting?** Learning the training set rather than the pattern. Diagnosed by a
train/validation gap, addressed with regularisation, more data or a simpler
model.

**Precision vs recall?** Precision is how many flagged items were right; recall is
how many right items were flagged. Which one matters depends on the cost of each
error type — for a medical screen you accept false positives to avoid misses.

**Class imbalance?** When one class dominates. My semiconductor yield project used
feature selection and SMOTE over 591 sensor signals for exactly this.

## Intermediate

**Walk me through a project end to end.**
> Customer churn. Telecom data, target is cancel-or-not. Cleaned and encoded,
> then compared bagging, AdaBoost and gradient boosting rather than picking one.
> Random Forest reached 81.5%. The output was not the model — it was a ranked
> list of at-risk customers with the features driving each, so the retention
> team could act on it.

**Why did your capstone only reach 69.2%?**
196 vehicle classes at make-model-year granularity, 16,185 images, and 24–68
images per class. The classes are visually near-identical — two model years of
the same car differ by a bumper. 69.2% against a 0.5% random baseline on a
long-tailed fine-grained problem is the honest number, and I would rather quote
it than a cherry-picked subset.

## Advanced

**How do you choose a model?**
Start with the simplest thing that could work and beat it deliberately. Baseline
first — always. Then judge on the metric that matches the business cost, not
accuracy by default. And weight interpretability: my trading system uses
gradient boosting and logistic models partly because I have to explain every
decision, which rules out anything I cannot attribute.

**How does your ML background help with LLMs?**
Evaluation discipline transfers directly. Train/test splits, leakage, class
imbalance, "is this difference significant" — these are the same questions in
both worlds. The bootstrap testing on my RAG eval is ordinary ML hygiene applied
to retrieval, and most people building RAG have not brought it across.

---

# Module 8 — Testing → AI evaluation

## Basics

**What did you do at Deloitte?**
Led a 6-person QA automation team for Fortune 500 clients — AT&T, HPE, Walmart
Sam's Club, a state benefits portal. Built Selenium and Katalon frameworks,
improved test execution efficiency 83%, tracked quality across 343 components,
and analysed 50,000+ SAP Hybris transactions in Python.

**Why does that matter for AI?**
Everyone is shipping agents. Far fewer can tell you when one is wrong. Testing is
the discipline of finding failure before the user does, and that is exactly the
gap in AI systems right now.

## Intermediate

**What transfers from QA to AI evaluation?**
Thinking in failure modes rather than happy paths. Building the measurement
before the feature. Distinguishing "it ran" from "it worked" — my liveness checks
require an observed output, because no errors in the log is not evidence of
anything. And knowing that a test which encodes the same assumption as the code
will pass and prove nothing.

**Give an example of that last one.**
> I shipped a fix, wrote a test, the test passed, and the behaviour was still
> broken for months. The test encoded the same wrong mental model as the code.
> What caught it was an observed output — a real alert in a real channel — not a
> re-read of the code path. Three audits had inspected that path and never once
> run it.

## Advanced

**How would you build an evaluation practice for an agent product from scratch?**
> Four things, in order.
>
> A labelled set first, small and human-reviewed, before any tuning. Then
> metrics that match the task — retrieval gets recall and MRR, generation gets
> groundedness and faithfulness — with confidence intervals, because most deltas
> are noise. Then observability in production: log inputs, retrieved context,
> output and the reason, so a complaint can be traced to a decision. And finally
> guardrails that fail loudly: refuse to act on unverified data, and make every
> fallback announce itself.
>
> That last one is the rule I hold hardest. Four separate multi-week bugs in my
> own system were the same pattern — something died, code substituted a
> plausible default, logged it as real, and nobody knew for weeks.

---

# Module 9 — GPU acceleration

## Basics

**What is cuDF?** A GPU DataFrame library in NVIDIA RAPIDS with a pandas-compatible
API. `cudf.pandas` accelerates existing pandas code with no rewrite.

**What did you accelerate?** The CPCV validation pipeline — 2.5M rows, 8 pairs,
1,095 days, 40 splits. **24s → 3.9s on a T4, about 6×.**

## Intermediate

**Why was that worth doing?** Validation was the bottleneck in the retrain loop.
Faster validation means more candidate strategies tested per week, which is
directly more learning.

**When does GPU not help?** Small data, where transfer cost dominates. Branch-heavy
logic that does not vectorise. And anything I/O-bound — a GPU does not make an
API call faster. I found this concretely: an early GPU version was *slower*
until the hot loop was rewritten to be GPU-native rather than looping in Python.

## Advanced

**How do you benchmark honestly?**
Same data, same splits, same machine class, warm start, and report the method not
just the number. The first figure I had was synthetic; I replaced it with a real
T4 measurement even though the honest number was less impressive, because a
benchmark you cannot reproduce is marketing.

---

# Module 10 — Tools I have not used

**The rule: answer in three beats. Say no. Say what you built that solves the same
problem. Say how fast you would pick it up. Never bluff.**

**"Have you used LangChain?"**
> At codelab level — the Google ADK track wraps LangChain community tools
> through an adapter, and I have run that. I have not built a production system
> on it. What I have done is build the equivalent by hand: six specialist agents
> voting into an aggregator with shared state and a confidence contract. I know
> what `StateGraph` is doing because I wrote that logic myself.

**"Have you used LangGraph / CrewAI / AutoGen?"**
> No. My multi-agent work is Google ADK and a hand-rolled system in Python. The
> concepts map directly — agents, tools, shared state, routing — so the ramp is
> days, not weeks. LangGraph is the closest to what I built.

**"Have you used Kubernetes?"**
> No. My deployments are Cloud Run for containers that scale to zero and
> Compute Engine under systemd for the long-running daemon. I understand the
> problems Kubernetes solves — orchestration, scaling, self-healing — because I
> solved the small version with systemd, watchdogs and health checks. I have not
> run a cluster.

**"Have you used Pinecone / Weaviate / Chroma?"**
> No, I used pgvector in Postgres. The concepts are identical — embeddings,
> cosine similarity, top-k, index tuning. The trade-off I made deliberately: no
> extra service to run, and it works on any Postgres.

**"Have you fine-tuned a model?"**
> No. I have trained classical models — gradient boosting, CNNs, logistic
> forecasters — and I have built the validation infrastructure that decides
> whether a retrained model ships. For LLMs I have used prompting and retrieval,
> which is usually the right first answer for adding knowledge.

**"How much Node/Express?"**
> Ramp-up, not lead. I have shipped React, Next.js and TypeScript in production
> at AutoKorrekt, and Tailwind on my own work. My backend depth is Python —
> FastAPI, Flask, Django-adjacent. I would not claim to be the person you want
> owning an Express service on day one.
