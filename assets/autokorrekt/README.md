# AutoKorrekt screenshots

The portfolio's AutoKorrekt card builds its gallery from the files listed in
the `autokorrekt` entry of `_portfolio_src/data.py`. Currently:

| File | Screen |
|---|---|
| `Index_page_signup.png` | Sign Up as a Teacher |
| `Index_pg_signin.png`   | Sign In |
| `add_Test.png`          | Add Class — class/subject/test details, student-list CSV + question-paper upload |
| `students.png`          | Students page — per-student pipeline (upload → processing → status) and bulk answer-sheet upload |

Adding a screenshot means adding it to the `shots` list in `data.py` and
rebuilding — dropping a file in here alone does nothing:

```bash
python3 _portfolio_src/build.py index.html
```

A file referenced but missing is removed from the page at load time rather
than showing a broken image.

## Before adding a screenshot — check what is in the frame

**Crop to the application window.** A full-screen capture also publishes your
bookmarks bar, open tabs, taskbar, notifications and system clock. Two such
captures were removed from this folder for exactly that reason: one showed an
unrelated site plus a full desktop, the other showed a logged-in email tab and
a graded quiz score.

Quick checklist:

- Is this actually the project the folder is for?
- Any other tabs, bookmarks, or window titles visible?
- Any email address, real student name, or account identifier on screen?
- Any grade, score, or private record that is not yours to publish?

`Win + Shift + S` (Windows) or `Cmd + Shift + 4` (macOS) captures a region
rather than the whole screen.
