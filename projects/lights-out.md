# Lights Out: a Hermes Agent plugin that asks before spending

**Nous Research Hermes Agent Plugin Hackathon, Nov 2026.** Built Nov 10–11, submitted Nov 12 (about 01:00 IST). Nous merged the catalog entry (NousResearch/hermes-agent PR #153822), so Lights Out is listed in the official Hermes plugin catalog. Prize results: pending when written (11-16).
**Code:** [github.com/JannetEkka/lights-out](https://github.com/JannetEkka/lights-out) · **Catalog PR:** [#153822](https://github.com/NousResearch/hermes-agent/pull/153822) · **Demo (74 s):** [X post](https://x.com/EkkaJanny96/status/2120602670750912581) · tracker [DSProjects#93](https://github.com/JannetEkka/DSProjects/issues/93)

## The 30-second version

An agent that can run the AWS CLI can leave things running and billing after it says "Done". Lights Out hooks Hermes's `pre_tool_call`: every billable create (7 resource types) goes to Hermes's own approval prompt with its monthly price from a dated AWS price table. `post_tool_call` writes a ledger line with the delete command. After any turn that changed the ledger, a receipt shows what is still running and its cost. `/lights out` turns everything off except resources a person kept on purpose until a date.

## 1. Architectural reasoning

### Database / storage
- **A local JSON-lines ledger** in the profile's plugin-data directory. Append-only, replayable, and it survives damaged lines (tested). No database: one user, one machine, and nothing should leave it.
- **A dated price table** (`prices/aws-us-east-1.yaml`) built from AWS's public price list files on 2026-11-10. A type not in the table shows "price unknown"; prices are never guessed.

### Compute & hosting
- Runs inside Hermes (v0.23.1 floor). No server, no network of its own, no keys: the optional one-line receipt summary uses `ctx.llm` on the user's own provider.

### Frameworks & libraries
- **Hermes plugin hooks**, because a skill is only text the agent reads; it can't block a command. A hook returning `{"action": "approve"}` hands the decision to Hermes's own approval gate, which fails closed on deny, timeout or no one present.
- **shlex-based matcher** over the command line, including `&&`, `;`, pipes and `bash -c`.
- **moto** (local AWS emulator) for every test and the measured run: no cloud account, no card.

## 2. Data & security pipelines

### Authentication & access control
- Never answers an approval and never routes around one. Under `--yolo` Hermes approves at once (the user's setting); under cron and non-TTY runs, creates are blocked.
- Only a person sets a keep. When the model calls `lights_keep`, that is a proposal sent to the approval prompt with the cost by that date, so the model can't hide a resource by marking it kept.

### Data flow
- Command → matcher → approval prompt with price → command runs → IDs read from the CLI's own output → ledger → receipt.
- Reads no secrets. AWS credentials stay with the user's CLI.

### Privacy
- Ledger holds resource IDs, sizes, prices and command lines, locally. No telemetry, no self-updater (catalog rules).

## 3. Reliability & failure operations

- If the plugin's hook raises or times out, Hermes blocks the tool. The matcher also catches its own errors and asks anyway for any command containing `aws`.
- `/lights check` compares the ledger with the cloud using read-only `describe` calls and marks a resource gone only on proof (not-found, terminated or deleted).
- Found during the build: aws-cli v1's `rds` commands ignored `AWS_ENDPOINT_URL` and reached real AWS with the dummy key (AWS rejected it, nothing created). Every aws call in tests now goes through a wrapper that forces moto.
- Found in Hermes 0.23.1: `/exit` in the CLI only detaches, so the end-of-session receipt was dropped. The receipt is now also posted after each turn that changed the ledger.

## 4. Evaluation & metrics

Hermes 0.23.1, `nvidia/nemotron-3-ultra-550b-a55b`, 10 tasks × 3 arms, a fresh moto per run, ground truth from moto:

| | A: Hermes alone | B: + clean-up prompt | C: + Lights Out |
|---|---|---|---|
| Left running unintentionally | 14 ($262.22/mo) | 1 ($3.65/mo) | 14 ($262.22/mo) before `/lights out` |
| Billable creates no person approved | 13 | 14 | **0** |
| Wrong "all clean" claims | 0 | 0 | 0 |
| After `/lights out`, still running and not kept | – | – | **0** |
| Keeps recorded for "stay up until" tasks | – | – | 2 of 2 |

- **The honest reading:** with this model, the clean-up prompt alone cleans up well, and the model reported leftovers honestly in every arm. What Lights Out adds is who decides: every billable create needed a person's yes with its price shown, and one command cleans up while keeping what should stay.
- 140 unit tests (46 matcher cases), integration 8/8 with real Hermes + moto + Nemotron, `hermes plugins doctor --ci` and `validate --install-deps` pass.

## What the history shows (real decisions)

1. 11-09: the web check found the idea already exists in parts (agent-leftovers, cloud-costaware, agent-cost-guard, rentctl). The build was paused.
2. 11-10: Jannet decided to build anyway, because the hackathon exists to fill the Hermes catalog and none of those is a Hermes plugin. The README names them and says what differs.
3. The first arm-C pass found two bugs (multi-line `aws \` commands lost their flags; RDS deletion protection blocked the delete). Both were fixed and arm C re-run; the first pass is kept in `bench/runs-first-C/`.

## Weak spots to own before they ask

- One run per task per arm, one model. With another model, or an agent that uses boto3 instead of the CLI, the numbers will differ.
- AWS CLI only; Terraform, boto3 and the console aren't seen. Emulated resources, real prices.
- In this run the receipt told the user nothing the model's reply hadn't; its value is that it doesn't depend on the model.

## Sources

The plugin README (results table, approvals, limits, related projects); DSProjects#93 comments 11-09 to 11-12; `hackathons/november-2026.md` row 4.
