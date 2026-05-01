---
title: 'Lord of the Rings: Living Card Game'
weight: 85
---

This plugin is for **The Lord of the Rings: The Card Game** (LCG) by Fantasy Flight Games (2011). This cooperative Living Card Game should not be confused with the competitive **Lord of the Rings Trading Card Game** (TCG) by Decipher (2001-2007).

This plugin reads decklists, fellowships, and scenarios, automatically fetches the card images from [RingsDB](https://ringsdb.com/) and [Hall of Beorn](https://hallofbeorn.com/), and puts the card images into the proper `game/` directories.

This plugin supports the `ringsdb_url`, `ringsdb_fellowship_url`, and `ringsdb_scenario_url` formats. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugin directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

**Important:** Lord of the Rings: Living Card Game uses two different card backs:
- Player cards use the standard player card back
- Encounter/scenario cards use the encounter card back

You must manually place the appropriate back image in `game/back` before creating your PDF. The plugin fetches only the card fronts.

Put your deck reference into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is RingsDB (`ringsdb_url`).

Run the script.

```sh
python plugins/lotr_lcg/fetch.py game/decklist/deck.txt ringsdb_url
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

For scenarios, double-sided quest cards are placed into `game/double_sided/` automatically.

Landscape quest/scenario cards and their matching backs are rotated during fetch so they print with the correct sideways card orientation.

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {ringsdb_url|ringsdb_fellowship_url|ringsdb_scenario_url}

Options:
  --scenario_mode [normal|easy|nightmare]
                                  Encounter card counts to use when fetching
                                  RingsDB scenarios.  [default: normal]
  --help                          Show this message and exit.
```

## Formats

### `ringsdb_url`

RingsDB format accepts published player decklists. The plugin fetches all cards listed in the decklist, including heroes and player cards.

You can provide the decklist in three ways:

**Published RingsDB decklist URL:**
```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0' ringsdb_url
```

**RingsDB public API URL:**
```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/api/public/decklist/337.json' ringsdb_url
```

**Bare decklist ID:**
```sh
python plugins/lotr_lcg/fetch.py 337 ringsdb_url
```

You can also put the URL or ID in a text file and pass the file path instead.

### `ringsdb_fellowship_url`

RingsDB fellowship format accepts published fellowships, which are collections of multiple player decks designed to work together. The plugin fetches cards from all decks in the fellowship.

You can provide the fellowship in two ways:

**Published RingsDB fellowship URL:**
```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship' ringsdb_fellowship_url
```

**Bare fellowship ID:**
```sh
python plugins/lotr_lcg/fetch.py 7100 ringsdb_fellowship_url
```

You can also put the URL or ID in a text file and pass the file path instead.

### `ringsdb_scenario_url`

RingsDB scenario format accepts published scenarios/quests. The plugin fetches all encounter cards and quest cards needed to play the scenario. Quest cards with two sides are automatically placed in `game/double_sided/`.

You can provide the scenario in three ways:

**RingsDB scenario API URL:**
```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/api/public/scenario/1.json' ringsdb_scenario_url
```

**Bare RingsDB scenario ID:**
```sh
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario_url
```

**Hall of Beorn scenario URL:**
```sh
python plugins/lotr_lcg/fetch.py 'https://hallofbeorn.com/LotR/Scenarios/passage-through-mirkwood' ringsdb_scenario_url
```

You can also put the URL or ID in a text file and pass the file path instead.

You can specify the difficulty mode (encounter card quantities vary by mode):

```sh
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario_url --scenario_mode easy
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario_url --scenario_mode nightmare
```
