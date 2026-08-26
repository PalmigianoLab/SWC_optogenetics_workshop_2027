#!/usr/bin/env python3
"""Take portrait files and put them into assets/img/ ready for the site.

Drop photographs anywhere (~/Downloads by default), named after the person —
"Kayvon-Daie.jpeg", "ran darshan.jpg" and "karel_svoboda.jpeg" all work:

    python3 scripts/import_portraits.py [source_dir]

Only files whose name matches somebody in _data/*.yml are taken, so pointing it
at a folder full of figures and screenshots is safe: everything else is ignored.
Each match is cropped to a square around where a head sits, resized to 600px and
saved as firstname_lastname.jpg. Re-running is safe; nothing is deleted.

Run scripts/people_from_sheet.py afterwards to wire the photographs in.

Needs Pillow: python3 -m pip install --user pillow
"""

import pathlib
import re
import sys
import unicodedata

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
SIZE = 600
VERTICAL_BIAS = 0.35   # heads sit above the middle of a portrait


def words(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return {w for w in re.split(r"[^A-Za-z]+", text.lower()) if len(w) > 2}


def guest_list():
    people = {}
    for data in ("keynotes", "speakers", "organizers"):
        path = ROOT / "_data" / f"{data}.yml"
        if not path.exists():
            continue
        for name in re.findall(r'- name: "(.+)"', path.read_text(encoding="utf-8")):
            people[name] = words(name)
    return people


def main():
    source = pathlib.Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else pathlib.Path.home() / "Downloads"
    people = guest_list()
    if not people:
        sys.exit("No people found in _data/ — run scripts/people_from_sheet.py first.")

    written, unmatched = 0, []
    for path in sorted(source.iterdir()):
        if path.suffix.lower() not in SUFFIXES:
            continue
        found = [n for n, w in people.items() if w & words(path.stem)]
        if len(found) != 1:
            unmatched.append(path.name)
            continue

        person = found[0]
        try:
            image = Image.open(path).convert("RGB")
        except Exception as error:
            print(f"  unreadable  {path.name}  ({type(error).__name__})")
            continue

        width, height = image.size
        side = min(width, height)
        left = (width - side) // 2
        top = max(0, int((height - side) * VERTICAL_BIAS))
        image = image.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)

        filename = "_".join(sorted(words(person), key=person.lower().find)) + ".jpg"
        image.save(OUT / filename, quality=88)
        print(f"  {filename:<26} <- {path.name}   ({person})")
        written += 1

    print(f"\n{written} portraits imported.")
    if unmatched:
        print(f"{len(unmatched)} file(s) ignored — no one on the guest list matched their name.")


if __name__ == "__main__":
    main()
