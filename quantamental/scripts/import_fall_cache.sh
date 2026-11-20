#!/usr/bin/env bash
# Copy the public FRED / Yahoo CSV cache from the fall repo into data/raw.
# Licensed Bloomberg files were never in that repo, so nothing licensed is copied.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${FALL_REPO:-https://github.com/el0617/SIG_FALL_26}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --depth 1 --quiet "$SRC" "$TMP/fall"
mkdir -p data/raw
cp "$TMP"/fall/data/raw/*.csv data/raw/
echo "Copied $(ls data/raw/*.csv | wc -l) files into data/raw (data through the fall repo's last refresh)."
