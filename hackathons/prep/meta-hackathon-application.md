# Meta Global AI Developer Hackathon: application answers

Apply by **Oct 25, 23:59 ET (Oct 26, 09:29 IST)**. Places are capped at 20,000 and reviewed as they arrive, so sooner is better. Track: **Indie developer** (can change later). Theme: **Build for Your World**.

Applications are scored equally on (1) how clear and feasible the idea is and how well it fits a theme, and (2) the technical skill shown in the project described. Required tools for the build: Meta Model API (Muse Spark series, Muse Image, SAM 3.1), Meta open-weights models, Muse Code.

## What do you want to build for this hackathon?

> **Chithi**: point your phone at an official letter (an electricity bill, a bank notice, a tax demand, a court summons) and get it explained in Bengali, Hindi or English, with every deadline and amount checked against the letter before you see it.
>
> In India these letters come in formal English or official Hindi, and many people who receive them can't read that register. A wrong date or amount in an AI explanation is worse than no explanation, so nothing reaches the reader unchecked.
>
> SAM 3.1 segments the photo into the parts that matter: amount boxes, dates, tables, stamps. The text in each part is read out, and Muse Spark writes the explanation, quoting the letter for every point. A deterministic check then finds each quote in the letter and compares its date or rupee amount. Points that fail are shown apart as "check this yourself", never as fact.
>
> Last week I built the same check for Swiss official letters on an open model (Klarbrief): across 48 explanations, 0 wrong amounts reached the reader. Chithi adds photos, Indian languages and Meta's models, and I will publish the same measurement for it.

## Tell us about an AI project you recently built that showcases your technical skills

> **Lore** (github.com/JannetEkka/lore, live at lore-gh5y.onrender.com), built in four days for FalkorDB's Graph Hacks in October 2026. It reads an open-source project's GitHub history into a FalkorDB graph: who wrote and reviewed which pull requests, which files they changed, which issues they fixed. A Gemini agent answers questions like "who knows this part of the code?" through 12 Cypher tools and cites the pull requests behind every answer, and a panel shows each tool call and query as it runs.
>
> Techniques: graph modelling in Cypher, tool calling, label propagation to find teams, per-user memory graphs, an MCP server and GitHub sign-in. I backtested it on 300 real PRs: a real reviewer in its top three 90% of the time, against 88% for the most-frequent-reviewer baseline. On the single top pick the baseline wins, and the write-up says so.
>
> Before that: a patent-pending AI trading agent I have run live since 2024, 91,000 lines of Python with 3,000+ tests.

## The multiple-choice questions

| Question | Answer |
|---|---|
| Have you used Meta Model API before? | No |
| How likely are you to build with Meta Model API? | The highest option (you're entering to build with it) |
| Overall opinion of Meta Model API? | "Haven't used it" if offered, otherwise neutral |
| How did you hear about this hackathon? | Online search / Internshala / Cerebral Valley listing: whichever option is closest, else "Other" |
| Marketing emails from Meta | Your choice; nothing says it affects selection |

## If the form has a character limit

Short version of the first answer (about 450 characters):

> Chithi: photograph an official Indian letter (bill, bank or tax notice) and get it explained in Bengali, Hindi or English. SAM 3.1 finds the amounts, dates and tables; Muse Spark explains, quoting the letter; a deterministic check verifies every quoted date and rupee amount before the reader sees it. I built this check for Swiss letters last week: 0 wrong amounts across 48 explanations.
