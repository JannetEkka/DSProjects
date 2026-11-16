# Lore: the first 40 projects to write to

**What this is:** the open-source projects we'll offer a free Lore report to, to find Lore's first users (plan, part 2). Picked 11-16 from GitHub searches for active projects, then measured: **merged PRs** = PRs merged in the 6 months to 11-16 (GitHub search); **people** = distinct non-bot authors among the latest 100 of those PRs (so it tops out near 100 and undercounts busy projects). Kept: 40+ merged PRs and 5–50 people, so "who knows this part?" is a real question and a maintainer still reads their own messages. Big-company repos (PyTorch, HashiCorp, Grafana, Kubernetes) were left out: their maintainers have internal tools and slower answers.

**How each one gets used:** Lore's Report job ([lore PR #1](https://github.com/JannetEkka/lore/pull/1)) runs on the project and lists who wrote and reviewed what, and which areas rest on one person. Claude picks the two clearest findings and writes the message; Jannet sends it where the project talks (GitHub Discussions if it has them, else the chat linked in its README). We log each send and reply below.

**First run done (11-16):** [lore Actions run](https://github.com/JannetEkka/lore/actions/runs/43882177521), 10 projects, report in the job summary and the `lore-report` artifact. Message drafts are given in chat, not kept in this public repo, because they name maintainers.

**Status key:** `report` = report done in the first run · `next` = later runs, 10 at a time.

| # | Project | Merged PRs (6 mo) | People | Stars | Where to write | Why it's on the list | Status |
|---|---|---|---|---|---|---|---|
| 1 | [FalkorDB/GraphRAG-SDK](https://github.com/FalkorDB/GraphRAG-SDK) | 67 | 10 | 1036 | chat or issue tracker linked in README | Warm: they've met Lore or us: Lore was built on FalkorDB and demoed on their repos; the Graph Hacks sponsor | report |
| 2 | [mozilla-ai/otari](https://github.com/mozilla-ai/otari) | 1842 | 11 | 932 | GitHub Discussions | Warm: they've met Lore or us: We entered Mozilla's Otari hackathon on 11-12 | report |
| 3 | [ossf/scorecard](https://github.com/ossf/scorecard) | 106 | 12 | 5843 | GitHub Discussions | People who measure project health for a living: OpenSSF's project-health checks; bus factor is their topic | report |
| 4 | [neo4j/neo4j-graphrag-python](https://github.com/neo4j/neo4j-graphrag-python) | 147 | 12 | 1335 | chat or issue tracker linked in README | Graph databases: Graph database or graph tooling | report |
| 5 | [memgraph/memgraph](https://github.com/memgraph/memgraph) | 587 | 9 | 4661 | GitHub Discussions | Graph databases: Graph database or graph tooling | report |
| 6 | [apache/age](https://github.com/apache/age) | 74 | 18 | 4944 | GitHub Discussions | Graph databases: Graph database or graph tooling | report |
| 7 | [oxigraph/oxigraph](https://github.com/oxigraph/oxigraph) | 175 | 8 | 2048 | GitHub Discussions | Graph databases: Graph database or graph tooling | report |
| 8 | [terminusdb/terminusdb](https://github.com/terminusdb/terminusdb) | 139 | 5 | 3483 | GitHub Discussions | Graph databases: Graph database or graph tooling | report |
| 9 | [Pometry/Raphtory](https://github.com/Pometry/Raphtory) | 155 | 12 | 654 | GitHub Discussions | Graph databases: Graph database or graph tooling | report |
| 10 | [apache/tinkerpop](https://github.com/apache/tinkerpop) | 260 | 8 | 2157 | chat or issue tracker linked in README | Graph databases: Graph database or graph tooling | next |
| 11 | [apache/hugegraph](https://github.com/apache/hugegraph) | 232 | 8 | 3208 | GitHub Discussions | Graph databases: Graph database or graph tooling | next |
| 12 | [pgmpy/pgmpy](https://github.com/pgmpy/pgmpy) | 74 | 25 | 3386 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | report |
| 13 | [pylint-dev/pylint](https://github.com/pylint-dev/pylint) | 425 | 32 | 5750 | chat or issue tracker linked in README | Python science and data libraries: Community library with outside contributors | next |
| 14 | [nilearn/nilearn](https://github.com/nilearn/nilearn) | 357 | 16 | 1456 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 15 | [torchgeo/torchgeo](https://github.com/torchgeo/torchgeo) | 442 | 7 | 4246 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 16 | [pymc-labs/pymc-marketing](https://github.com/pymc-labs/pymc-marketing) | 420 | 27 | 1310 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 17 | [deepinv/deepinv](https://github.com/deepinv/deepinv) | 169 | 21 | 854 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 18 | [sunlabuiuc/PyHealth](https://github.com/sunlabuiuc/PyHealth) | 221 | 20 | 1699 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 19 | [PyCalendar/icalendar](https://github.com/PyCalendar/icalendar) | 304 | 50 | 1190 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 20 | [jelmer/dulwich](https://github.com/jelmer/dulwich) | 252 | 6 | 2297 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 21 | [widgetti/solara](https://github.com/widgetti/solara) | 91 | 5 | 2180 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 22 | [undertheseanlp/underthesea](https://github.com/undertheseanlp/underthesea) | 63 | 7 | 1817 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 23 | [embeddings-benchmark/mteb](https://github.com/embeddings-benchmark/mteb) | 657 | 39 | 3517 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 24 | [django/djangoproject.com](https://github.com/django/djangoproject.com) | 204 | 20 | 2024 | chat or issue tracker linked in README | Python science and data libraries: Community library with outside contributors | next |
| 25 | [nvaccess/nvda](https://github.com/nvaccess/nvda) | 426 | 26 | 2693 | GitHub Discussions | Python science and data libraries: Community library with outside contributors | next |
| 26 | [opsmill/infrahub](https://github.com/opsmill/infrahub) | 1503 | 13 | 551 | chat or issue tracker linked in README | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 27 | [perses/perses](https://github.com/perses/perses) | 384 | 19 | 2538 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 28 | [zarf-dev/zarf](https://github.com/zarf-dev/zarf) | 424 | 15 | 2097 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 29 | [pipe-cd/pipecd](https://github.com/pipe-cd/pipecd) | 476 | 25 | 1371 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 30 | [kptdev/kpt](https://github.com/kptdev/kpt) | 179 | 22 | 1910 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 31 | [stackql/stackql](https://github.com/stackql/stackql) | 166 | 11 | 1095 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 32 | [tofuutils/tenv](https://github.com/tofuutils/tenv) | 48 | 14 | 1466 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 33 | [borgbase/vorta](https://github.com/borgbase/vorta) | 56 | 15 | 2531 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 34 | [mariadb-operator/mariadb-operator](https://github.com/mariadb-operator/mariadb-operator) | 115 | 20 | 1038 | chat or issue tracker linked in README | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 35 | [pantsbuild/pants](https://github.com/pantsbuild/pants) | 292 | 21 | 3857 | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 36 | [kubearmor/KubeArmor](https://github.com/kubearmor/KubeArmor) | 105 | 17 |  | GitHub Discussions | Infrastructure and developer tools: Infra project with a core team plus outside contributors | next |
| 37 | [gptme/gptme](https://github.com/gptme/gptme) | 2011 | 6 | 4483 | GitHub Discussions | AI tools: Terminal AI agent | next |
| 38 | [lmnr-ai/lmnr](https://github.com/lmnr-ai/lmnr) | 656 | 6 | 3493 | GitHub Discussions | AI tools: Observability for AI agents (YC S24) | next |
| 39 | [Giskard-AI/giskard-oss](https://github.com/Giskard-AI/giskard-oss) | 246 | 12 | 5956 | GitHub Discussions | AI tools: Testing for LLM agents | next |
| 40 | [marketcalls/openalgo](https://github.com/marketcalls/openalgo) | 285 | 15 | 3012 | GitHub Discussions | AI tools: Indian open-source trading platform; close to SMT's world | next |

## Send log

| Date | Project | Channel | Sent by | Reply? | Ran Lore themselves? | Call? | Notes |
|---|---|---|---|---|---|---|---|

We count: messages sent, replies, people who ran Lore or read the full report, calls, repeat use, and anyone who asks about a paid version. After 20 sends we'll know the reply rate; nothing here guesses it in advance.

