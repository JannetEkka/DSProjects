#!/usr/bin/env bash
# Collects the portfolio site into _site/ for Cloudflare Pages (jannetekka.cv).
# Cloudflare Pages settings: build command `bash _portfolio_src/build_pages.sh`, output directory `_site`.
# Why: the repo also holds files over Pages' 25 MiB per-file limit (a model .pkl, node_modules
# binaries), so Pages publishes only what the site links to. GitHub Pages still serves the whole
# repo at https://jannetekka.github.io/DSProjects/ as the backup copy.
# If index.html starts linking a new local folder or file, add it to SITE_FILES below.
set -euo pipefail
cd "$(dirname "$0")/.."

SITE_FILES=(
  index.html
  assets
  certificates
  resumes
  Jannet_Ekka_Resume.pdf
  Jannet_Ekka_Founder_Resume.pdf
  "profile pic.png"
)

rm -rf _site
mkdir _site
for f in "${SITE_FILES[@]}"; do
  cp -r "$f" _site/
done

# Fail the deploy if index.html links a local file that wasn't copied.
missing=0
while IFS= read -r ref; do
  path="${ref%%[#?]*}"
  path="${path//%20/ }"
  [ -z "$path" ] && continue
  if [ ! -e "_site/$path" ]; then
    echo "missing from _site: $path" >&2
    missing=1
  fi
done < <(grep -oE '(href|src)="[^"]+"' index.html | sed -E 's/^(href|src)="//; s/"$//' \
         | grep -vE '^(https?:|mailto:|tel:|data:|#|javascript:)' | sort -u)
[ "$missing" -eq 0 ] || exit 1

echo "_site: $(find _site -type f | wc -l) files, $(du -sh _site | cut -f1)"
