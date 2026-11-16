# Lessons from our results

Check every new entry against this list before choosing the idea and again before writing code. It comes from three results read on 2026-11-08:

- **JigJoy NTP Novi Sad:** the five winners in the gallery; Spona did not place.
- **Qloo Agentic:** the three winners on Devpost; Footfall did not place.
- **HackerRank Orchestrate:** the judges' written feedback on Ghost Ledger, in [hackerrank-orchestrate-oct26/feedback.md](hackerrank-orchestrate-oct26/feedback.md).

Points marked *(our reading)* are inferred from what the winners did, since neither JigJoy nor Qloo published scores. The HackerRank points are the judges' own, paraphrased.

## Choosing the idea

0. **Search the web for the same idea before proposing it (Jannet, 11-09).** For every idea, search GitHub, app stores, Product Hunt, Devpost and the sponsor's own marketplace, and name the closest existing project with a link. If something already does our core thing, drop the idea and brainstorm another; a port of an existing tool to a new platform doesn't count as unique, **except** when the hackathon's goal is to fill its own marketplace: Jannet's call on 11-10 was that Hermes wants plugins it doesn't have, so a Hermes version of Lights Out is fine, as long as the README names the closest projects and says what Lights Out does differently. Checking only the sponsor's catalog is not enough: on 11-09 Lights Out (Hermes) had no match among 1,377 catalog plugins, but the web already had [agent-leftovers](https://github.com/ApahSaroj/agent-leftovers) (leftover cloud resources, cost so far, expiry tags, teardown commands), [cloud-costaware](https://github.com/ozkanpoyrazoglu/cloud-costaware) and [agent-cost-guard](https://github.com/ashishkaloge/agent-cost-guard) (approval with a price before `aws ec2 run-instances`) and [rentctl](https://github.com/Michael-Drake/rentctl) (leased servers that die with the session).
1. **A problem anyone recognises, and a non-obvious use of the sponsor's tech.** All five JigJoy winners came from the open Freestyle track: hardware, traffic, meetings, building codes, political claims. None of the 11 entries on the fixed EINSTEIN brief placed. Qloo's rules asked for a non-obvious idea, and its winners were about elections, booking a whole trip, and a room you walk into, all far from Qloo's everyday use. *(our reading)*
2. **Plan the measured comparison before building.** Run the same task with and without our system and report both numbers:
   - Roomful sends the same favourites to an LLM alone, and 0 of its 8 picks hold up.
   - BringUp: 0 violations with its shared design contract, 16 mismatches without it.
   - The HackerRank judges asked for exactly this: "compare the model-assisted and rules-only paths."

   That number is the impact statement our writing rule asks for.
3. **A result people see in seconds.** A routed board and case, a floor plan marked red then green, a room you can walk into, a map. Not a list of suggestions. *(our reading)*

## Before the first prompt to the coding tool (HackerRank feedback)

4. **Write the architecture down first**: how input interpretation, matching, evidence and decisions connect, and which parts are model judgment and which are fixed rules. The August Orchestrate winner's summary: "let the model describe, let deterministic code decide."
5. **Settle open policy questions explicitly**, and turn ambitions like "a distinctive interface" into acceptance conditions before building them.
6. **Keep the AI chat transcript raw and append-only** from the first prompt: real prompts, real responses, nothing cut or reordered. A curated log scored 3/10. **Only for hackathons that ask for the transcript** (HackerRank Orchestrate grades it). Don't add a build log to other entries or their repos (Jannet, 11-11).

## While building

7. **Agents with different roles that act on each other**: an arbiter between two proposers, a prosecutor and defender before a judge, a devil's advocate, a shared contract that wakes only the agents a change touches. Not one role copied three times over slices of the data. *(our reading, JigJoy)*
8. **Claims depend on evidence coverage.** An unreadable input or an unknown state blocks "complete". Validate every model response against required fields and allowed values. Survive malformed data and damaged caches. Make the README's recovery promises match the code.
9. **A verification pass before any output** that checks the plan against the policy and the evidence it cites.

## Presentation

10. **The home page:** a headline of six words or fewer; the product itself on the first screen; a look that fits the subject (engineering paper for hardware, an editorial serif for meetings), not the default dark-navy-with-glow; one accent colour that means something; motion that shows the agents working. *(our reading, JigJoy and Qloo)*
11. **Interviews and Q&A:** say what is implemented and what is proposed before giving an example, and rehearse one end-to-end walkthrough of the core policy.

## Results read on 2026-11-09 (Jannet)

- **Meta Global AI Developer Hackathon** (Chithi, [#40](https://github.com/JannetEkka/DSProjects/issues/40)): not a finalist, and no bonus prize.
- **Open Agent Hackathon** (sql-noir, [#23](https://github.com/JannetEkka/DSProjects/issues/23)): not a finalist. A winner, TradeFlow, used review agents on a Dhaka Stock Exchange portfolio. Jannet's reading: SMT's agents could have entered the Tinkerer track, and Proof of Fix would have fitted this hackathon.
- **Themes Jannet saw among winners across hackathons:** AR and connecting devices, proof of evidence, health and cancer, satellites and space, fine-tuning, making older tech better, women's safety, music. *(Jannet's reading)*


## Code-scored "vibe coding" hackathons (Catalyst, 2026-11-15)

Hack2skill's PromptWars format scores the repo automatically before any human looks at it. Orbit ([#109](https://github.com/JannetEkka/DSProjects/issues/109)) scored 94.29, then 96.64 on the second and last attempt. That placed it 11th, just outside the top 10 who pitch. These points come from that day.

12. **Read the scoring weights in the first 10 minutes and build to them.** The rubric was code quality (high impact), problem alignment (high), security (medium), efficiency (medium), testing (low) and accessibility (low). It was in the official deck and the submission page, not on the event listing. Ask for the deck or the submission guide at the reveal.
13. **Write high-scoring code from the first commit; it can't be cleaned up at the end.** Code quality stayed at 88 on both attempts, even after a late split of the API into files, because the split kept the same shape: one 167-line `register()` per file, 132 of 173 functions without docstrings, 21 mypy errors, plain dicts instead of named types, and a 673-line frontend file. From the start:
    - one `APIRouter` per file, with each route a top-level function and shared things passed with `Depends`;
    - no function over about 40 lines, and a docstring on each;
    - typed models for stored records;
    - `mypy` and `ruff` clean in CI;
    - the frontend split by screen.
14. **Efficiency is measurable, so fix the measurable faults.** Efficiency went from 80 to 100 after four fixes:
    - one slow hash per sign-in instead of one per member;
    - caching the model's answer for identical input;
    - gzip and cache headers on static files;
    - a counter instead of scanning a table.

    Look for loops that repeat expensive work, repeated model or API calls, and uncompressed assets.
15. **Submit the first attempt early.** Only the last attempt counts, but the first one shows which areas are weak while there is still time to act. Ours came back with efficiency at 80, which is what we then fixed.
16. **One branch means one branch.** Adding Dependabot opened 5 update branches within a minute, and they broke the "repository must have only one branch" rule. The session's git proxy can't delete branches, so Jannet had to. Never add Dependabot or anything else that creates branches to a hackathon repo. Check `git ls-remote --heads origin` before every submission.
17. **Don't trust a 5-minute GitHub Actions schedule on a new repo.** Ours never fired in 5 hours, although a manual run worked. Run scheduled work inside the app as well, and keep it idempotent, so overlapping callers are harmless.
18. **A free host that sleeps can look like a broken link.** The top 10 needed a working deployed link to stay in. Render's free plan sleeps after 15 idle minutes. Keep it awake during judging, and open the link yourself just before any pitch.
19. **Check the build environment rule early.** The page said to build in Google Antigravity. Jannet asked the organisers, and it wasn't mandatory. Ask in the first hour; don't assume.
20. **Automated accessibility checks find real faults.** axe-core found four colour pairs under WCAG AA contrast and content outside the `main` landmark, after the design already looked fine. Run it in light, dark and any night mode before submitting.
