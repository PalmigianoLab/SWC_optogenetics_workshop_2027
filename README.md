# Theory and Practice of Optogenetics: Function and Dynamics

Website for the workshop at the Sainsbury Wellcome Centre, UCL, 31 March – 2 April 2027.

A plain Jekyll site — no theme — so everything is in this repository.

## Editing without touching HTML

| What                                   | Where                                      |
| -------------------------------------- | ------------------------------------------ |
| Name, dates, venue, deadline, apply link | `_config.yml` (needs a server restart)     |
| The three topic cards                  | `_data/topics.yml`                         |
| FAQ                                    | `_data/faq.yml`                            |
| About text                             | `_includes/about.html`                     |
| Hero artwork                           | `assets/img/hero.svg` (three colours at the top) |

## People

`_data/keynotes.yml`, `_data/speakers.yml` and `_data/organizers.yml` are **generated**
from the planning spreadsheet — edit the sheet, not these files:

```sh
python3 scripts/people_from_sheet.py        # refresh from the sheet
python3 scripts/people_from_sheet.py --all  # also list who has not confirmed
```

Only people whose "Confirmed invite" column says yes are published, so nobody
appears before they have agreed. Photographs are mapped by name in that script,
each taken from the person's own institutional page.

Give a person a `bio:` and their card becomes clickable, opening a panel.

## Running it locally

```sh
chruby 3.3.5
bundle install
bundle exec jekyll serve      # http://127.0.0.1:4000
```
