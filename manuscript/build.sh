#!/usr/bin/env bash
#
# Build the manuscript PDF with Pandoc.
#
#   ./build.sh                     # -> out/manuscript.pdf
#   OUT=out/draft.pdf ./build.sh   # custom output path
#   PDF_ENGINE=lualatex ./build.sh
#
# Requires Pandoc (>= 3) and a unicode-capable LaTeX engine (xelatex by default; the
# manuscript uses glyphs like α σ ρ ∫ ∩ → that pdflatex cannot set). Citations resolve
# from references.bib through Pandoc's built-in citeproc — no separate bibtex/biber pass.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

SRC="${SRC:-manuscript.md}"
OUT="${OUT:-out/manuscript.pdf}"
PDF_ENGINE="${PDF_ENGINE:-xelatex}"

mkdir -p "$(dirname "$OUT")"

args=(
  "$SRC"
  --citeproc
  --pdf-engine="$PDF_ENGINE"
  --metadata=date:"$(date +'%B %d, %Y')"
  -V geometry:margin=1in
  -V colorlinks=true
  -V linkcolor=RoyalBlue
  -V urlcolor=RoyalBlue
  -o "$OUT"
)

# DejaVu carries the broad symbol coverage the manuscript needs (∫ ∩ → σ α …). Use it when
# fontconfig can see it; otherwise fall back to the engine default (Latin Modern) so a build
# without DejaVu still succeeds.
if command -v fc-list >/dev/null 2>&1 && fc-list | grep -qi "DejaVu Serif"; then
  args+=(-V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono")
fi

echo "pandoc: building $OUT (engine: $PDF_ENGINE)"
pandoc "${args[@]}"
echo "wrote $DIR/$OUT"
