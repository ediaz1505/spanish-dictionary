# Spanish-English (words + idioms)

A native macOS `Dictionary.app` dictionary — Spanish↔English words plus
17,500+ idioms and set phrases, so highlighting a phrase in the system
Look Up menu gives its real meaning instead of a literal word-by-word guess.

Built from:
- **[doozan/spanish_data](https://github.com/doozan/spanish_data)** — Wiktionary + Tatoeba data, CC-BY-SA. Base word list and a first layer of idioms.
- **[Language Realm's Spanish Idiom Dictionary](https://www.languagerealm.com/spanish/spanishidioms.php)** — curated idioms not already in Wiktionary, added by hand in `manual_additions.data`.

## Install

Open Terminal and run:

```
curl -fsSL https://raw.githubusercontent.com/ediaz1505/spanish-dictionary/main/install.sh | bash
```

This downloads the latest build from [Releases](../../releases) and installs
it into `~/Library/Dictionaries`. A plain Finder unzip-and-drag often silently
fails here — downloaded files get a Gatekeeper quarantine flag that blocks
moving a `.dictionary` bundle into place, with no clear error — so the script
handles that (`xattr -dr com.apple.quarantine`) for you.

Then: quit Dictionary.app if it's open (⌘Q), reopen it, go to
**Dictionary.app → Settings**, and tick **"Spanish-English (words + idioms)"**.

Prefer to do it by hand? Download `es-en-idioms.dictionary.zip` from
[Releases](../../releases), unzip it, then in Terminal run
`xattr -dr com.apple.quarantine path/to/es-en-idioms.dictionary` before
moving it into `~/Library/Dictionaries` — skipping that step is the most
common reason the move silently doesn't go through.

## How it stays current
A GitHub Actions workflow (`.github/workflows/update.yml`) runs weekly:
- Checks doozan/spanish_data for a newer release; rebuilds if there is one.
- Re-scrapes Language Realm roughly every 6 months (it's a static page with
  no version to poll), diffs against every headword already known, and adds
  only genuinely new idioms.
- When either happens, it rebuilds the dictionary, publishes a new Release
  with the `.dictionary.zip` attached, and commits the updated
  `manual_additions.data` back to this repo.

## Building locally
Requires macOS (uses Apple's Dictionary Development Kit under the hood).

```
python3 build_stardict.py          # needs spanish_data/es-en.data present
# then convert the resulting StarDict files with:
# https://github.com/Sangyop-Lee/stardict2mac
```

## License
Base dictionary data is CC-BY-SA (Wiktionary/Tatoeba, via doozan/spanish_data).
Scripts in this repo (`build_stardict.py`, `scrape_language_realm.py`) are
provided as-is.
