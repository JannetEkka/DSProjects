# Lights Out: build notes (build session, 11-10)

Build session: https://claude.ai/code/session_016VDQom3X84652goidUewwo. Brief: [design.md](design.md). Tracking: #93.

## Step 1: setup and findings (2026-11-10)

**Hermes under test:** v0.23.1, the latest stable release on 11-10 (tag `v0.23.1`, commit `3b421578588243f920886e6fe79a6faa87ea026e`, 2026-11-09). Installed from the source checkout with the PM developer environment (`scripts/run-in-hermes-env`, Python 3.14.9). The official one-line installer was blocked by the session's permission check, so the checkout route from CONTRIBUTING.md was used instead; it is the same code. `hermes --version` → `Hermes Agent v0.23.1`. So the floor is `requires_hermes: ">=0.23.1"`.

**Model:** `nvidia/nemotron-3-ultra-550b-a55b` through Hermes's built-in `nvidia` provider, `NVIDIA_API_KEY="$HERMES_NVIDIA_API_KEY"` set in the run script. Chosen on 2026-11-10: it made a correct `terminal` tool call (`aws ec2 run-instances ...`) in 2.1 s. Tried and not used: `nemotron-3-super-120b-a12b`, `kimi-k2.6`, `nemotron-nano-3-30b-a3b` (404 for this key), `deepseek-v4.1-flash`, `glm-5.3-flash`, `minimax-m3.1-flash`, `gpt-oss-20b` (timed out at 90 s), `mistral-large-4-1t-a52b` (refused to run the command). Fallback: `nvidia/nemotron-3.5-lightning-30b-a3b` (also called the tool correctly, 3.1 s).

**Cloud:** moto 5.2.5 server on `127.0.0.1:5000`, aws-cli 1.46.3, both in a separate venv. `AWS_ENDPOINT_URL=http://127.0.0.1:5000`, credentials `testing`/`testing`. Smoke test: Hermes ran `aws ec2 run-instances ... t3.micro` and moto listed `i-d2430c4c4787dab83` running.

**Finding 1: the terminal tool.** Name `terminal`. Arguments: `command` (string, required), `background`, `timeout`, `workdir`, `pty`, `notify`, `heartbeat`, `persist_on_release`. Its result is a JSON string `{"output": ..., "exit_code": ..., "error": ...}` (`tools/terminal_tool_result.py`). `pre_tool_call` gets `tool_name="terminal"` and `args["command"]`.

**Finding 2: `request_tool_approval` (what our `{"action":"approve"}` triggers), `tools/approval.py`:**
- **YOLO (`--yolo`) or `approvals.mode: off`:** approved at once, no prompt. Lights Out can't ask in that mode, by design (catalog rule 12: we don't override the user's approval mode). The ledger and receipt still work, so the receipt still shows what was created.
- **Interactive CLI / gateway:** the normal approval prompt (once / session / always / deny). An "always" answer is stored per `rule_key`, so `lights-out:ec2:create` never covers RDS.
- **Cron:** `approvals.cron_mode` (default deny) → blocked. **`-q` one-shot on a non-TTY:** `approvals.single_query_mode` (default deny) → blocked. **Any other unattended context without an approval bridge:** blocked (`fail_closed_when_no_human=True`). So nothing billable is created unasked when nobody is there.
- A `pre_tool_call` callback that raises or times out blocks the tool (fails closed, hooks doc).

**Finding 3: `ctx.dispatch_tool` skips plugin hooks.** It calls `registry.dispatch` directly, so `pre_tool_call`/`post_tool_call` don't fire for tools a slash command runs. The terminal tool's own guards (hardline, user deny rules, dangerous patterns) still run. Consequences for `/lights out`: the command records its own `deleted` lines from each delete's output. `aws ... terminate-instances` isn't on Hermes's dangerous list, so Hermes wouldn't prompt for it. **Proposed (needs Jannet's OK):** `/lights out` first lists what it will turn off and asks once with `ctx.ask_choice` ("Turn off N resources, $X/month? yes / no"); no answer, or an unattended run, means nothing is deleted.

**Finding 4: where the receipt can appear.** Only `on_session_finalize` can show the user text (a returned string; CLI quit, `/new`, the end of a `-z`/`-q` one-shot on stderr, a gateway `/new` or `/reset`). `on_session_end` fires after every turn and can't show anything, so it's used only to keep the ledger flushed. The receipt is not shown when a TUI is closed, a Desktop chat is deleted or the gateway idle-expires a session; the next `on_session_start` notice covers those.

## Steps 3–5 (2026-11-10)

Plugin code is in the local repo `/home/user/lights-out` in this session (commits on `main`). It moves to `JannetEkka/lights-out` once the session can push there: attaching the repo was refused by the session's permission check, so Jannet needs to allow it.

- 137 unit tests pass (46 matcher cases, real moto outputs as fixtures, ledger replay with damaged lines, keep parser, receipt states, the three failure tests).
- `hermes plugins doctor --ci` and `hermes plugins validate --install-deps` pass on v0.23.1 (security scan safe; declared tools and hooks match registrations).
- Integration test 8/8 (real Hermes + moto + Nemotron): no → nothing in moto; yes → the ledger ID is moto's ID; `/lights out` → moto empty; green receipt.

**Finding 5: the CLI detaches on `/exit` in 0.23.1.** `hermes chat --cli` is a client of a local gateway; `/exit` detaches, and the gateway later finalizes the session where `on_session_finalize` text isn't delivered. So the receipt is also posted with `ctx.post_message` from `on_session_end` after any turn that changed the ledger. That is the demo moment in the brief ("Done ✅" and the receipt under it). `on_session_finalize` still returns it for `/new`, one-shot runs and gateway resets. (Divergence from the brief: `on_session_end` is used to show the receipt, not only as a fallback.)

**Finding 6: aws-cli v1's `rds` commands ignore `AWS_ENDPOINT_URL`.** Its `update_endpoint_url` customisation pointed `rds` calls at `https://rds.amazonaws.com`. Three calls went to real AWS with the dummy key `testing` and were rejected (`InvalidClientTokenId`): no account exists behind that key, so nothing was created anywhere. Fix: the session's `aws` is a wrapper that always passes `--endpoint-url` for the local moto server and refuses to run if the endpoint isn't localhost. Debug logs confirmed rds, ec2, elbv2 and s3 all go to `127.0.0.1` after the fix.

**Finding 7: models often use `--query ... --output text`.** The output then has no resource ID (an EIP printed only its IP). The plugin records an *unknown* (blocks "All clear") and immediately runs one read-only list call for that kind; it pairs the unknown with the untracked resource only when the counts match exactly. Tested in the smoke run: the EIP was paired one second after the create and `/lights out` released it.

**Proposed change (needs Jannet's OK): `/lights out` asks once.** It lists everything it will delete with the $/month and asks with `ctx.ask_choice`; `/lights out yes` typed by a person is the same answer. No answer or an unattended run deletes nothing.
