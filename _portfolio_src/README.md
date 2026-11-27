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

## Where the site is served (since 2026-11-19)

- **https://jannetekka.cv/** is the main address: **Cloudflare Pages**, built from `main`. Pages runs `bash _portfolio_src/build_pages.sh` (build command) and publishes `_site` (output directory). The script copies only what the site links to (`index.html`, `assets/`, `certificates/`, `resumes/`, the two root PDFs and the photo), because the repo also holds files over Pages' 25 MiB per-file limit. It fails the deploy if `index.html` links a local file it didn't copy, so if the page starts linking a new local folder, add it to `SITE_FILES` in the script.
- **https://jannetekka.github.io/DSProjects/** is the backup and QA copy: GitHub Pages, from the same `main`. Never set a custom domain in the repo's Settings → Pages (and never add a `CNAME` file): GitHub would then redirect the github.io address to jannetekka.cv, and the backup would stop being independent.
- The domain is registered at ola.cv (free first year, expires 18 Nov 2027, auto-renew off); its nameservers point to Cloudflare, where its DNS and the `www` → apex redirect live.
- The page carries `<link rel="canonical" href="https://jannetekka.cv/">`, so search engines treat jannetekka.cv as the main copy.

## The résumés

Five résumés, all generated from HTML in this folder, the same build-and-verify
approach as the site. Four are role variants for job applications; they share
contact, experience and education, and differ in tagline, summary, skills and
which projects lead.

**Since 2026-11-19 the site links one résumé** (Jannet: "keep only about jobs, one generic résumé in the Word format I made, for FDE or AI/ML/data roles"). The nav button reads "Resume" and downloads `Jannet_Ekka_Resume.pdf`. The founder résumé and the role variants below are no longer linked from the site; their files stay in the repo.

| PDF | source | for | length |
|---|---|---|---|
| **`Jannet_Ekka_Resume.pdf` (repo root) + `resumes/Jannet_Ekka_Resume.docx`** | `build_resume_docx.js` | **the one the site links**: forward deployed, applied AI/ML and data roles, in Jannet's Word table layout; LibreOffice renders the PDF | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_Applied_AI.pdf` | `resume.html` | applied AI engineer roles (was the site's nav button until 11-19) | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_FDE.docx` + `.pdf` | `build_resume_fde_docx.js` | forward deployed engineer roles, in Jannet's Word table layout (name in the page header, one bordered table, grey section bars) | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_Data_Science.docx` + `.pdf` | `build_resume_data_science_docx.js` | data scientist roles at insurers and other tabular-data teams (first sent to Ominimo via JigJoy, 11-16): modelling and evaluation first, then data engineering, then agents; same Word layout as FDE | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_AI_Trainer.pdf` | `resume_ai_trainer.html` | AI trainer / LLM output-evaluation work | **exactly 2 pages** |
| `resumes/Jannet_Ekka_Resume_Model_Evaluation.pdf` | `resume_model_eval.html` | model evaluation, AI QA, red-teaming | **exactly 2 pages** |
| `Jannet_Ekka_Founder_Resume.pdf` (repo root) | `resume_founder.html` | grants, accelerators, investors (not linked from the site since 11-19) | **exactly 1 page** |

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

2026-11-02: the FDE résumé moved to Jannet's own Word layout (her 10-31 edit
of the HTML version, rebuilt as a generated `.docx` so it can be edited in Word
and regenerated). `build_resume_fde_docx.js` writes the `.docx`; LibreOffice
renders the PDF. On a box without Calibri, map Calibri and Calibri Light to
Carlito in fontconfig first, or the page count is wrong. `resume_fde.html` is
the older HTML version, kept for reference and no longer rendered.

2026-11-16: added the Data Scientist variant, for Ominimo (car-insurance
insurtech, offices in Belgrade, Novi Sad and Budapest), which asked JigJoy
hackathon participants for CVs. Built like the FDE one: `build_resume_data_science_docx.js`
writes the `.docx`, LibreOffice renders the PDF, so the two never disagree. It
leads with tabular modelling and evaluation (SMT's statistical gate, the
portfolio churn and loan-default models, the semiconductor leak found on review),
adds November 2026 (Aftershock, Lights Out, Catalyst, the submitted entries)
and says plainly that dbt, Trino and Databricks are not used yet. The `LOCATION`
constant at the top of the content sets the header's location line.
Fontconfig: alias both Calibri and Calibri Light to Carlito
(`~/.config/fontconfig/fonts.conf`) before rendering.

2026-11-19: the portfolio link became `jannetekka.cv`, and `resume.html` jumped
from 2 pages to 3, although the text got shorter. **Third trap: Chrome shrinks
the whole page to fit anything too wide.** The contact line had no break
points (the `<span>`s touch, and each is `nowrap`), so it was wider than the
page (955 px against 711), and Chrome printed everything at about 74% of the
sizes in the file. The "10.1pt" body above was really printing at about 7.5pt.
A shorter contact line meant less shrinking, bigger text and a third page.
Fixed in `resume.html`: `.contact` is now `display: flex; flex-wrap: wrap`, and
every `pt` value was scaled by 0.76, the largest factor that fits 2 pages
(body 7.69pt, about 2% larger than the earlier PDF). `resume_ai_trainer.html`
and `resume_model_eval.html` still overflow the same way (794 and 861 px) and
are shrunk by Chrome, but print at the right page counts; give them the same
fix when they're next edited. To check for overflow, load the page at 711 px
wide with print media and compare `document.documentElement.scrollWidth` to
711.
