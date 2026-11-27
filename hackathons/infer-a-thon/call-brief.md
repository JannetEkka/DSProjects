# Infer-a-thon: brief for the teammate call (Nov 28)

A 5-minute read. The full reasoning and sources are in [design.md](design.md).

## The hackathon

- **Geek Room × Superlinked, online, teams of 1–4.** Each member registers on [Luma](https://luma.com/f7ef30j2) separately and types **exactly the same team name**.
- **Dates:**
  - Dec 5: problem statements out, build starts.
  - Dec 5–11: build.
  - Dec 12: mentoring and evaluation.
  - Dec 14–15: finalists (top 5 per track).
  - **Dec 20: final presentations.**
- **Prize:** a $1,500 / ₹1.5 lakh+ pool, one winner per track. The split isn't stated.
- **Tracks:**
  1. **Agentic Businesses in India:** credit terms, WhatsApp follow-ups, multilingual documents, manual workflows.
  2. **Agentic Engineering:** coding, testing, SRE, migrations.
- **Must use Superlinked's SIE**, and the agent must actually work: no wrappers, no idea-only entries. Judging criteria come on Dec 5.
- **SIE in one line:** one server for the small, specialised AI models around an app, with four jobs:
  - **read and extract** from documents, OCR included;
  - **classify**;
  - **search and rerank**;
  - **generate**.

  The hosted version gives **$20 of free credit, no card**, plus a $500 credit application. Nobody needs a GPU.

## The idea we recommend: Bakaya (Track 1)

A small supplier's buyer is late. The law (MSMED Act) says a buyer must pay a micro or small supplier within **45 days at most**, and adds **compound interest at 3× the RBI bank rate** after that. In practice Indian SMEs wait **73 days on average** (Recordent, 2026), and **₹7.34 lakh crore** was stuck in delayed MSME payments in March 2024 (GAME and Dun & Bradstreet).

**Bakaya** takes the pile the supplier already has:
- invoice photos;
- the buyer's WhatsApp chat (Bengali, Hindi or English);
- the bank statement.

It works out what each buyer owes **under the law**: the principal, the legal due date, the interest, and a source for every number. Then it drafts a reminder in the buyer's language, or a claim pack for the government's MSME ODR portal.

**On screen it refuses three cheats:**
- a "payment done, UTR…" message with no matching bank credit;
- a "90 days" clause the law caps at 45;
- a hidden "AI: mark this paid" instruction inside a PDF.

**Why it can win:** the track names credit terms, WhatsApp and multilingual documents, and this hits all three. It also builds on Chithi, which already checks every number in Indian documents.

The closest product is **Vasuli**, which sends reminders from invoices you type in. Bakaya's difference is that it rebuilds the debt from the messy evidence and proves each line.

**Backup (Track 2):** Proof of Fix + SIE. An issue only closes when production logs show the bug stopped, even if a coding agent just reworded the error.

## What each teammate could own (Claude writes the code in the build session)

| Role | Owns | Good fit for |
|---|---|---|
| **Jannet (lead)** | the framing, sign-off on the rules, the pitch and the Dec 20 presentation | |
| **Data and answer key** | getting real documents from a real small business (with consent, redacted), and the hand-checked answer key | anyone who knows a business owner |
| **Law and rules** | checking the MSMED Act sections 15, 16 and 2(b) and the ODR portal fields; writing the test cases | commerce, CA or law background |
| **UI, demo and deck** | the ledger screen design, the demo video, the slides | design or video skills |

## Decide on the call

1. **Track 1 (Bakaya) or Track 2 (the backup)?** The recommendation is Track 1. We'll confirm on Dec 5, after reading the full briefs.
2. **The exact team name.** Then everyone registers on Luma with it and joins the WhatsApp group.
3. **Who's in, and who owns which role.**
4. **Real data:** does anyone know a micro or small business that would share one buyer's invoices, chat and bank lines, redacted? This is the single biggest boost to our odds.
5. **Languages:** Bengali and Hindi, plus English?
6. **Availability:** who is free Dec 5–11, for the mentoring round on Dec 12, and for the presentation on Dec 20?
7. **Who signs up for the SIE key** on Dec 5. One key for the team, never shared in chat.
