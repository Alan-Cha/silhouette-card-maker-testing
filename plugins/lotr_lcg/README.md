# Lord of the Rings: Living Card Game Plugin

This plugin reads decklists, fellowships, and scenarios, automatically fetches the card images from [RingsDB](https://ringsdb.com/) and [Hall of Beorn](https://hallofbeorn.com/), and puts the card images into the proper `game/` directories.

This plugin supports the `ringsdb`, `ringsdb_fellowship`, and `ringsdb_scenario` formats. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

**Important:** Lord of the Rings: Living Card Game uses two different card backs:
- Player cards use the standard player card back
- Encounter/scenario cards use the encounter card back

You must manually place the appropriate back image in [game/back/](../../game/back/) before creating your PDF. The plugin fetches only the card fronts.

Put your deck reference into a text file in [game/decklist/](../../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is RingsDB (`ringsdb`).

Run the script.

```sh
python plugins/lotr_lcg/fetch.py game/decklist/deck.txt ringsdb
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

For scenarios, double-sided quest cards are placed into `game/double_sided/` automatically.

Landscape quest/scenario cards and their matching backs are rotated during fetch so they print with the correct sideways card orientation.

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {ringsdb|ringsdb_fellowship|ringsdb_scenario}

Options:
  --scenario-mode [normal|easy|nightmare]
                                  Encounter card counts to use when fetching
                                  RingsDB scenarios.  [default: normal]
  --help                          Show this message and exit.
```

## Formats

### `ringsdb`

RingsDB format accepts published player decklists. The plugin fetches all cards listed in the decklist, including heroes and player cards.

You can provide the decklist in three ways:

- a published RingsDB decklist URL
- a RingsDB public API URL  
- a bare published decklist ID

**Example decklist structure** (this is what RingsDB provides via their API):

```
Heroes:
- Legolas (01005) x1
- Thalin (01006) x1
- Éowyn (01007) x1

Player Cards:
- Gondorian Spearman (01029) x3
- Horseback Archer (01030) x2
- Veteran Axehand (01031) x1
- Blade of Gondolin (01032) x3
- Horn of Gondor (01034) x2
- The Favor of the Lady (01035) x2
- Stand and Fight (01042) x2
- Dwarven Tomb (01045) x2
- Gandalf (01046) x2
- Gléowine (01048) x2
- Northern Tracker (01050) x2
- Snowbourn Scout (01051) x3
- Faramir (01053) x1
- Hasty Stroke (01057) x1
- Forest Snare (01073) x1
```

**Usage:**

Put the decklist URL or ID into a text file:

```
https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0
```

Then run:

```sh
python plugins/lotr_lcg/fetch.py game/decklist/deck.txt ringsdb
```

You can also use the URL or ID directly on the command line:

```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0' ringsdb
```

Or use a bare decklist ID:

```sh
python plugins/lotr_lcg/fetch.py 337 ringsdb
```

### `ringsdb_fellowship`

RingsDB fellowship format accepts published fellowships, which are collections of multiple player decks designed to work together. The plugin fetches cards from all decks in the fellowship.

You can provide the fellowship in two ways:

- a published RingsDB fellowship URL
- a bare published fellowship ID

**Example fellowship structure:**

```
Fellowship: Beginner Mono-Sphere Fellowship

Deck 1: Leadership Deck
  Heroes: Aragorn, Denethor
  Cards: Steward of Gondor, Faramir, Snowbourn Scout, ...

Deck 2: Tactics Deck
  Heroes: Legolas, Gimli
  Cards: Quick Strike, Blade of Gondolin, Veteran Axehand, ...

Deck 3: Spirit Deck
  Heroes: Éowyn, Eleanor
  Cards: The Galadhrim's Greeting, A Test of Will, Unexpected Courage, ...
```

**Usage:**

```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship' ringsdb_fellowship
```

Or use a bare fellowship ID:

```sh
python plugins/lotr_lcg/fetch.py 7100 ringsdb_fellowship
```

### `ringsdb_scenario`

RingsDB scenario format accepts published scenarios/quests. The plugin fetches all encounter cards and quest cards needed to play the scenario. Quest cards with two sides are automatically placed in `game/double_sided/`.

You can provide the scenario in three ways:

- a RingsDB scenario API URL
- a bare RingsDB scenario ID
- a Hall of Beorn scenario URL

**Example scenario structure:**

```
Scenario: Passage Through Mirkwood

Quest Cards:
- Flies and Spiders (01085) - Quest Stage 1A/1B (double-sided)
- A Fork in the Road (01086) - Quest Stage 2A/2B (double-sided)  
- A Chosen Path (01087) - Quest Stage 3A/3B (double-sided)

Encounter Cards:
- Ungoliant's Spawn (01080) x1
- Hummerhorns (01081) x2
- Dol Guldur Orcs (01082) x3
- East Bight Patrol (01083) x3
- Eyes of the Forest (01084) x2
- Forest Spider (01089) x2
- Mountains of Mirkwood (01093) x3
- Necromancer's Pass (01094) x2
- Old Forest Road (01095) x2
```

**Usage:**

Put the scenario URL or ID into a text file:

```
1
```

Then run:

```sh
python plugins/lotr_lcg/fetch.py game/decklist/scenario.txt ringsdb_scenario
```

Or use directly on the command line:

```sh
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario
```

You can specify the difficulty mode (encounter card quantities vary by mode):

```sh
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario --scenario-mode easy
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario --scenario-mode nightmare
```

Hall of Beorn URLs are also supported:

```sh
python plugins/lotr_lcg/fetch.py 'https://hallofbeorn.com/LotR/Scenarios/passage-through-mirkwood' ringsdb_scenario
```
