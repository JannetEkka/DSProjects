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
6. **Keep the AI chat transcript raw and append-only** from the first prompt: real prompts, real responses, nothing cut or reordered. A curated log scored 3/10.

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

## Monad Metropolis winners (read 2026-11-12)

Our entry, SMT Receipts ([#26](https://github.com/JannetEkka/DSProjects/issues/26)), did not win a track prize, an honorable mention or a sponsor bounty. Source: Monad's "Meet the Metropolis Winners" article, pasted by Jannet on 11-12. Scale: 885 teams and 1,256 builders from 76 countries, four tracks, $250K+ in prizes. Monad published no scores or judges' comments, so the patterns below are *(our reading)* of what the winners built. Use this list before the next crypto hackathon.

**What kept winning**

- **A new thing to trade, not a new tool for traders.** The grand champion and three more winners made the price of GPU compute into a market: Corpus (compute price feeds, shares in a machine), PIRY and Agate (claims on the H100 rental price), Rackrate (weekly GPU price contracts). Isotherm did the same for city temperature, Trendr for what the internet is talking about.
- **Event and prediction markets were the biggest group:** Eros Markets (perpetuals on event probability), Amplifi (leverage on Polymarket's book), Hunch, Makeo ("TikTok for prediction games"), Terrace Social (group-chat bets on a match), Move Market (markets on each moment of a chess game).
- **Trading as a game or a consumer app:** Rip Trade (each card is a five-second trade), Chart Arena (perps with levels and cards), Copycat (mobile copy trading), Desk (face as the trading key).
- **Cross-border money for ordinary people:** PayZoll, Henad (dollars in, pounds out, with a receipt showing the rate and spread), Kova, Money Moves, Invoices on Monad, Sigilo (private payroll), Kitty (family savings), Pitter (rain cover by the minute).
- **AI agents that handle money, with limits and receipts:** Tab (buy now, pay later for agents), Kanmani (escrow until the agent delivers), Kyvera and MoneySwitch (spending limits), Aria (a receipt for every sponsored line in an AI answer), Assay (which host is really serving the model you pay for).
- **One sentence anyone can repeat.** "Rain cover you switch on for a single shift." "Send dollars that arrive as pounds." "License your face to AI and get paid per image." The winning descriptions name a person and what they get, not the mechanism.

**How they used the sponsors**

- The same three parts recur: a **Kuru order book** to trade on, **Chainlink CRE** to settle from a real-world reading, **Mera passkeys** for sign-in. PIRY, Isotherm, Rackrate, Hunch, Terrace Social and Move Market each use two or three of them.
- **One project, several prizes:** Corpus (grand champion, Kuru, Alchemy), PIRY (track first place, MetaMask), Trendr (Kuru, Mera, Nansen), Likeness, Sigilo, Fork Night, Rizz.town, Terrace Social. Building on the sponsors' own products from day one paid more than once. The sponsor bounties had far fewer entrants than the four tracks.
- Narrow bounty briefs had a clear path: Perpl's two bounties (best use of its API, best analytics or risk tool) paid six projects that were plain dashboards, alerts and a liquidation guard.

**Where SMT Receipts sat**

- It wrote a trading bot's calls on-chain to be graded later: a track record nobody can edit. No winner in Onchain Finance was a record of past behaviour; all three placed projects created a market people can trade today. The nearest winners to our idea were small bounty placings: Xtrading (a caller's real track record beside each post, Nansen honorable mention) and SMIndex (Perpl analytics, third).
- It was a testnet proof with one user, the bot's owner. Several winners say "live on mainnet" or name the users (traders, streamers, freelancers, families).

**For the next crypto hackathon**

1. Pick a lane the list above shows the judges reward: something new to trade, a consumer money app, or agents with money. A verification or audit layer on its own did not place here.
2. Read every sponsor bounty first and design around two or three of them, so one build is eligible for several prizes. This sharpens lesson 1.
3. Write the one-sentence description before the design brief: who it is for and what they get, with no protocol words.
4. If the entry is a tool, enter it in a narrow bounty that asks for tools (as Perpl's did), not in a main track.

