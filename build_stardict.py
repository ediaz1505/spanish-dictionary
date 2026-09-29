#!/usr/bin/env python3
"""
Parse doozan/spanish_data's es-en.data into a StarDict dictionary
(.ifo + .idx + .dict), including its already-tagged idiomatic phrases.
"""
import html
import struct
import sys

SRC = "spanish_data/es-en.data"
MANUAL = "manual_additions.data"  # phrases missing from Wiktionary; same format, appended by hand
OUT_BASE = "es-en-idioms"

def parse(path):
    entries = []  # (headword, [ (pos, [ (gloss, [quals]) ]) ])
    headword = None
    blocks = []  # current entry's pos blocks
    cur_pos = None
    cur_glosses = None  # list of (gloss_text, [qualifier_text,...]) for cur_pos
    cur_gloss_idx = None

    def flush_entry():
        if headword is not None and blocks:
            entries.append((headword, blocks))

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line == "_____":
                if cur_pos is not None:
                    blocks.append((cur_pos, cur_glosses))
                flush_entry()
                headword = None
                blocks = []
                cur_pos = None
                cur_glosses = None
                cur_gloss_idx = None
                continue
            if headword is None:
                headword = line.strip()
                continue
            if line.startswith("pos:"):
                if cur_pos is not None:
                    blocks.append((cur_pos, cur_glosses))
                cur_pos = line.split(":", 1)[1].strip()
                cur_glosses = []
                cur_gloss_idx = None
                continue
            stripped = line.strip()
            if line.startswith("  gloss:"):
                gloss_text = stripped.split(":", 1)[1].strip()
                cur_glosses.append([gloss_text, []])
                cur_gloss_idx = len(cur_glosses) - 1
                continue
            if line.startswith("    q:") and cur_gloss_idx is not None:
                cur_glosses[cur_gloss_idx][1].append(("q", stripped.split(":", 1)[1].strip()))
                continue
            if line.startswith("    syn:") and cur_gloss_idx is not None:
                cur_glosses[cur_gloss_idx][1].append(("syn", stripped.split(":", 1)[1].strip()))
                continue
            # ignore meta/etymology/other lines
    if cur_pos is not None:
        blocks.append((cur_pos, cur_glosses))
    flush_entry()
    return entries


def render_html(headword, blocks):
    parts = [f'<b>{html.escape(headword)}</b>']
    is_idiom = len(headword.split()) > 1
    if is_idiom:
        parts.append(' <i>(phrase)</i>')
    for pos, glosses in blocks:
        parts.append(f'<br/><span class="pos">{html.escape(pos)}.</span> ')
        gloss_strs = []
        for gloss_text, quals in glosses:
            s = html.escape(gloss_text)
            qbits = [f"{k}: {html.escape(v)}" for k, v in quals]
            if qbits:
                s += f' <i>({"; ".join(qbits)})</i>'
            gloss_strs.append(s)
        parts.append("; ".join(gloss_strs))
    return "".join(parts)


def main():
    print("Parsing", SRC, file=sys.stderr)
    entries = parse(SRC)
    print(f"Parsed {len(entries)} headwords", file=sys.stderr)

    import os
    if os.path.exists(MANUAL):
        manual_entries = parse(MANUAL)
        print(f"Parsed {len(manual_entries)} manual additions from {MANUAL}", file=sys.stderr)
        entries = entries + manual_entries

    # Merge duplicate headwords (same word can recur, e.g. different etymologies)
    merged = {}
    order = []
    for headword, blocks in entries:
        if headword not in merged:
            merged[headword] = []
            order.append(headword)
        merged[headword].extend(blocks)

    idiom_count = sum(1 for h in order if len(h.split()) > 1)
    print(f"{len(order)} unique headwords, {idiom_count} multi-word (idioms/phrases)", file=sys.stderr)

    dict_path = f"{OUT_BASE}.dict"
    idx_path = f"{OUT_BASE}.idx"
    ifo_path = f"{OUT_BASE}.ifo"

    idx_entries = []
    with open(dict_path, "wb") as df:
        offset = 0
        for headword in sorted(order, key=lambda s: s.encode("utf-8")):
            body = render_html(headword, merged[headword]).encode("utf-8")
            df.write(body)
            idx_entries.append((headword, offset, len(body)))
            offset += len(body)

    with open(idx_path, "wb") as f:
        for headword, offset, size in idx_entries:
            f.write(headword.encode("utf-8") + b"\x00")
            f.write(struct.pack(">I", offset))
            f.write(struct.pack(">I", size))

    with open(ifo_path, "w", encoding="utf-8") as f:
        f.write("StarDict's dict ifo file\n")
        f.write("version=2.4.2\n")
        f.write(f"wordcount={len(idx_entries)}\n")
        import os
        f.write(f"idxfilesize={os.path.getsize(idx_path)}\n")
        f.write("bookname=Spanish-English (words + idioms)\n")
        f.write("sametypesequence=h\n")
        f.write("description=Built from doozan/spanish_data (Wiktionary CC-BY-SA), words and idiomatic phrases in one dictionary.\n")

    print("Wrote", dict_path, idx_path, ifo_path, file=sys.stderr)


if __name__ == "__main__":
    main()
