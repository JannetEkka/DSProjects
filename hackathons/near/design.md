# Design brief: Aftershock (NEAR Hackathon, Investment Thesis track)

**Process (Jannet, 11-08):** the discussion session (https://claude.ai/code/session_016VDQompiU69EYpVYxKBsMY) wrote this brief on 11-13. Jannet reads it, explains it back, and signs it off; a **separate build session** then starts from section 10. Checked against [../lessons.md](../lessons.md). Tracking issue: [#85](https://github.com/JannetEkka/DSProjects/issues/85). The name **Aftershock** is a proposal until Jannet approves it.

## 0. The hackathon, in one screen

- **Link:** https://nearhackathon.com/ and its rules file https://nearhackathon.com/HACKATHON.md. No registration. Solo is fine.
- **Deadline:** **Sat Nov 15, 05:29 IST** (Nov 14, 23:59 UTC). Our own target: submitted by **Nov 14, 22:00 IST**. One submission, not editable afterwards.
- **Deliverables:** a public repo with a LICENSE file and README steps a stranger can run; a public post on X saying it was built at NEAR HACKATHON, tagging `@NEARProtocol` and `#NEARHackathon`, with a **video**; the form (project name, lead, email, team size, tracks, a **mainnet** NEAR address for the payout, repo link, post link, 20–2,000 characters on what we built; leave "website" empty, it is a spam trap).
- **Judging:** no weights published. "Previous NEAR hackathons evaluated technical implementation, design, impact, originality and sustainability." First, "Claude Code & Codex screen every project": they check that it runs and does what the README says. Humans decide. The human judges are mostly crypto investors.
- **Our track:** Investment Thesis: a long-term thesis for NEAR backed by onchain data and models anyone can re-run; "judged on the evidence, not the conviction." Prizes per track: $10K / $3K / $2K, paid in NEAR; one $55K grand prize.
- **Money:** none of ours. Testnet-only projects qualify in every track (Q-010) and testnet tokens are free (Q-008). We do not use NEAR Intents, which has no testnet (Q-007); we only *read* public figures about it. Every data source below is free and needs no key. No card anywhere, so [../cards.md](../cards.md) needs no row.

## 1. The idea

**One sentence:** for someone deciding whether to hold NEAR for years, Aftershock shows which news actually changed how much the chain is used, and which only moved the price, and writes a thesis in which every sentence had to pass a check against the chain's own daily records.

**Where it comes from (Jannet, 11-12):** news sets the bull and bear story for every coin, and a market doesn't move without an influential event. So the honest test of a thesis is the events: after each big headline, did people actually use the chain more, or did only the price jump and fade? Price reacting to news is short-term. Usage reacting to news is the long-term case.

**Why it's not the obvious entry (lessons 1):** the obvious entry in this track is a dashboard of charts with an AI-written bull case. Ours treats the news as the experiment and the chain as the judge, and it compares every event against ordinary days, so a "reaction" that happens just as often by chance is called chance.

**Closest existing work (lessons 0, searched 11-11 and 11-12):**
- [The Tie SigDev](https://thetie.io/solutions/news): a paid product that tags news by coin and tracks market reactions. Not open, no chance comparison, no checked thesis.
- [crypto-event-study](https://awesome.ecosyste.ms/api/v1/projects/github.com%2Fstudiofarzulla%2Fcrypto-event-study): academic event-study code for crypto prices. Not about chain usage or NEAR.
- [CRE Fact-Checker](https://chain.link/hack-26/projects/cre-fact-checker): checks ETH price claims and stores verdicts on-chain. Price claims only.
- [DYOR.bot](https://hackquest.io/projects/DYOR): labels claims VERIFIED / AMBIGUOUS / UNRESOLVED.
- [CryptoAnalystBench](https://arxiv.org/abs/2602.11304): a research benchmark showing AI crypto analysis fails in ways ordinary fact checks miss. We cite it as the reason the check exists.
- **Our own Countersign** (Mozilla Otari hackathon, 11-12): one model writes, another checks, code decides, on 2019 Apple news. Aftershock reuses that keep-or-remove rule as its last step. What is new here: the event test against ordinary days, chain usage as the evidence, and forecasts recorded on NEAR. The README names Countersign as earlier work (rule Q-005).
- Honest note: event studies and claim checkers both exist. We found nothing that joins them for a chain's usage, on NEAR or elsewhere.

**Ideas considered and dropped:** Leash (an AI paying invoices behind spending rules): IntentGuard, Exequatur, AuditShield and OutLayer already do it, and it is the track's own starter. Chit circle (savings circle in a contract): more than 15 exist since 2017, and it has no measured comparison.

## 2. The measured comparison (decide before building)

Three numbers, all reported even if they come out badly.

**A. Events against ordinary days.** An *event day* is a day when news coverage of NEAR spikes (fixed rule in section 4). For each event day and each measure (price, transactions, active accounts, new accounts, DEX volume, Intents volume) we compute the change from the 28 days before to the 7 days after. We compute the same change for every ordinary day. An event "moved" a measure only if its change is outside the middle 95% of the ordinary-day changes. By chance alone about 5% of events would pass, and we print that next to the result. **The number:** "of N news events, X moved the price, Y moved usage."

**B. An AI alone against the data.** The same models are asked for a NEAR thesis with figures, with no data given. Code checks each numeric claim against the dataset. **The number:** "K of M checkable figures were right." Claims our data can't check are counted separately as "uncheckable", never as wrong.

**C. Our thesis, check on and off.** Claims written by the Bull and the Bear, claims removed, and why.

**What we'll say if it's not good:** if news moves usage no more often than chance, that *is* the finding ("NEAR's usage doesn't follow its headlines") and the thesis is written from it. If the AI alone is mostly right, we say so. Caveats to state: news spikes are a rough stand-in for "influential events"; several events can overlap; 7 days is one choice of window and the README shows 3 and 14 days too.

## 3. What a judge sees in the first 10 seconds

- A long strip of chart paper, like a seismograph. The top trace is price, the bottom trace is active accounts. Each news event is a pin on the strip with its headline.
- Each pin is stamped: **moved usage**, **price only**, or **nothing**. Above the strip: "N events. X moved the price. Y moved usage. Chance alone: 5%."
- Below: the thesis. Sentences that passed are in black with a small mark that opens the query and the figure; removed claims are struck through with the reason.
- A panel of forecasts, each with a due date and a "recorded on NEAR testnet" link.
- **Headline:** "Did the news move the chain?" (six words)
- **Look:** recording-instrument paper: pale grid, thin ink traces, monospace labels. One accent colour, a seismograph red, used only for events that moved usage. Motion: the strip draws left to right and the stamps land one at a time.

## 4. Architecture

```
FREE PUBLIC DATA (no keys)                         MODELS (NVIDIA free endpoints)
 NearBlocks charts: 2,305 days, 2020-07-21 →        
   price, txns, active/new accounts, fees           
 DefiLlama: TVL, DEX volume, stablecoins,           
   NEAR Intents volume (702 days)                   
 GDELT: daily count of news about NEAR, headlines   
        │                                           
        ▼                                           
 [1] Snapshot: save everything to data/, fingerprint it (SHA-256)
        │
 [2] Event finder (code): days where news count spikes
        │                         ┌──────────────────────────────┐
        ├── headlines of each day ─► [3] Labeller model: what was it about? │
        ▼                         └──────────────────────────────┘
 [4] Event test (code): each event vs all ordinary days → moved / not
        │
        ├─► [5] Bull model  ─┐  each writes claims as data:
        ├─► [6] Bear model  ─┤  {measure, dates, figure, event ids}
        │                    ▼
        │            [7] Recompute (code): run each claim's figure from the snapshot
        │            [8] Examiner model (other family): do the cited events support the wording?
        │            [9] Decision rule (code): keep or remove
        │                    ▼
        │            [10] Judge model: writes the thesis from kept claims only
        │            [11] Final check (code): every sentence cites kept claims, or it is cut
        ▼                    ▼
 [12] NEAR testnet contract: snapshot fingerprint, run verdict counts, forecasts with due dates
        ▼
 results.json ─► static page (GitHub Pages)
```

**Terms.** *Snapshot*: a saved copy of the data, so everyone checks against the same numbers. *Fingerprint (hash)*: a short code computed from a file; change one digit in the file and the code changes, so a fingerprint stored on NEAR proves the data wasn't edited later. *Contract*: a small program living on the chain. *Testnet*: NEAR's free practice network.

**Model judgment vs fixed rules (lessons 4):**
- Models: label what an event was about; write claims (Bull, Bear); say whether the cited events support a claim's wording (Examiner); write the thesis from kept claims (Judge).
- Code: pick event days; run the event test; recompute every figure; validate every model reply (required fields, allowed values); decide keep or remove; cut any thesis sentence without a kept claim behind it. A claim is kept only if its figure matches the recomputation (within 1%), its event ids exist, **and** the Examiner says supported. The model describes, the code decides.

**The agents act on each other (lessons 7):** the Bull and the Bear see the same data and are told to argue opposite sides, and each is shown the other's claims once to rebut them. The Examiner is from a different model family and sees only a claim and its events, never the writer's reasoning. The Judge can't use anything the code removed.

**NEAR's concrete role:** (a) NEAR's own mainnet history is the evidence (read-only, free). (b) A contract on testnet stores the snapshot's fingerprint, the run's counts, and each forecast with its due date, posted *before* the outcome is known. After the due date anyone runs `make settle`: it recomputes the figure and records the result and the new fingerprint. The contract can't see mainnet data itself, so it is a public, timestamped notebook, not an automatic referee; the README says this plainly.

**Hosting and cost:** Python scripts and one small Rust contract. Static page on GitHub Pages (free). Models: NVIDIA build.nvidia.com free endpoints, two different families. Everything free.

## 5. The flow, step by step

1. `make live` fetches the three sources (GDELT at one request per 5 seconds, its stated limit), writes `data/`, and fingerprints it. `make replay` skips this and uses the committed snapshot and recorded model replies, so it needs **no keys and no network**. The AI screeners and judges run `make replay`.
2. Event finder: a day is an event when its news count is above the 95th percentile of the previous 90 days; spikes within 3 days merge into one event.
3. Labeller gives each event a type (upgrade, partnership, listing, security, people, market-wide, other) and a one-line summary from that day's headlines. A reply outside the allowed types is retried once, then recorded as "unlabelled".
4. Event test (section 2A) for every event and measure.
5. Bull and Bear each return claims as JSON; each sees the other's once and may add rebuttals.
6. Code recomputes each figure; Examiner judges wording; decision rule keeps or removes with a reason.
7. Judge writes the thesis; final check cuts unsupported sentences.
8. The same models write a thesis with no data; code scores it (section 2B).
9. Bull and Bear each propose forecasts from a fixed menu (a measure, a threshold, a due date); code checks the form; they are posted to the contract.
10. Write `results.json`; build the page.
11. Bad input: a source that fails or returns too few days stops the run and names the source; nothing is published from partial data. A measure with missing days in an event's window is "not tested" for that event, not "nothing" (lessons 8, 9).

## 6. Decisions settled now

- **Track:** `thesis` only.
- **No Intents, no BigQuery (GCP), no paid data.** Santiment is not used: the only key in the environment is an old one, and our rule is a new key per entry.
- **News source:** GDELT, a free public index of world news. Google News feeds were checked and rejected: their terms forbid this use.
- **Windows:** 28 days before, 7 after; 3 and 14 shown as a sensitivity table.
- **Models:** two open models from different families on build.nvidia.com, chosen at build time from what answers. Jannet creates a **new** key named `aftershock`; the build session asks for it through the secure form. Environment variable: `NVIDIA_API_KEY`. Never pasted in chat.
- **Repo:** Jannet creates a new public repo `aftershock` (empty, MIT licence) and gives the Claude GitHub app access. The entry's repo holds the project only.
- **Testnet account:** the build session creates a fresh testnet account from the faucet. It holds nothing of value; its key stays out of the repo.
- **Payout account (Jannet, by Nov 14):** a mainnet NEAR account made in any NEAR wallet. Free; send nothing to it.
- **No build log in the repo** (lessons 6: this hackathon doesn't grade one).

## 7. Acceptance conditions

- [ ] `make replay` runs from a clean clone with no keys and no network, and rebuilds `results.json` and the page identically.
- [ ] `make live` refetches all three sources and stops with a clear message if one fails.
- [ ] The event test prints, per measure, events tested, events moved, and the 5% chance line; the sensitivity table shows 3, 7 and 14 days.
- [ ] Every kept claim has a recomputed figure within 1%, existing event ids, and an Examiner "supported". Unit tests cover the decision rule, reply validation and the event test (including a made-up series with a known jump).
- [ ] Every thesis sentence links to kept claims. THESIS.md has the claim, evidence for, evidence against, and what would change our mind.
- [ ] The AI-alone score is reported as right / wrong / uncheckable.
- [ ] The contract is deployed on testnet; the snapshot fingerprint, run counts and at least 3 forecasts are on it; the page shows explorer links; `make settle` works on a test forecast.
- [ ] Page: the six-word headline; the strip chart on the first screen; red only for "moved usage"; the drawing-and-stamping motion; works on a phone.
- [ ] README: the impact with its numbers and what they are compared with; "do X, see Y" steps; libraries used; Countersign named as earlier work; the closest projects; what is implemented and what is only proposed.
- [ ] No keys in the repo history; LICENSE present.

## 8. Demo plan

No length limit is given; we aim for 90 seconds, Jannet's screen and voice.
1. (10 s) "Every coin has a story made of headlines. I asked NEAR's own chain which headlines mattered."
2. (30 s) The strip draws; the stamps land; the three numbers.
3. (25 s) The thesis: click a sentence to see its figure; a struck claim and why; the AI-alone score.
4. (15 s) A forecast on the testnet explorer, with its due date.
5. (10 s) `make replay` in a terminal; the repo link.

UI step: 2–3 directions on a Claude Design canvas before any UI code, if time allows; otherwise the look in section 3 is the direction.

## 9. Jannet's check

Answer in your own words before sign-off:
1. What makes a day an "event", and who decides: a model or the code?
2. Why do we compare events with ordinary days, and what does "chance alone: 5%" mean?
3. What three things must be true for a claim to stay?
4. What does the NEAR contract store, and what can't it do?
5. Why can a judge run it without any keys?
6. What is built today, and what is only planned?

- Jannet's answers and gaps fixed: *(to fill)*
- **Signed off:** *(Jannet, date)*

## 10. The build prompt

> Build Aftershock from `hackathons/near/design.md` in JannetEkka/DSProjects (branch `claude/near-design` if not merged). Read that brief and `hackathons/lessons.md` first. Work in the new public repo `JannetEkka/aftershock`; open PRs, never push to main. Order of work: (1) snapshot fetchers for NearBlocks `/v1/charts`, DefiLlama (chain TVL, DEX volume, stablecoins, `summary/dexs/near-intents`) and GDELT (one request per 5 seconds), with SHA-256 fingerprints; (2) the event finder and event test with unit tests, including a synthetic series with a known jump; (3) the claim pipeline: Bull, Bear, recompute, Examiner (different model family), decision rule, Judge, final check, with every model reply validated and recorded for replay; (4) the AI-alone baseline; (5) a small Rust contract on NEAR **testnet** (snapshot fingerprint, run counts, forecasts, settle) on a fresh faucet account, never mainnet, never NEAR Intents; (6) the static page from section 3, on GitHub Pages; (7) README and THESIS.md. Models describe and code decides: a claim is kept only if its figure matches the recomputation within 1%, its event ids exist, and the Examiner says supported. `make replay` must run with no keys and no network. Models go through build.nvidia.com with the key in `NVIDIA_API_KEY`, asked for through the credential form, never in chat. Spend no money; if anything asks for a card, stop and record it in `hackathons/cards.md`. Report every number as measured, with what it is compared with, and invent no baseline. Meet every acceptance condition in section 7 and tick issue #85's checklist. Deadline: ready for Jannet to record by Nov 14, 14:00 IST; submitted by 22:00 IST; hard close Nov 15, 05:29 IST. Show Jannet the full submission payload and wait for her OK; she submits.
