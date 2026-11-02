#!/usr/bin/env bash
# Renders the four job-application résumés to PDF and prints each page count.
# Run from anywhere: bash _portfolio_src/build_resumes.sh
# The founder résumé is not built here; see README.md.
set -euo pipefail
cd "$(dirname "$0")"

CHROME="${CHROME:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || echo /opt/pw-browsers/chromium)}"

# Without Carlito the browser falls back to a wider font and every page count is wrong.
if ! fc-list : family | grep -i carlito >/dev/null; then
  echo "Carlito font missing (apt-get install fonts-crosextra-carlito); page counts would be wrong." >&2
  exit 1
fi

render() {  # render <source.html> <output.pdf>
  "$CHROME" --headless --no-sandbox --no-pdf-header-footer --print-to-pdf="$2" "$1" 2>/dev/null
  printf '%-50s %s pages\n' "$2" "$(pdfinfo "$2" | awk '/^Pages/{print $2}')"
}

mkdir -p ../resumes
render resume.html            ../Jannet_Ekka_Resume.pdf
cp ../Jannet_Ekka_Resume.pdf  ../resumes/Jannet_Ekka_Resume_Applied_AI.pdf
# FDE: since 2026-11-02 the source is Jannet's Word table layout, generated as .docx
# (resume_fde.html is the older HTML version and is no longer rendered).
if node -e "require('docx')" 2>/dev/null && command -v soffice >/dev/null; then
  node build_resume_fde_docx.js ../resumes/Jannet_Ekka_Resume_FDE.docx >/dev/null
  soffice --headless --convert-to pdf --outdir ../resumes ../resumes/Jannet_Ekka_Resume_FDE.docx >/dev/null 2>&1
  printf '%-50s %s pages\n' ../resumes/Jannet_Ekka_Resume_FDE.pdf "$(pdfinfo ../resumes/Jannet_Ekka_Resume_FDE.pdf | awk '/^Pages/{print $2}')"
else
  echo "FDE résumé skipped: needs the docx npm package (npm install docx) and LibreOffice (soffice)" >&2
fi
render resume_ai_trainer.html ../resumes/Jannet_Ekka_Resume_AI_Trainer.pdf
render resume_model_eval.html ../resumes/Jannet_Ekka_Resume_Model_Evaluation.pdf
