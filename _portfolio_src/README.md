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
