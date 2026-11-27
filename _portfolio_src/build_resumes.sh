#!/usr/bin/env bash
# Renders the main résumé and the job-application variants to PDF and prints each page count.
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
# The résumé the portfolio links (since 2026-11-19): one generic version in Jannet's Word layout,
# for forward deployed, applied AI/ML and data roles. Its PDF is ../Jannet_Ekka_Resume.pdf, the
# address older links already use. The role variants below are kept but no longer linked.
if node -e "require('docx')" 2>/dev/null && command -v soffice >/dev/null; then
  node build_resume_docx.js ../resumes/Jannet_Ekka_Resume.docx >/dev/null
  soffice --headless --convert-to pdf --outdir ../resumes ../resumes/Jannet_Ekka_Resume.docx >/dev/null 2>&1
  mv ../resumes/Jannet_Ekka_Resume.pdf ../Jannet_Ekka_Resume.pdf
  printf '%-50s %s pages\n' ../Jannet_Ekka_Resume.pdf "$(pdfinfo ../Jannet_Ekka_Resume.pdf | awk '/^Pages/{print $2}')"
else
  echo "Main résumé NOT built: needs the docx npm package (npm install docx) and LibreOffice (soffice)" >&2
  exit 1
fi
render resume.html            ../resumes/Jannet_Ekka_Resume_Applied_AI.pdf
# FDE: since 2026-11-02 the source is Jannet's Word table layout, generated as .docx
# (resume_fde.html is the older HTML version and is no longer rendered).
if node -e "require('docx')" 2>/dev/null && command -v soffice >/dev/null; then
  node build_resume_fde_docx.js ../resumes/Jannet_Ekka_Resume_FDE.docx >/dev/null
  soffice --headless --convert-to pdf --outdir ../resumes ../resumes/Jannet_Ekka_Resume_FDE.docx >/dev/null 2>&1
  printf '%-50s %s pages\n' ../resumes/Jannet_Ekka_Resume_FDE.pdf "$(pdfinfo ../resumes/Jannet_Ekka_Resume_FDE.pdf | awk '/^Pages/{print $2}')"
else
  echo "FDE résumé skipped: needs the docx npm package (npm install docx) and LibreOffice (soffice)" >&2
fi
# Data Scientist (insurtech data roles, 2026-11-16): same Word layout as FDE, generated as .docx.
if node -e "require('docx')" 2>/dev/null && command -v soffice >/dev/null; then
  node build_resume_data_science_docx.js ../resumes/Jannet_Ekka_Resume_Data_Science.docx >/dev/null
  soffice --headless --convert-to pdf --outdir ../resumes ../resumes/Jannet_Ekka_Resume_Data_Science.docx >/dev/null 2>&1
  printf '%-50s %s pages\n' ../resumes/Jannet_Ekka_Resume_Data_Science.pdf "$(pdfinfo ../resumes/Jannet_Ekka_Resume_Data_Science.pdf | awk '/^Pages/{print $2}')"
else
  echo "Data Science résumé skipped: needs the docx npm package and LibreOffice (soffice)" >&2
fi
render resume_ai_trainer.html ../resumes/Jannet_Ekka_Resume_AI_Trainer.pdf
render resume_model_eval.html ../resumes/Jannet_Ekka_Resume_Model_Evaluation.pdf
# Role-tailored versions of the generic Word resume (11-27): only summary and skills change.
if node -e "require('docx')" 2>/dev/null && command -v soffice >/dev/null; then
  for pair in htc:AI_Engineer freecharge:Lead_AI_ML; do
    ROLE=${pair%%:*} node build_resume_docx.js "../resumes/Jannet_Ekka_Resume_${pair#*:}.docx" >/dev/null
    soffice --headless --convert-to pdf --outdir ../resumes "../resumes/Jannet_Ekka_Resume_${pair#*:}.docx" >/dev/null 2>&1
    printf '%-50s %s pages\n' "../resumes/Jannet_Ekka_Resume_${pair#*:}.pdf" "$(pdfinfo "../resumes/Jannet_Ekka_Resume_${pair#*:}.pdf" | awk '/^Pages/{print $2}')"
  done
fi
