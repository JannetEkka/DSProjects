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

## The résumé

`../Jannet_Ekka_Resume.pdf` is generated from `resume.html` in this folder —
the same build-and-verify approach as the site. To regenerate after editing:

```bash
chromium --headless --no-pdf-header-footer \
  --print-to-pdf=../Jannet_Ekka_Resume.pdf _portfolio_src/resume.html
```

It is tuned to land on **exactly two pages**. Adding content can push it to
three; the fix is to step the body `font-size` and the matching spacing values
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
2. **Measure, do not eyeball.** Render and count:

   ```bash
   chromium --headless --no-sandbox --no-pdf-header-footer \
     --print-to-pdf=/tmp/r.pdf _portfolio_src/resume.html
   python3 -c "from pdfminer.high_level import extract_pages; \
     print(sum(1 for _ in extract_pages('/tmp/r.pdf')))"
   ```

The current source is at a **0.92 type scale** and holds two pages. If it
spills again, cut the entry that earns its place least — everything cut so far
(VerseCanvas, the 13-project ML portfolio, the Internship Studio role) is one
click away on the site, which the header links.
