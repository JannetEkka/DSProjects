# ---------------------------------------------------------------------------
# CREDENTIALS — every field below was read off the certificate itself.
# `files` entries are (label, path-relative-to-index.html). Spaces are
# %20-encoded because these are URLs, not filesystem paths.
# ---------------------------------------------------------------------------
C = "certificates/"
CREDENTIALS = [
 dict(title="Post Graduate Program in AI &amp; Machine Learning", issuer="Texas McCombs School of Business &amp; Great Lakes",
      date="Mar 2025", note="GPA 4.09/5 · Rank 1 in batch", kind="degree",
      files=[("Certificate", C+"pgp%20great%20lakes%20cert.pdf"),
             ("Grade book", C+"UTA%20transcript.pdf"),
             ("Verify", "https://www.mygreatlearning.com/certificate/SPXKJOPH")]),

 dict(title="Gen AI Academy — Completion", issuer="Google Cloud &amp; Hack2skill",
      date="28 May 2025", note="Vertex AI · Gemini APIs · Imagen · Streamlit · Multimodal RAG",
      cid="2025H2S04GENAI-A01917", kind="google",
      files=[("Certificate", C+"genai%20academy%20COC.pdf")]),

 dict(title="Gen AI Academy APAC 2026 — Cohort 3, Completion", issuer="Google Cloud &amp; Hack2skill",
      date="Sep 2026", note="Agentic AI on Google Cloud — the cohort Wiretrap was built in",
      kind="google",
      files=[]),

 dict(title="Gen AI Academy APAC 2026 — Cohort 2, Completion", issuer="Google Cloud &amp; Hack2skill",
      date="31 Jul 2026", note="Data, analytics and intelligent systems on Google Cloud",
      cid="2026H2S07GCGENAIAPACC2-P02585", kind="google",
      files=[("Certificate", C+"cohort%202%20cert%20comp.pdf")]),

 dict(title="Gen AI Academy APAC 2026 — Cohort 1, Completion", issuer="Google Cloud &amp; Hack2skill",
      date="28 Apr 2026", note="Building, connecting and migrating AI-powered applications",
      cid="2026H2S04GCGENAIAPACC1-P01679", kind="google",
      files=[("Certificate", C+"cohort%201%20cert%20comp.pdf")]),

 dict(title="Gen AI Academy APAC 2026 — Cohort 1 Hackathon", issuer="Google Cloud &amp; Hack2skill",
      date="19 May 2026", note="Shortlisted top 101 of 1,500+ teams",
      cid="2026H2S05GCGENAIAPACC1-P00373", kind="google",
      files=[("Certificate", C+"cohort%201%20cert%20part.pdf")]),

 dict(title="Gen AI Exchange Hackathon 2025", issuer="Google Cloud &amp; Hack2skill",
      date="14 Jan 2026", note="Problem statement — &ldquo;Automating Test Case Generation with AI&rdquo;",
      cid="2025H2S08GH-P100275", kind="google",
      files=[("Certificate", C+"GenAI%20Exc%20Hack%20COP.pdf")]),

 dict(title="Agentic AI Day", issuer="Google Cloud &amp; Hack2skill",
      date="2025", note="Build the next generation of intelligent agents",
      cid="2025H2S06AID-I01369", kind="google",
      files=[("Certificate", C+"Agentic%20AI%20DAy%20COP.pdf")]),

 dict(title="Asha AI Hackathon 2025", issuer="JobsForHer Foundation &amp; Hack2skill",
      date="2025", note="The hackathon behind the Asha Chatbot project",
      cid="2025H2S03AAIH-P00105", kind="hack",
      files=[("Certificate", C+"Asha%20AI%20Hack%20COP.pdf")]),

 dict(title="Machine Learning Internship", issuer="Internship Studio",
      date="Jul – Aug 2024", note="YouTube ad-view analytics", cid="ISMAIL600552", kind="work",
      files=[("Internship", C+"Jannet%20Ekka%20-%20Machine%20Learning%20Internship%20-%20Internship.pdf"),
             ("Training", C+"Jannet%20Ekka%20-%20Machine%20Learning%20Internship%20-%20Training.pdf")]),

 dict(title="AI-Preneur Workshop", issuer="AI-Preneur", date="Mar 2025",
      note="Freelancing with AI — business applications", kind="work",
      files=[("Certificate", C+"Jannet%20Ekka.pdf")]),

 dict(title="CPSAT — Certified Professional Selenium Automation Testing", issuer="CPSAT",
      date="2022", note="", kind="work", files=[]),
]

PROFILES = [
 ("Credly badges", "https://www.credly.com/users/jannet-akanksha-ekka/badges"),
 ("Google Skills profile", "https://www.skills.google/public_profiles/2a91b2f0-31d3-467e-ba45-3ba1888a908e"),
 ("All certificate files", "https://github.com/JannetEkka/DSProjects/tree/main/certificates"),
]

# ---------------------------------------------------------------------------
# CONTACT + FORM CONFIG  — the only things you need to edit to switch the form on
# ---------------------------------------------------------------------------
# WEB3FORMS_KEY: get a free key at https://web3forms.com — enter your email,
#   they send the access key to that inbox. Every submission then arrives there.
#   Free tier: 250 submissions/month. The key is PUBLIC by design (it is tied to
#   your email, it is not a password), so it is safe to commit.
#   While this is blank the form still renders but falls back to opening an
#   email instead of posting, so it can never silently swallow an enquiry.
#
# DISCORD: paste your invite or profile URL. Left blank = the button is not
#   rendered at all (no dead link).
CONTACT = dict(
    email="jannetekka96@gmail.com",          # general / hiring
    grants_email="jtech26smt@gmail.com",     # SMT grants & funding only
    phone="+919078802572",
    whatsapp="https://wa.me/919078802572",
    telegram="https://t.me/Jannetekka",
    discord="jannetekka_03690",      # a username, not a URL — rendered as click-to-copy
    linkedin="https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/",
    github="https://github.com/JannetEkka",
    twitter="https://x.com/EkkaJanny96",
    smt_twitter="https://x.com/JTechSMT",
    web3forms_key="",
)

# Remote-work / hiring profiles. Add a (label, url) pair as each one goes live
# and rebuild — nothing else needs changing.
# Visitor counter (Abacus — free, no signup, no key; abacus.jasoncameron.dev).
# Counts once per browser session, not per refresh, so a reload does not inflate it.
# Set enabled=False to remove it entirely.
COUNTER = dict(
    enabled=True,
    namespace="jannetekka-github-io",
    key="portfolio",
)

HIRE = [
    ("Himalayas", "https://himalayas.app/@jannetaekka"),
    ("LinkedIn", "https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/"),
]

# ---- verified link status ----
# 200 OK : workers.dev SMT, smt-mantle pages, all github repos (public via API)
# DEAD 2026-10-05: run.app SMT World (503) and wiretrap.ai.studio — both on GCP projects whose billing closed 10-02
# LIVE again 2026-10-05: Wiretrap at wiretrap.onrender.com (Render free tier + Firebase Spark + a free AI Studio key)
# user-confirmed live: versecanvas.streamlit.app
# no repo exists: Smart Money Tracker -> left blank per instruction

GH = "https://github.com/JannetEkka/"

FLAGSHIP = dict(
    slug="smt", grants=True, cat="agents", title="Smart Money Trading (SMT)",
    sub="Explainable AI Trading Agent",
    meta="Jan 2024 – Present · Founder &amp; sole engineer · JTech Solutions (pre-incorporation)",
    badge="Patent pending · IN 202631090789",
    desc="An AI trading agent for 8 crypto perpetual-futures pairs that has to prove why it traded. Written rules with replayed records open every trade. Six AI advisors explain each decision and are graded on whether they were right; one earns a veto only after 30 proven warnings. Before a reason reaches a user, the system flips that advisor&rsquo;s input and re-runs the decision, and drops the reason if nothing changes. The learning loop retunes only through a CPCV + Deflated-Sharpe + PBO + FDR overfitting gate. It places real orders 24/7 on WEEX&rsquo;s exchange-granted simulated account from a free-tier Oracle Cloud VM, and <em>SMT World</em>, a Three.js/WebGL ocean on Cloudflare Workers, lets anyone watch it trade and ask it why. It is not profitable yet, and its own receipts on Monad show that.",
    stats=[("88K","lines of Python"),("3,152","tests"),("673","findings recorded"),("362","PRs merged")],
    tags=["Multi-Agent Systems","Explainable AI","AI Evaluation","AI-Native Development","Oracle Cloud + systemd","Cloudflare Workers","Gemini (AI Studio)","Optuna","NVIDIA cuDF / RAPIDS","BigQuery","Three.js / WebGL"],
    links=[("Live site","https://smt-weex-trading-bot.jannet-ekka.workers.dev/","live"),
           ("Code","https://github.com/JannetEkka/smt-apac","code"),
           ("Press","https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641","doc")],
    note="Core repo private — the linked repo is the public explanatory layer.",
)

PROJECTS = [
 dict(slug="spona", wide=True, cat="agents", title="Spona", sub="Concurrent Agents That Match Researchers with Companies",
   meta="2026 · NTP Novi Sad Hackathon (JigJoy × Mozaik), Track 02 EINSTEIN · submitted Oct 31",
   desc="<strong>The University of Novi Sad has thousands of researchers and NTP Novi Sad hundreds of companies, yet they rarely work together.</strong> Spona is 12 agents on Mozaik, JigJoy&rsquo;s runtime for concurrent agents. They read the whole EINSTEIN dataset (1,047 researchers, 10,779 papers, 489 company challenges, about 7M tokens in English and Serbian) and give every challenge an outcome with its reason: a written proposal, a close match, no close match at the university, or not a research problem.<br><br>Every claim about a person or a company cites the record it came from. A critic agent checks those claims while the other agents are still working: rules first (the quote must be in the source, a paper must be listed as that person&rsquo;s, never matched on a name alone), then a model. Fit belongs to the pair. Title, seniority and publication counts are not inputs, and a test checks that.<br><br>In the recorded run every one of the 489 challenges got an outcome in 5 min 48 s, with up to 19 agent loops running at once. The critic sent back 33 claims that went beyond their sources, and the run found 64 research challenges that no researcher&rsquo;s own work covers, listed by sector. The whole run cost about $1.52 of Claude credit plus the Gemini free tier. The data is synthetic, so whether these pairs would actually meet is not measured yet.",
   stats=[("489","challenges, each with an outcome"),("19","agent loops at once"),("33","claims the critic sent back"),("$1.52","for the whole run")],
   tags=["Mozaik","Multi-Agent Systems","Concurrency","BM25 search","Claude Sonnet","Gemini API","TypeScript","GitHub Pages"],
   links=[("Live run","https://jannetekka.github.io/spona/","live"),("Code",GH+"spona","code")]),

 dict(slug="beautywithin", cat="cv", title="Beauty Within", sub="Your Own Colours, Tried On Your Own Photo",
   meta="2026 · YouCam API Skin AI &amp; eCommerce VTO Hackathon · submitted Nov 2",
   desc="Reads a woman&rsquo;s own colours and face shape with YouCam&rsquo;s analysers and shows one look chosen from them on her own unretouched photo: an outfit in her colours, a hairstyle for her face shape, and one lip tint at her own lip depth. The vendor&rsquo;s defaults were measured, not trusted. Its makeup render darkened lips by about 5 L*, and the calibrated render keeps them within about 2 L*. Its hair-colour try-on brightened the whole face, so hair colour was left out. Whether it lowers wrong-shade purchases is not measured yet.",
   stats=[("~2 L*","lip depth kept (was ~5 off)"),("0","skin smoothing (default 50)"),("44","API units per portrait"),("40","tests")],
   tags=["YouCam APIs","Virtual Try-On","CIELAB colour","TypeScript","Cloudflare Pages + KV"],
   links=[("Live demo","https://beauty-within.pages.dev","live"),("Code",GH+"beauty-within","code"),
          ("Demo video","https://youtu.be/ATzI4K94w44","doc")]),

 dict(slug="footfall", wide=True, cat="agents", title="Footfall", sub="A Taste Agent for Small Local Shops",
   meta="2026 · Qloo Agentic Hackathon + Nebius × NVIDIA Global AI Hackathon · submitted Oct 29",
   desc="<strong>Chains research their audience before they pick a playlist or a product line. The café on the corner guesses.</strong> Footfall asks Qloo which places within a walk of the shop the locals go to, uses those places as the signal for what the street listens to, reads and buys, and compares that with the wider area and with the shop itself. An NVIDIA Nemotron agent on Nebius Token Factory makes its own extra Qloo calls and writes a plan: a playlist, things to stock or add to the menu, and one weekend event.<br><br>Every suggestion cites the Qloo results behind it, and a checker deletes anything Qloo didn&rsquo;t return. Qloo silently ignores invalid parameters, so the client refuses any parameter its documentation doesn&rsquo;t list for that type, and the undocumented one it uses was probed live first.<br><br>A run takes 20&ndash;30 s and costs about $0.013. The LLM account has a card on file and the demo is public, so the app enforces its own cap: each run reserves its worst case in a ledger before the first call, and the whole demo stops at $15. All testing and runs so far have used $0.45. When the hackathon&rsquo;s Qloo key expires, the demo shops replay saved answers and Nemotron keeps running live. No shop owner has used it yet.",
   stats=[("$0.013","per run, 20–30 s"),("$0.45","total LLM spend, $15 cap"),("~18","Qloo calls per run"),("55","tests")],
   tags=["Qloo API","NVIDIA Nemotron","Nebius Token Factory","AI Agents","Tool Calling","FastAPI","Leaflet","Render"],
   links=[("Live demo","https://footfall-zz9v.onrender.com","live"),("Code",GH+"footfall","code"),
          ("Demo video","https://youtu.be/Smw3hQl3CB0","doc")]),

 dict(slug="sqlnoir", cat="agents", title="SQL Noir", sub="A Detective Game That Teaches SQL on Live Data",
   meta="2026 · Open Agent Hackathon (Zetaris), Track 02 · submitted Oct 27",
   desc="You get a case, write SQL to crack it, and the game runs your query on real data in Zetaris. <strong>No verdict comes from the model.</strong> The grader compares your rows with the answer&rsquo;s by value and shows the rows you shouldn&rsquo;t have and the rows you&rsquo;re missing. Nemo, a detective on NVIDIA Nemotron, turns that evidence into a hint, and a critic blocks any hint that leaks the answer. Meterless H-MEM remembers what you got stuck on. A validator checks every case on Zetaris before it&rsquo;s posed, and on real data it refused two of my own.",
   stats=[("50","tests"),("13 / 13","H-MEM conformance"),("6","checks before a case is posed"),("0","verdicts from the model")],
   tags=["Zetaris","NVIDIA Nemotron","Meterless H-MEM","Agent loops","TypeScript","SQL","Cursor"],
   links=[("Code",GH+"sql-noir","code"),("Demo video","https://youtu.be/oX4KvIMfIbE","doc")]),

 dict(slug="proofoffix", wide=True, cat="agents", title="Proof of Fix", sub="Issues Close on Production Evidence, Not on a Merge",
   meta="2026 · GitLab AI Hackathon (Duo Agent Platform) · submitted Oct 27",
   desc="<strong>&ldquo;Closed&rdquo; usually means a merge request merged. Nobody checks that users stopped hitting the bug</strong>, and with agents writing and merging fixes that gap gets wider. In Proof of Fix, a GitLab Duo flow reads production logs when a bug is filed and writes a proof contract into the issue: the failure that must stop and the log event the fix must start. After the deploy, the pipeline judges the build that shipped on its own logs. The issue closes with a receipt, or stays open with the lines that show the bug is still there, and a second Duo flow works out what the fix missed.<br><br>The real run on GitLab: triage found the rounding bug on two routes. The first fix covered one, and it passed the tests, the contract gate and Duo Code Review. Production disagreed: failures fell from 32% to 9% of requests, so the issue stayed open. The Duo Developer flow wrote the second fix from that evidence, and after its deploy production showed 0 failures on 875 requests. The issue closed itself.<br><br>The pipeline covers all nine DevSecOps stages, with SAST, secret and container scanning, and a rollback that fires only if the new build is worse than the old one.",
   stats=[("32% → 9%","not proven, issue stayed open"),("0 / 875","failures after the real fix"),("9","DevSecOps stages"),("38","tests")],
   tags=["GitLab Duo Agent Platform","GitLab CI/CD","OpenTelemetry","GitLab Observability","Python","FastAPI","Render"],
   links=[("The real run","https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase/-/work_items/2","live"),
          ("GitLab project","https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase","code"),
          ("Demo video","https://youtu.be/tec52HoWT5A","doc")]),

 dict(slug="klarbrief", cat="genai", title="Klarbrief", sub="Official Swiss Letters, Explained Offline",
   meta="2026 · Hack Apertus, Track 2B · submitted Oct 14",
   desc="27% of Swiss residents don&rsquo;t hold a Swiss passport, and official letters arrive in German, French or Italian. Klarbrief has Apertus 1.5 8B, Switzerland&rsquo;s open LLM, explain a letter in the reader&rsquo;s language. Every point must quote the letter, and plain code checks the quote and its date or CHF amount before the point is shown. It runs offline in llama.cpp on a 4-core CPU, so a letter never leaves the machine. On 48 explanations the model offered 7 wrong deadline dates and the check stopped 6. No wrong CHF amount reached the reader.",
   stats=[("6 of 7","wrong dates stopped"),("0","wrong CHF amounts shown"),("48 / 48","in the reader's language"),("4-core","CPU, no internet")],
   tags=["Apertus 1.5","llama.cpp","Air-gapped Docker","LLM output checks","Python"],
   links=[("Code",GH+"klarbrief","code")]),

 dict(slug="aside", wide=True, cat="genai", title="Aside", sub="A Fire TV Companion That Never Spoils the Film",
   meta="2026 · Amazon Build, Ship, Shape Hackathon, Fire TV track · submitted Oct 22",
   desc="Press Up on the remote and ask what just happened, who that is, or what you missed while you were out of the room, or ask out loud from your phone. Aside knows the film only up to the second you&rsquo;ve watched. It also writes audio description for the gaps between dialogue, because most titles have none.<br><br>Gemini watches each film once and writes a timeline where every fact carries the second it appears. Each answer is built only from the facts you have seen, and a second model checks it against the rest of the film. <strong>On 16 questions written to pry out the future, the whole film in the prompt with an instruction not to spoil leaked 6. Aside leaked none</strong>, and it stayed helpful on all 8 questions about what you had already seen.<br><br>It runs on a real Fire TV Stick 4K Select (Vega OS), rebuilt overnight from Amazon&rsquo;s Vega WebView template when the stick turned out not to run Android APKs. Eight developer-tool problems from that night went into a friction log.",
   stats=[("6 → 0","of 16 spoiler probes leaked"),("8 / 8","helpful on past questions"),("Vega OS","on a real Fire TV Stick"),("₹0","to host, all free tiers")],
   tags=["Fire TV / Vega OS","Gemini video understanding","Groq","Spoiler evaluation","Audio description","FastAPI","Kotlin"],
   links=[("Live TV app","https://aside-tv.onrender.com/tv/","live"),("Code",GH+"aside-tv","code"),
          ("Demo video","https://youtu.be/8459XKUURhs","doc"),
          ("Friction log","https://github.com/JannetEkka/aside-tv/blob/main/docs/FRICTION_LOG.md","doc")]),

 dict(slug="ghostledger", cat="agents", title="Ghost Ledger", sub="A Deletion-Audit Agent, Built in 24 Hours",
   meta="2026 · HackerRank Orchestrate · 75.9 / 100",
   desc="A shop&rsquo;s dashboards said every GDPR deletion was &ldquo;Complete&rdquo;. For each of 518 requests the agent decides whether deletion was really asked for, finds every copy of the person&rsquo;s data across 94 evidence files (SQL snapshots, six log formats, PDFs, screenshots), rebuilds each record&rsquo;s state at the audit time and writes a cited remediation plan. Models only read intent and transcribe screenshots; the verdict is deterministic, and doubt resolves toward not deleting. 100% status accuracy and 99.2% step F1 on the 32 public samples. The chat transcript scored 3/10 because I had tidied it, a lesson kept.",
   stats=[("100%","status accuracy, 32 samples"),("99.2%","step F1"),("94","evidence files"),("$0.00004","model cost per request")],
   tags=["Agentic auditing","GDPR","SQLite","Gemini","Groq","Prompt-injection defence","Python"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/hackathons/hackerrank-orchestrate-oct26","code")]),

 dict(slug="afterburn", wide=True, cat="cv", title="Afterburn", sub="Farm-Fire Verification from Satellite Burn Scars",
   meta="2026 · IEEE ClimateChain Global Hackathon · submitted Oct 21",
   desc="<strong>Punjab&rsquo;s farm-fire count fell 90% since 2021. Burnt area fell a third.</strong> Farmers now light stubble after the 1:30 pm satellite pass, so the official count misses most fires. Afterburn reads the burn scar in Sentinel-2 imagery instead, which stays for days whatever hour the fire was lit.<br><br>On this season&rsquo;s data for 80 × 52 km of Amritsar, Tarn Taran and Kapurthala it mapped 23,963 ha of scars. Between the Oct 13 and Oct 18 passes, only 2.9% of the scars it found had a VIIRS fire detection nearby. Inside VIIRS fire footprints it finds 3.4× more burnt land than on random harvested land. A positive-unlabeled model did worse, so a dozen published thresholds make the verdicts.<br><br>The verdicts settle a pay-for-not-burning pact on Monad testnet, built on a J-PAL trial in 171 Punjab villages: a quarter paid at sign-up, the rest after a clean season, and a village bonus only if every enrolled field stays clean. Each verdict goes on-chain with the hash of its evidence, and a recheck script rebuilds it from public scenes. All 24 demo verdicts match.",
   stats=[("23,963 ha","burn scars mapped this season"),("3.4×","lift against VIIRS fire footprints"),("24 / 24","verdicts recheck from public data"),("98","transactions on Monad testnet")],
   tags=["Sentinel-2","Remote Sensing","NASA FIRMS","rasterio","Positive-Unlabeled Learning","Solidity","Monad testnet","Hardhat","Leaflet","Gemini API"],
   links=[("Live demo","https://jannetekka.github.io/afterburn","live"),("Code",GH+"afterburn","code"),
          ("Demo video","https://youtu.be/XqyN4N3_2TY","doc")]),

 dict(slug="smtreceipts", grants=True, cat="agents", title="SMT Receipts", sub="An AI Bot&rsquo;s Calls, Sealed On-Chain and Graded Later",
   meta="2026 · Monad Metropolis, Onchain Finance &amp; Trading · submitted Oct 14",
   desc="Signal sellers delete the calls that lost. SMT Receipts writes every hourly call from my trading agent to a contract on Monad testnet before the market moves, WAITs included, and grades each one against RedStone-signed prices net of a 12 bp fee it can&rsquo;t change. The contract has no owner and no upgrade path, so nobody can edit a receipt, including me. A keeper has run it unattended since Oct 13. The record isn&rsquo;t flattering: by Nov 1, 26 of 75 graded calls were hits after fees.",
   stats=[("227","batches sealed by Nov 1"),("1,728","WAITs on the record too"),("26 / 75","graded calls that were hits"),("18","contract tests")],
   tags=["Solidity","Monad testnet","RedStone oracles","Envio HyperIndex","GitHub Actions"],
   links=[("Live","https://jannetekka.github.io/monad-hack/","live"),("Code",GH+"monad-hack","code")]),

 dict(slug="recourse", wide=True, cat="genai", title="Recourse", sub="Receipts for Welfare Algorithms",
   meta="2026 · Web3 for Social Good (SMU × GSR Foundation × University of Málaga) · submitted Oct 21",
   desc="<strong>When an algorithm cuts a family off its rations, which record did it?</strong> In Telangana, a matching system removes families from subsidised food when it finds a &ldquo;match&rdquo; across government databases. Al Jazeera reported in 2024 that it tagged Bismillah Bee&rsquo;s late husband, a rickshaw puller, as a car owner, and her family lost its rations. Nobody could tell her which record did it.<br><br>Recourse makes the agency publish the hash of its matching rules on Monad testnet before it uses them. The contract refuses any batch decided under rules that weren&rsquo;t public in an earlier block. Every decision gets a receipt naming the records that decided it, with their match scores and the threshold. A record is listed only if removing it changes the outcome. One Merkle root per batch goes on-chain, so nothing personal does, and anyone can check a receipt against it in the browser.<br><br>Gemini explains each receipt in Telugu, Hindi or English and drafts the appeal letter. A guard checks every number and record ID in the text against the receipt and throws out any draft that invents one. A legal-aid worker files the appeal on-chain for the family, and the agency&rsquo;s answer is sealed too. An appeal left unanswered shows as overdue.<br><br>The demo agency and its 1,005 households are synthetic, so the truth is known: the second rule version refused 209 families, 127 of them wrongly. The transactions are real. Recourse can&rsquo;t prove the agency ran its rules on every household, only which rules it said it ran and what it decided.",
   stats=[("2,010","decisions sealed on Monad testnet"),("127","families wrongly refused by rules v2"),("16","appeals on the record, 11 reversed"),("3","languages, every number checked")],
   tags=["Solidity","Foundry","Monad testnet","Merkle proofs","Python","Gemini API","LLM output guard","Vanilla JS","GitHub Pages"],
   links=[("Live demo","https://jannetekka.github.io/recourse/","live"),("Code",GH+"recourse","code"),
          ("Demo video","https://youtu.be/KDfbYbLN7Cw","doc"),
          ("Contract","https://testnet.monadvision.com/address/0x0113802632a88f7f5ebd7603a8eea5f31e5c30ce","doc")]),

 dict(slug="clockin", grants=True, cat="agents", title="SMT World: Clock In", sub="A Daily Call Against the AI, on Solana",
   meta="2026 · Solana Mobile Hackathon · submitted Oct 12",
   desc="A native Android app. Once a day you call a coin up or down for four hours. Your call and my trading agent&rsquo;s land on Solana devnet in one memo signed through Mobile Wallet Adapter, and both are graded on real prices four hours later, so neither can be written after the market moves. The leaderboard needs no server and trusts no price a memo claims. Tested on my own phone across four releases, which found two real bugs: a wallet refusing a saved session, and a notification that never fired because the phone deferred the background job.",
   stats=[("4","releases tested on a phone"),("40","unit tests"),("0","servers"),("devnet","no real money")],
   tags=["Kotlin","Jetpack Compose","Mobile Wallet Adapter","Solana devnet","WorkManager"],
   links=[("Code",GH+"smt-solana-hack","code")]),

 dict(slug="lore", wide=True, cat="agents", title="Lore", sub="Who Knows What in an Open-Source Project",
   meta="2026 · Graph Hacks (FalkorDB × WeMakeDevs) · submitted Oct 18",
   desc="<strong>Who knows this part of the code, and who should look at this issue?</strong> Lore reads an open-source project&rsquo;s public GitHub history into a FalkorDB graph: who wrote and reviewed which PRs, which files each one changed, which issues it fixed. A Gemini agent answers from that graph with twelve Cypher tools, and every answer cites the PRs behind it.<br><br>While it works, an <em>Under the hood</em> panel shows each tool it picks and each Cypher query it runs, then draws the evidence as a graph. Triage finds related issues and an active reviewer for a new issue and drafts a reply without posting it. Teams runs label propagation over who reviews whom. Signed in with GitHub, each person gets a memory graph of their own, and anyone can add a public repo.<br><br>Backtested on 300 real FalkorDB PRs: Lore had a real reviewer in its top three 90% of the time, against 88% for &ldquo;the most frequent reviewer&rdquo;. On the single top pick that baseline wins overall, and the write-up says so.<br><br>A port to the Anna app store rebuilds the same graph and scores in plain JavaScript, so it runs on the user&rsquo;s own model quota with no server of mine (in App Review).<br><br><em>The live demo runs on free tiers, so the first load can take up to a minute.</em>",
   stats=[("1,357","FalkorDB PRs in the graph"),("90%","real reviewer in the top 3"),("12","Cypher tools for the agent"),("₹0","to host, all free tiers")],
   tags=["FalkorDB","Cypher","Graph Algorithms","AI Agents","Gemini API","MCP","FastAPI","GitHub Actions","Docker on Render","FalkorDB Cloud"],
   links=[("Live demo","https://lore-gh5y.onrender.com/","live"),("Code",GH+"lore","code"),
          ("Demo video","https://youtu.be/V-Ifwi_jxhg","doc"),
          ("Blog post","https://medium.com/@jannetaekka/i-built-a-company-brain-for-open-source-projects-on-falkordb-47f519f9ce08","doc"),
          ("Anna port",GH+"anna-lore","code")]),

 dict(slug="rsna", cat="cv", title="RSNA Knee MRI", sub="Twelve Abnormalities, 1.3% Hand Labels",
   meta="2026 · Kaggle RSNA Knee Abnormality Detection · not placed",
   desc="Only 58 of 4,407 training studies carried hand labels; the rest had a radiology report in a dozen languages. Before training on the public LLM-extracted labels I scored them against those 58 (macro AUC 0.870 to 0.904) and trained on a blend. My own model, with no outside data, reached 0.918 public AUC against a top score of 0.966. Most of the work was making it run inside Kaggle&rsquo;s free GPU and memory limits.",
   stats=[("0.918","public AUC, no outside data"),("58","hand labels of 4,407"),("0.894","blend labels vs hand labels"),("₹0","Kaggle free GPUs")],
   tags=["Medical imaging","PyTorch","timm","Label quality","Kaggle"],
   links=[("Competition","https://www.kaggle.com/competitions/rsna-knee-abnormality-detection","doc")]),

 dict(slug="wiretrap", wide=True, cat="agents", title="Wiretrap", sub="Adversarial Security Testing for AI Agents",
   meta="2026 · Google Cloud Gen AI Academy APAC — Cohort 3",
   desc="<strong>&ldquo;We don&rsquo;t grade what your agent says. We audit what it does.&rdquo;</strong> Most LLM security tools read the agent&rsquo;s reply and grade the text. This one reads the tool-call log.<br><br>Every tool the agent declares gets cloned as a dead copy with the same name and JSON Schema. The copy records the call and returns fake data, so nothing real fires. Attacks run in separate Gemini conversations and a judge model reads the log. The payloads are written to look like ordinary work, no shouting and no &ldquo;ignore all previous instructions&rdquo;, because current models refuse those easily.<br><br>It caught a Google codelab agent saying <em>&ldquo;I don&rsquo;t have access or authorization to modify configuration files&rdquo;</em> after it had already run <code>ls -la</code> through its shell tool. Text scanners pass that. Wiretrap calls it <strong>&ldquo;Said No, Did Yes&rdquo;</strong> and shows the arguments.<br><br>A run with nothing classified reports <code>INCONCLUSIVE</code>, never <code>HARDENED</code>. Attacks against tools the agent doesn&rsquo;t have are dropped from the score. Approved fixes get re-run against the attacks that broke it, and the report says when one didn&rsquo;t hold.<br><br><em>The live demo runs on free tiers, so the first load can take up to a minute while it wakes up.</em>",
   stats=[("8","attack categories"),("10K","lines of TypeScript"),("₹0","to host, all free tiers"),("4","model fallback ladder")],
   tags=["Adversarial Testing","Agent Security","Gemini API","React + TypeScript","Express","Firestore","Firebase Auth","Docker on Render","Google AI Studio"],
   links=[("Live demo","https://wiretrap.onrender.com/","live"),("Code",GH+"wiretrap","code")]),

 dict(slug="versecanvas", grants=True, cat="genai", title="VerseCanvas", sub="AI Poetry-to-Art Generator", meta="2025 · Personal project",
   desc="Turns a poem into original artwork through a multi-stage pipeline: semantic analysis with Gemini 2.0 &rarr; automated prompt engineering &rarr; image synthesis with Imagen 3.0 on Vertex AI &rarr; hybrid editing and text overlay. Six languages, six art styles, tunable mood intensity.",
   tags=["Gemini 2.0","Imagen 3.0","Vertex AI","Streamlit"],
   links=[("Live demo","https://versecanvas.streamlit.app/","live"),("Code",GH+"versecanvas","code")]),

 dict(slug="smartdesk", grants=False, wide=True, cat="agents", title="SmartDesk", sub="Multi-Agent Assistant with Measured RAG", meta="2026 · Gen AI Academy APAC — Cohort 1 Hackathon · top 101 of 1,500+",
   desc="A root ADK orchestrator routing to specialised sub-agents — InboxAgent, PlannerAgent and a DataAgent doing retrieval over a pgvector knowledge base — with a SequentialAgent synthesising the reply. Gmail and Calendar are reached through <em>MCP servers I wrote myself</em> against the protocol SDK over stdio, not off-the-shelf toolsets. Containerised on Cloud Run.<br><br>The retrieval is <em>evaluated, not assumed</em>: 40 labelled questions over 120 notes, recall@k and MRR@k, significance by paired bootstrap at 10,000 resamples. That harness is what stopped a bad decision — a cross-encoder reranker looked like a clear win on the development embedder (MRR@10 +0.094, p=0.04), then collapsed on the production embedder to +0.028 with a CI spanning zero. Shipping it would have added <em>190&nbsp;MB of PyTorch and taken search from 29&nbsp;ms to 2,382&nbsp;ms</em>, in an image deliberately cut from 1.8&nbsp;GB to 340&nbsp;MB, for a gain indistinguishable from noise. The baseline ships instead, now on evidence rather than caution.",
   stats=[("0.963","recall@5"),("40","labelled questions"),("82×","latency the reranker cost"),("54","tests")],
   tags=["Google ADK","MCP (servers written from scratch)","pgvector","RAG evaluation","Paired bootstrap","Cross-encoder / RRF / BM25","Gemini 2.5 Flash","Cloud Run"],
   links=[("Code",GH+"smartdesk","code"),
          ("Eval results","https://github.com/JannetEkka/smartdesk/blob/main/evals/RESULTS.md","doc")]),

 dict(slug="locintel", cat="agents", title="Location Intelligence Agent", sub="MCP over BigQuery + Google Maps", meta="2026 · Google Cloud Gen AI Academy APAC",
   desc="An ADK agent wired to two remote MCP servers — BigQuery for demographic, pricing and sales data, Google Maps for location analysis. Scores zip codes by demographics and foot traffic, flags underperforming stores, projects next-month revenue and measures competitor density.",
   tags=["MCP Servers","BigQuery","Google Maps API","ADK"],
   links=[("Code",GH+"bakery-growth-agent","code")]),

 dict(slug="autokorrekt", cat="genai", wide=True, title="AutoKorrekt", sub="AI Answer-Evaluation Platform for Teachers", meta="May 2023 – Jan 2024 · Lead Frontend Developer · EdTech startup MVP",
   desc="An evaluation platform that takes a teacher from sign-up to graded scripts: create a class, upload a student roster and question paper, bulk-upload scanned answer sheets, then track each student through OCR, AI evaluation and validation. I led the frontend and designed the ML data flow across S3, RDS and SageMaker &mdash; interactive PDF processing with coordinate-based text extraction over AWS Textract, a bilingual EN/DE feedback interface on Amazon Comprehend, and a per-student status pipeline that scaled to 1,000+ concurrent submissions.",
   tags=["React","Next.js","TypeScript","AWS Textract","Amazon Comprehend","SageMaker","Django"],
   shots=[("assets/autokorrekt/Index_page_signup.png","Teacher sign-up"),
          ("assets/autokorrekt/Index_pg_signin.png","Sign in"),
          ("assets/autokorrekt/add_Test.png","Create a class — student roster (CSV) + question-paper upload"),
          ("assets/autokorrekt/students.png","Per-student evaluation pipeline &amp; bulk answer-sheet upload")],
   links=[]),

 dict(slug="smtracker", cat="agents", title="Smart Money Tracker", sub="Multi-Agent Blockchain Analytics", meta="2024 · Winner — Best DeFi Application",
   award="OpenServ × Hack2skill",
   desc="Multi-agent whale tracking across Ethereum, BNB Smart Chain and Polygon using the OpenServ SDK, with Alchemy webhooks driving sub-second transaction monitoring. Confidence-scored detection of accumulation, distribution and coordinated movements, with automated exchange-wallet exclusion.",
   tags=["OpenServ SDK","Alchemy","Moralis","Cloud Run","pgvector"],
   links=[]),

 dict(slug="smtchains", grants=True, cat="agents", title="SMT Chain Adapters", sub="Mantle &amp; BNB hackathon builds", meta="2026 · Hackathon adapters",
   desc="Thin per-chain adapters that import the SMT brain and expose it to a specific ecosystem — keeping one shared decision engine behind platform-specific front ends rather than forking the strategy code.",
   tags=["Mantle","BNB Chain","Python"],
   links=[("Live","https://jannetekka.github.io/smt-mantle/","live"),("Mantle",GH+"smt-mantle","code"),("BNB",GH+"smt-bnb","code")]),

 dict(slug="asha", cat="genai", title="Asha Chatbot", sub="JobsForHer Foundation", meta="2025 · Hackathon project",
   desc="A context-aware chatbot surfacing job listings, community events and mentorship programmes, and handling FAQs — built to support women returning to and advancing in the workforce.",
   tags=["Conversational AI","NLP","Python"], links=[("Code",GH+"asha-chatbot","code")]),

 dict(slug="medtest", cat="genai", title="MedTestAI", sub="Test Cases for Healthcare Software", meta="Sep – Nov 2025 · Gen AI Exchange Hackathon 2025",
   desc="Generates structured test cases for regulated healthcare software from a requirements document, with Gemini 2.0 Flash. Each case carries steps, expected results, priority, risk and the compliance control it covers, across 8 frameworks (HIPAA, FDA 21 CFR Part 11, GDPR, ISO 13485 and others), with CSV, JSON and Excel export. Node on Cloud Run with rate limits; CI deploys through Workload Identity Federation, so no long-lived key sits in GitHub. Generated-test quality was not measured.",
   tags=["Gemini","Test generation","Healthcare compliance","Node.js","Cloud Run","Workload Identity Federation"], links=[("Code",GH+"MedTestAI","code")]),

 dict(slug="webqna", cat="genai", title="WebContentQnA", sub="Ask questions about any page", meta="2025 · Personal project",
   desc="Paste a set of URLs and ask questions about their contents; the app retrieves and answers from page text using a DistilBERT question-answering model.",
   tags=["DistilBERT","Question Answering","Transformers"], links=[("Code",GH+"WebContentQnA","code")]),

 dict(slug="capstone", cat="cv", title="Automotive Surveillance System", sub="Capstone — Computer Vision", meta="Dec 2024 – Jan 2025 · Great Learning",
   desc="Car make/model/year classification from the 196-class, 16,185-image Stanford Cars set. Compute limits meant training on a 16-class subset, where a fine-tuned ResNet50 reached 69.2% validation accuracy; Fast R-CNN with a MobileNetV2 backbone reached 58% on detection. The main finding was overfitting: about 29 images per class is too few.",
   tags=["ResNet50","Fast R-CNN","TensorFlow","OpenCV"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Automotive_Surveillance_System_Capstone","code")]),

 dict(slug="botanical", cat="cv", title="MultiModel Botanical Classification", sub="Plant species recognition", meta="Jun – Jul 2024 · UT Austin McCombs",
   desc="83.79% accuracy with a CNN for automated plant-species classification across 4,750+ seedling images, benchmarked against Random Forest and SVM baselines.",
   tags=["CNN","Transfer Learning","Computer Vision"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/MultiModel_Botanical_Classification_CV","code")]),

 dict(slug="signal", cat="cv", title="Signal &amp; SVHN Classification", sub="Neural networks, two domains", meta="Aug – Sep 2024 · UT Austin McCombs",
   desc="Dense neural networks with batch normalisation and dropout on two problems: SVHN street-number digits, 87.1% test accuracy on 18,000 images, and signal-quality prediction from 11 parameters, about 65% at best, a harder ordinal target with few examples at the extremes.",
   tags=["Deep Learning","Keras","Regularisation"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Signal_Classification_Digit_Recognition_NNDL","code")]),

 dict(slug="churn", cat="ml", title="Customer Churn Prediction", sub="Telecom retention", meta="Oct – Nov 2024 · UT Austin McCombs",
   desc="Decision Tree, Random Forest, AdaBoost and Gradient Boosting, each tuned with grid search, to flag telecom customers likely to cancel. Random Forest won at 81.48% test accuracy. For a retention budget, recall on churners and lift over random targeting are the numbers that matter, and the write-up says so.",
   tags=["Ensemble Methods","scikit-learn","Business Strategy"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Customer_Churn_Prediction_ET","code")]),

 dict(slug="semi", cat="ml", title="Semiconductor Yield Prediction", sub="591 sensor signals", meta="Sep – Oct 2024 · UT Austin McCombs",
   desc="Pass/fail yield prediction from manufacturing sensor data, using feature selection and SMOTE to cut 591 signals down to the ones that actually carry information about defects.",
   tags=["Feature Selection","SMOTE","Quality Control"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Semiconductor_Manufacturing_Prediction_FMT","code")]),

 dict(slug="adview", cat="ml", title="YouTube AdView Analytics", sub="Ad-revenue prediction", meta="Jul – Aug 2024 · Internship Studio",
   desc="Random Forest regression predicting advertisement views from engagement metrics across 15,000+ videos, packaged for integration with business dashboards.",
   tags=["Random Forest","pandas","Predictive Analytics"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/YouTube_AdView_Analytics_ML","code")]),

 dict(slug="nbfc", cat="ml", title="NBFC Loan Default Prediction", sub="Credit risk", meta="Feb 2025 · Great Learning Hackathon",
   desc="A classification model predicting whether a client will default on loan repayment, built against a non-banking financial company dataset under hackathon time constraints.",
   tags=["Classification","Risk Modelling"], links=[("Code",GH+"NBFC-Loan-Default","code")]),

 dict(slug="usl", cat="ml", title="Automobile Analysis &amp; Classification", sub="K-Means + PCA-enhanced SVM", meta="Apr – May 2024 · UT Austin McCombs",
   desc="K-Means segmentation of 398 cars on 8 attributes (MPG, displacement, horsepower, weight and more; silhouette 0.59 at k = 3), and an SVM on 846 vehicle silhouettes with 18 geometric features, with and without PCA (best test accuracy 0.96).",
   tags=["K-Means","PCA","SVM"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Automobile_Analysis_Classification_USL","code")]),

 dict(slug="sentiment", cat="ml", title="Stock Market Sentiment Analysis", sub="Financial news NLP", meta="Nov – Dec 2024 · UT Austin McCombs",
   desc="An ensemble sentiment classifier over financial news using Word2Vec, GloVe and SBERT embeddings, with weekly market summaries generated by a Mistral-7B LLM.",
   tags=["NLP","SBERT","Mistral-7B","Transformers"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Stock_Market_Sentiment_Analysis_NLP","code")]),

 dict(slug="newwheels", cat="analytics", title="New-Wheels Performance Analytics", sub="SQL business intelligence", meta="Jul – Aug 2024 · UT Austin McCombs",
   desc="Customer behaviour and sales analysis for a vehicle-resale business covering 994 customers and $1.25B revenue, with a KPI tracking system identifying key markets.",
   tags=["SQL","Business Intelligence","KPI Design"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/New_Wheels_Performance_Analytics_SQL","code")]),

 dict(slug="bizanalytics", cat="analytics", title="Business Analytics Portfolio", sub="Pricing + HR attrition", meta="May – Jun 2024 · UT Austin McCombs",
   desc="Two supervised-learning studies: used-car price regression for Cars4U, with feature engineering taking R² from 0.65 to 0.87, and employee-attrition classification on a healthcare HR dataset, 84% test accuracy at baseline and 97% tuned.",
   tags=["Regression","HR Analytics","scikit-learn"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Business_Analytics_Portfolio_SL","code")]),

 dict(slug="ecom", cat="analytics", title="E-commerce Price Analysis", sub="Scraper to dashboard data", meta="2024 – 2025 · Personal project",
   desc="A product-listing scraper with rate limiting, validation and resumable checkpoints, a price analyser, and CSV/SQL exports for a Tableau dashboard, designed first on generated sample data.",
   tags=["Web scraping","Data pipeline","SQL","Tableau","Python"], links=[("Code",GH+"ecommerce-analysis","code")]),

 dict(slug="stats", cat="analytics", title="Applied Statistics &amp; Hypothesis Testing", sub="Statistical foundations", meta="May – Jun 2024 · UT Austin McCombs",
   desc="Binomial models for quality control at a given 5% defect rate, Poisson models for weekly car sales, and hypothesis tests on purchase and sports-team data.",
   tags=["Hypothesis Testing","SciPy","Probability"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Applied_Statistics_Project","code")]),

 dict(slug="yatra", cat="automation", title="Yatra Test Automation Framework", sub="Hybrid Selenium framework", meta="2024 · Personal project",
   desc="A hybrid data-driven Selenium framework with Page Object Model structure, external test data, cross-browser runs on Edge/Chrome/Firefox, HTML reporting and failure screenshots — wired into Jenkins.",
   tags=["Selenium","PyTest","POM","Jenkins"], links=[("Code",GH+"python-automation","code")]),

]

CATS = [("all","All work"),("agents","AI Agents"),("genai","Generative AI"),
        ("cv","Computer Vision"),("ml","Machine Learning"),("analytics","Analytics"),("automation","Automation")]
