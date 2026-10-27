# Portfolio source

`../index.html` is **generated**. Don't hand-edit it — edit here and rebuild.

- `data.py` — every project (title, description, tags, links, category).
- `build.py` — page template, CSS and JS; renders the cards from `data.py`.

## Add or change a project

1. Edit the `PROJECTS` list in `data.py`.
   Each link is a `(label, url, kind)` tuple where `kind` is one of
   `live` (filled violet button) · `code` · `doc`.
   A project with no links renders cleanly with none — leave the list empty.
2. Set `cat` to one of the keys in `CATS` so the filter buttons pick it up.
3. Rebuild from the repo root:

   ```bash
   python3 _portfolio_src/build.py index.html
   ```

No dependencies — plain Python 3, standard library only.

## The résumés

Five résumés, all generated from HTML in this folder, the same build-and-verify
approach as the site. Four are role variants for job applications; they share
contact, experience and education, and differ in tagline, summary, skills and
which projects lead.

| PDF | source | for | length |
|---|---|---|---|
| `Jannet_Ekka_Resume.pdf` (repo root) and `resumes/Jannet_Ekka_Resume_Applied_AI.pdf` | `resume.html` | applied AI engineer roles (the site's nav button) | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_FDE.pdf` | `resume_fde.html` | forward deployed engineer roles | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_AI_Trainer.pdf` | `resume_ai_trainer.html` | AI trainer / LLM output-evaluation work | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_Model_Evaluation.pdf` | `resume_model_eval.html` | model evaluation, AI QA, red-teaming | **exactly 2 pages** |
| `Jannet_Ekka_Founder_Resume.pdf` (repo root) | `resume_founder.html` | grants, accelerators, investors | **exactly 1 page** |

The four role variants carry the same `<style>` block. A change to one fact
(a new project, a new number) usually belongs in all four.

Build the four role variants and print their page counts in one go:

```bash
bash _portfolio_src/build_resumes.sh
```

Or one at a time (from this folder):

```bash
chromium --headless --no-pdf-header-footer \
  --print-to-pdf=../Jannet_Ekka_Resume.pdf resume.html
chromium --headless --no-pdf-header-footer \
  --print-to-pdf=../Jannet_Ekka_Founder_Resume.pdf resume_founder.html
```

Each is tuned to its page count above. Adding content can push one over; the fix is to step the body `font-size` and the matching spacing values
down together until it fits again, rather than cutting content blindly.

⚠️ **Verify the page count after every edit — and verify the FONT first.**
2026-09-22: `resume.html` had already drifted to **three pages** while the
committed PDF was two, so the source and the artefact disagreed and nobody
knew. Two traps found while fixing it:

1. **The body font is `Calibry`/`Carlito`.** On a box without either, the
   browser falls back to DejaVu Sans, which is wider, and the render is three
   pages *regardless of the content*. `fc-list | grep -i carlito` before
   trusting any page count; on Debian/Ubuntu,
   `apt-get install fonts-crosextra-carlito`.
2. **Measure, do not eyeball.**

   ```bash
   chromium --headless --no-sandbox --no-pdf-header-footer \
     --print-to-pdf=/tmp/r.pdf _portfolio_src/resume.html
   pdfinfo /tmp/r.pdf | grep Pages
   ```

2026-10-05: the committed `Jannet_Ekka_Resume.pdf` was itself **three** pages
(`pdfinfo`, built 09-22 — the font trap above). Both résumés rewritten (applied AI + evaluation, and a separate founder
page). The body is **10.1pt** (every `pt` value in the `<style>` block scaled
together); the 2-page résumé has about a third of page 2 free, so there is room
to add before anything has to go. Everything cut so far (VerseCanvas, the
Location Intelligence agent, the Internship Studio role) is one click away on
the site, which the header links.

2026-10-20: the applied AI résumé became one of four role variants (FDE, AI
trainer, model evaluation), built by `build_resumes.sh`. All four add the
October hackathon entries (Lore, Klarbrief, SMT World: Clock In, SMT Receipts),
and the eval and trainer variants add the RSNA label-quality check. Section
headings now carry `break-after: avoid`, after a heading was left alone at the
foot of page 1.
