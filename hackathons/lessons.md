# Lessons from our results

Check every new entry against this list before choosing the idea and again before writing code. It comes from three results read on 2026-11-08:

- **JigJoy NTP Novi Sad:** the five winners in the gallery; Spona did not place.
- **Qloo Agentic:** the three winners on Devpost; Footfall did not place.
- **HackerRank Orchestrate:** the judges' written feedback on Ghost Ledger, in [hackerrank-orchestrate-oct26/feedback.md](hackerrank-orchestrate-oct26/feedback.md).

Points marked *(our reading)* are inferred from what the winners did, since neither JigJoy nor Qloo published scores. The HackerRank points are the judges' own, paraphrased.

## Choosing the idea

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
