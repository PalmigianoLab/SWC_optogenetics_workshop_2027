#!/usr/bin/env python3
"""Lay out the programme and write _data/schedule.yml.

Each full day runs to the same shape:

    09:30  keynote (45) + 2 talks
    11:15  coffee (30)
    11:45  2 talks
    12:45  lunch (75 minutes)
    14:00  keynote (45) + 2 talks
    15:45  coffee (40)
    16:25  3 talks
    17:55  close

Thursday's talks are followed by a poster session running to 21:00.

Wednesday is an evening only: nothing before 17:00, then registration, a
keynote and two talks, then dinner. Every slot length comes from the constants
below, so changing one moves everything after it. Twenty talk slots in all.

Speakers come from _data/*.yml. The organisers speak too, and some of them have
to be in a particular half of the day — see FIXED below. Everybody else is
placed to alternate theory and experiment, using the spreadsheet's column.
Ordering beyond that is arbitrary: this is a draft to rearrange, not a
considered programme. Once you edit _data/schedule.yml by hand, stop running
this or your changes will be lost.

    python3 scripts/make_schedule.py
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYNOTE, TALK = 45, 30
MORNING_COFFEE, AFTERNOON_COFFEE = 30, 45   # 45 puts the posters on 18:00
REGISTRATION = 15

# Wednesday runs from 17:00 to dinner; the full days break for lunch at a fixed
# hour rather than a fixed length, so lunch absorbs any drift in the morning.
WEDNESDAY_START, DINNER = 16 * 60 + 45, 19 * 60 + 30
LUNCH_END = 14 * 60

# One day carries the poster session, which runs from the last talk to 21:00.
POSTER_DAY, POSTERS_END = "Thursday 1 April", 21 * 60

# Keynotes are placed in this order — Wednesday evening, then Thursday morning,
# Thursday afternoon, Friday morning, Friday afternoon. Anyone not named here
# follows in the order the spreadsheet lists them.
# While the programme is still being settled, no names appear at all: each slot
# just says whether it is a keynote or a talk. Set this to True once the running
# order is decided and the names go back in.
NAME_THE_TALKS = False

KEYNOTE_ORDER = ["Vivek Jayaraman"]

# Organisers who speak, and which half of the day they need.
FIXED = {
    "Arseny Finkelstein": "morning",
    "Agostina Palmigiano": "morning",
    "Andrew Leifer": "afternoon",
}


# Straight swaps applied after everything else is placed, for the hand
# adjustments that do not follow from any rule.
SWAPS = []


def people(data):
    text = (ROOT / "_data" / f"{data}.yml").read_text(encoding="utf-8")
    out = []
    for block in text.split("- name: ")[1:]:
        name = block.split('"')[1]
        field = re.search(r'field: "([^"]*)"', block)
        out.append((name, (field.group(1) if field else "").lower()))
    return out


def interleave(speakers):
    """Alternate theory and experiment, starting with whichever is scarcer."""
    theory = [s for s in speakers if s[1].startswith("theory")]
    experiment = [s for s in speakers if s[1].startswith("experiment")]
    other = [s for s in speakers if s not in theory and s not in experiment]
    short, long_ = sorted((theory, experiment), key=len)
    mixed, i, j = [], 0, 0
    while i < len(short) or j < len(long_):
        if i < len(short):
            mixed.append(short[i]); i += 1
        if j < len(long_):
            mixed.append(long_[j]); j += 1
        if j < len(long_) and len(long_) - j > 2 * (len(short) - i):
            mixed.append(long_[j]); j += 1
    return [n for n, _ in mixed + other]


def hhmm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


class Day:
    """Slots laid end to end from a start time, in minutes past midnight."""

    def __init__(self, start):
        self.rows, self.clock = [], start

    def add(self, length, kind, what=None, period=None):
        self.rows.append((f"{hhmm(self.clock)} – {hhmm(self.clock + length)}",
                          kind, what, period))
        self.clock += length

    def until(self, end, kind, what):
        """A slot that runs to a fixed time rather than for a fixed length."""
        self.rows.append((f"{hhmm(self.clock)} – {hhmm(end)}", kind, what, None))
        self.clock = end

    def at(self, time, kind, what):
        """A slot with a start time and no end — dinner, and the close."""
        self.rows.append((hhmm(time), kind, what, None))


def skeleton():
    """Every slot in the workshop, before anyone is assigned to it."""
    days = []

    wed = Day(WEDNESDAY_START)
    wed.add(REGISTRATION, "break", "Registration and coffee")
    wed.add(KEYNOTE, "keynote")
    wed.add(TALK, "talk", None, "evening")
    wed.add(TALK, "talk", None, "evening")
    wed.at(DINNER, "dinner", "Dinner at a restaurant")
    days.append(("Wednesday 31 March", wed.rows))

    for title in ("Thursday 1 April", "Friday 2 April"):
        day = Day(9 * 60 + 30)
        day.add(KEYNOTE, "keynote")
        day.add(TALK, "talk", None, "morning")
        day.add(TALK, "talk", None, "morning")
        day.add(MORNING_COFFEE, "break", "Coffee")
        day.add(TALK, "talk", None, "morning")
        day.add(TALK, "talk", None, "morning")
        day.until(LUNCH_END, "lunch", "Lunch")
        day.add(KEYNOTE, "keynote")
        day.add(TALK, "talk", None, "afternoon")
        day.add(TALK, "talk", None, "afternoon")
        day.add(AFTERNOON_COFFEE, "break", "Coffee")
        day.add(TALK, "talk", None, "afternoon")
        day.add(TALK, "talk", None, "afternoon")
        day.add(TALK, "talk", None, "afternoon")
        if title == POSTER_DAY:
            day.until(POSTERS_END, "poster", "Poster session")
        else:
            day.at(day.clock, "break", "Close")
        days.append((title, day.rows))

    return days


def main():
    keynotes = [n for n, _ in people("keynotes")]
    first = [n for n in KEYNOTE_ORDER if n in keynotes]
    keynotes = first + [n for n in keynotes if n not in first]

    speaking_organisers = [p for p in people("organizers") if p[0] in FIXED]
    pool = interleave(people("speakers") + speaking_organisers)

    days = skeleton()
    # index every talk slot so the constrained people can be placed first
    talk_slots = [(d, i) for d, (_, rows) in enumerate(days)
                  for i, row in enumerate(rows) if row[1] == "talk"]
    assigned = {}

    for name, period in FIXED.items():
        if name not in pool:
            continue
        for day_i, row_i in talk_slots:
            if (day_i, row_i) in assigned:
                continue
            if days[day_i][1][row_i][3] == period:
                assigned[(day_i, row_i)] = name
                pool.remove(name)
                break

    # Fill in order, so any unfilled slots fall at the end of the programme.
    free = [key for key in talk_slots if key not in assigned]
    gaps = max(0, len(free) - len(pool))
    rest = iter(pool)
    for key in free:
        assigned[key] = next(rest, "Open slot")

    for one, other in SWAPS:
        here = [key for key, name in assigned.items() if name == one]
        there = [key for key, name in assigned.items() if name == other]
        if here and there:
            assigned[here[0]], assigned[there[0]] = other, one

    if not NAME_THE_TALKS:
        assigned = {key: "Invited talk" for key in assigned}

    k = iter(keynotes)
    lines = ["# Generated by scripts/make_schedule.py — a first pass, not a considered",
             "# programme. Rearrange freely; once you edit this by hand, do not re-run it.",
             ""]
    for day_i, (title, rows) in enumerate(days):
        lines.append(f"- day: {title}")
        lines.append("  slots:")
        for row_i, (time, kind, what, _) in enumerate(rows):
            if kind == "keynote":
                named = next(k, None)
                what = named if (named and NAME_THE_TALKS) else "Keynote talk"
            elif kind == "talk":
                what = assigned[(day_i, row_i)]
            lines.append(f'    - time: "{time}"')
            lines.append(f"      kind: {kind}")
            lines.append(f'      what: "{what}"')

    (ROOT / "_data" / "schedule.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(keynotes)} keynotes and {len(talk_slots)} talk slots; "
          f"{gaps} left open at the end")


if __name__ == "__main__":
    main()
