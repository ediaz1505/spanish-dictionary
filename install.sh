#!/bin/bash
# Installs "Spanish-English (words + idioms)" into Dictionary.app.
# Downloads the latest build from GitHub Releases, handles the Gatekeeper
# quarantine flag that blocks a plain Finder move/copy, and installs it.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ediaz1505/spanish-dictionary/main/install.sh | bash
set -euo pipefail

REPO="ediaz1505/spanish-dictionary"
BUNDLE_NAME="es-en-idioms.dictionary"
DEST="$HOME/Library/Dictionaries"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Finding latest release..."
asset_url=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
  | python3 -c "import json,sys; a=json.load(sys.stdin)['assets']; print(next(x['browser_download_url'] for x in a if x['name'].endswith('.zip')))")

echo "Downloading $asset_url"
curl -fsSL -o "$TMP/dict.zip" "$asset_url"

echo "Extracting..."
ditto -xk "$TMP/dict.zip" "$TMP/extracted"

echo "Removing quarantine flag (this is what blocks a plain Finder move/copy)..."
xattr -dr com.apple.quarantine "$TMP/extracted/$BUNDLE_NAME" 2>/dev/null || true

mkdir -p "$DEST"
if [ -e "$DEST/$BUNDLE_NAME" ]; then
  echo "Backing up existing install to $BUNDLE_NAME.bak"
  rm -rf "$DEST/$BUNDLE_NAME.bak"
  mv "$DEST/$BUNDLE_NAME" "$DEST/$BUNDLE_NAME.bak"
fi

mv "$TMP/extracted/$BUNDLE_NAME" "$DEST/$BUNDLE_NAME"

echo
echo "Installed to $DEST/$BUNDLE_NAME"
echo "Now: quit Dictionary.app if it's open (Cmd+Q), reopen it, go to"
echo "Dictionary.app -> Settings, and tick \"Spanish-English (words + idioms)\"."
