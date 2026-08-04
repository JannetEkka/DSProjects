# AutoKorrekt screenshots

The portfolio's AutoKorrekt card renders a gallery from this folder.
Drop the four PNGs in with **exactly** these names:

| File | Screen |
|---|---|
| `signup.png`    | Sign Up as a Teacher |
| `signin.png`    | Sign In |
| `add-class.png` | Add Class — class/subject/test details, student-list CSV + question-paper upload |
| `students.png`  | Students page — per-student pipeline (upload → processing → status) and bulk answer-sheet upload |

Any file that is missing is **removed from the page at load time** rather than
showing a broken image, so the card stays clean until you add them. No rebuild
is needed after dropping the files in — the gallery reads them directly.

Wireframes can go here too; add them to the `shots` list for the `autokorrekt`
entry in `_portfolio_src/data.py`, then rebuild:

```bash
python3 _portfolio_src/build.py index.html
```
