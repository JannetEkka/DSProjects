# Part 1 — What I have actually built

Every claim here points at code. The "depth" column is the honest one: it is what
decides how a question about that skill should be answered.

**Depth key**

| | meaning | how to answer a question about it |
|---|---|---|
| **Built** | designed and shipped it | lead with it, go as deep as they want |
| **Used** | used it in a shipped project, did not design it | answer confidently, name the project |
| **Lab** | completed a codelab or course exercise | say "codelab level" unprompted, then pivot to the built equivalent |
| **No** | never used it | say no, then say what I built that solves the same problem |

---

## Projects

| Project | What it is | Where |
|---|---|---|
| **Smart Money Trading (SMT)** | Patent-pending multi-agent trading system. 6 persona agents → learned Judge → risk gate → execution. 33K lines, 153 modules, 166 tests. Live on GCP. | private core; public layer `smt-apac` |
| **SmartDesk** | Multi-agent assistant. ADK orchestrator → inbox / planner / knowledge sub-agents. Own MCP servers. RAG with a measured eval harness. | `github.com/JannetEkka/smartdesk` |
| **VerseCanvas** | Poem → art. Gemini analysis → prompt engineering → Imagen on Vertex AI → editing. 2,600 lines. | `github.com/JannetEkka/versecanvas` |
| **Smart Money Tracker** | Multi-agent whale tracking, 3 chains, OpenServ SDK, Alchemy webhooks. **Won Best DeFi Application.** | private |
| **Location Intelligence Agent** | ADK agent over two remote MCP servers (BigQuery + Google Maps). | `github.com/JannetEkka/bakery-growth-agent` |
| **AutoKorrekt** | AI answer-evaluation for teachers. Textract OCR + Comprehend, S3/RDS/SageMaker pipeline, 1,000+ concurrent submissions. | private |
| **Asha Chatbot** | Context-aware chatbot, JobsForHer Foundation. | `github.com/JannetEkka/asha-chatbot` |
| **WebContentQnA** | Extractive QA over web pages with DistilBERT. | `github.com/JannetEkka/WebContentQnA` |
| **Automotive Surveillance (capstone)** | ResNet50 classification 69.2%, Fast R-CNN detection, 16,185 images / 196 classes. | `DSProjects/` |
| **11 further ML projects** | Churn 81.5%, semiconductor yield over 591 sensors, SVHN, sentiment with Mistral-7B embeddings, K-Means + PCA-SVM, SQL analytics, applied statistics. | `DSProjects/` |
| **Yatra automation framework** | Hybrid Selenium + POM, data-driven, cross-browser, Jenkins. | `github.com/JannetEkka/python-automation` |

---

## Skills, with evidence

### Agents and orchestration

| Skill | Depth | Evidence |
|---|---|---|
| Multi-agent architecture | **Built** | SMT `smt/personas/` — 6 personas + `judge.py` aggregating weighted votes |
| Google ADK | **Built** | SmartDesk `agent.py` — root orchestrator, sub-agents, `SequentialAgent` |
| Agent state passing | **Built** | `tool_context.state["USER_REQUEST"]`, `output_key="inbox_data"` |
| A2A SDK | **Used** | Track 1 codelab, 17 references in `gcp-ai-labs` |
| OpenServ SDK | **Built** | Smart Money Tracker (award-winning, repo private) |
| LangChain | **Lab** | Track 1 Cloud Run codelab — `LangchainTool` wrapping `WikipediaQueryRun` |
| LangGraph / CrewAI / AutoGen | **No** | — |

### Tools and MCP

| Skill | Depth | Evidence |
|---|---|---|
| MCP servers (writing them) | **Built** | `smartdesk/.../mcp_servers/gmail_server.py`, `calendar_server.py` — `Server()`, `stdio_server()` |
| MCP clients / toolsets | **Built** | `MCPToolset(StdioServerParameters(...))` in `tools.py` |
| Remote MCP servers | **Used** | BigQuery + Google Maps MCP, Location Intelligence agent |
| Function tools | **Built** | `search_notes`, `get_contacts`, `add_task` — typed signatures + docstrings |

### RAG and retrieval

| Skill | Depth | Evidence |
|---|---|---|
| RAG pipeline end to end | **Built** | SmartDesk `rag/` — chunking, embeddings, retrieval, rerankers |
| pgvector / Postgres | **Built** | `VECTOR(768)`, cosine `<=>`, `001_note_chunks.sql` |
| Chunking with overlap | **Built** | `rag/chunking.py` — token-based, sentence-aligned, 180/40, title-prefix fix |
| Reranking | **Built** | `rag/rerankers.py` — RRF, BM25, cross-encoder, Gemini reranker |
| Vector search at scale | **Built** | BigQuery `ML.GENERATE_EMBEDDING` + `VECTOR_SEARCH` over 173K decisions |
| AlloyDB | **Used** | SmartDesk production target |

### Evaluation — the rarest thing here

| Skill | Depth | Evidence |
|---|---|---|
| Retrieval eval harness | **Built** | `evals/harness.py`, `metrics.py` — recall@k, MRR@k |
| Statistical significance | **Built** | Paired bootstrap, 10,000 resamples, 95% CI |
| Overfitting gates | **Built** | `smt/learning/validation/` — CPCV, DSR, PBO, FDR, conformal |
| Faithfulness checking | **Built** | `smt/learning/faithfulness.py` — counterfactual: does the stated reason match the decision |
| Forward vs backtest validation | **Built** | P(up) forecaster — AUC 0.723 on 27 *non-overlapping* 4h windows |

### LLM and GenAI

| Skill | Depth | Evidence |
|---|---|---|
| Gemini / Vertex AI | **Built** | `genai.Client(vertexai=True)`, sentiment fetcher, SMT World chat |
| Imagen | **Built** | VerseCanvas generation pipeline |
| Prompt engineering | **Built** | SMT World persona prompt, VerseCanvas prompt synthesis |
| Embeddings | **Built** | `text-embedding-005`, MiniLM, BigQuery embeddings |
| Hugging Face / transformers | **Used** | Mistral-7B embeddings (sentiment), DistilBERT (WebContentQnA) |
| Fine-tuning | **No** | — |

### Cloud and infrastructure

| Skill | Depth | Evidence |
|---|---|---|
| Cloud Run | **Built** | SmartDesk, SMT World, smt-world-chat |
| Cloud Functions | **Built** | `cloud_functions/` — budget pause, cost digest |
| BigQuery | **Built** | 173K decisions + 447K klines, Conversational Analytics agent |
| Compute Engine + systemd | **Built** | SMT daemon, watchdog, auto-restart |
| Secret Manager | **Built** | `v4/secrets_loader.py` |
| Pub/Sub, Cloud Scheduler | **Used** | budget pause, cost digest cron |
| Cloudflare Workers | **Built** | SMT live site |
| Docker | **Used** | Dockerfiles; image slimmed 1.8 GB → 340 MB |
| AWS (S3, EC2, RDS, SageMaker, Textract, Comprehend) | **Used** | AutoKorrekt |
| Kubernetes | **No** | — |

### GPU and acceleration

| Skill | Depth | Evidence |
|---|---|---|
| NVIDIA cuDF / RAPIDS | **Built** | `cudf.pandas`, 2.5M rows, 24s → 3.9s on a T4 |
| Vertex AI GPU notebooks | **Used** | benchmark run |
| CUDA (direct kernels) | **No** | — |

### Classical ML

| Skill | Depth | Evidence |
|---|---|---|
| scikit-learn, ensembles | **Built** | churn 81.5%, semiconductor yield |
| TensorFlow / Keras / CNNs | **Built** | ResNet50, Fast R-CNN, SVHN |
| Optuna / TPE | **Built** | SMT weekly refit |
| Contextual bandits | **Built** | `smt/learning/bandit.py` — regime-aware sizing |
| Time series | **Built** | P(up) forecaster, kline pipelines |
| PyTorch | **Used** | 2 files |

### QA and testing — the bridge nobody else has

| Skill | Depth | Evidence |
|---|---|---|
| Test automation leadership | **Built** | Deloitte, 6-person team, 4 years |
| Selenium / Katalon | **Built** | 83% efficiency improvement, Yatra framework |
| CI/CD (Jenkins) | **Built** | automated reporting, 75% manual time cut |
| pytest | **Built** | 166 tests SMT, 54 tests SmartDesk |
| Enterprise systems | **Used** | HPE CPQ, AT&T, Salesforce, SAP Hybris, Walmart Sam's Club DR, ND benefits portal |
