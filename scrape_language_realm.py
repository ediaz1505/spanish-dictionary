#!/usr/bin/env python3
"""
Scrape languagerealm.com's Spanish Idiom Dictionary, diff against headwords
already in es-en.data + manual_additions.data, and append any genuinely new
idioms to manual_additions.data in the same format build_stardict.py expects.

Fetching is done via curl subprocesses (urllib gets HTTP 406 from this site).
Prints a one-line summary to stdout: "scraped=N new=M" for the caller to log.
"""
import html
import re
import subprocess
import sys

PAGES = ["spanishidioms.php"] + [
    f"spanishidioms_{c}.php" for c in "bcdefghijlmnopqrstuvyz"
]
BASE = "https://www.languagerealm.com/spanish/"

SRC = "spanish_data/es-en.data"
MANUAL = "manual_additions.data"

ENTRY_RE = re.compile(
    r"<p>\s*<strong>(.*?)</strong>\s*<br\s*/?>\s*(.*?)</p>", re.IGNORECASE | re.DOTALL
)
TAG_RE = re.compile(r"<[^>]+>")


def clean(s):
    s = TAG_RE.sub("", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def known_headwords():
    known = set()
    for path in (SRC, MANUAL):
        headword = None
        try:
            with open(path, encoding="utf-8") as f:
                for raw in f:
                    line = raw.rstrip("\n")
                    if line == "_____":
                        headword = None
                        continue
                    if headword is None:
                        headword = line.strip()
                        known.add(headword.lower())
        except FileNotFoundError:
            continue
    return known


def fetch(page):
    try:
        out = subprocess.run(
            ["curl", "-s", "--max-time", "20", BASE + page],
            capture_output=True, timeout=30,
        )
        return out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return ""


def main():
    known = known_headwords()
    scraped = {}
    for page in PAGES:
        body = fetch(page)
        for m in ENTRY_RE.finditer(body):
            idiom = clean(m.group(1)).lower()
            meaning = clean(m.group(2))
            if idiom and meaning:
                scraped[idiom] = meaning

    new_entries = {k: v for k, v in scraped.items() if k not in known}

    if new_entries:
        with open(MANUAL, "a", encoding="utf-8") as f:
            for idiom, meaning in sorted(new_entries.items()):
                f.write(idiom + "\n")
                f.write("pos: phrase\n")
                f.write(f"  gloss: {meaning}\n")
                f.write("    q: idiomatic (source: Language Realm)\n")
                f.write("_____\n")

    print(f"scraped={len(scraped)} new={len(new_entries)}")


if __name__ == "__main__":
    main()
