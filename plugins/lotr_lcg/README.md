# Lord of the Rings LCG Plugin

This plugin reads decklists, fellowships, and scenarios, fetches the card images from [RingsDB](https://ringsdb.com/) and [Hall of Beorn](https://hallofbeorn.com/), and puts the card images into the proper `game/` directories.

This plugin supports the `ringsdb`, `ringsdb_fellowship`, and `ringsdb_scenario` formats. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Before running the fetcher, add your local LOTR back scans to [plugins/lotr_lcg/assets](assets/README.md):

- `Player Card Back.jpg`
- `Encounter Card Back.jpg`

These files are intentionally kept out of git, so each user supplies their own local copies.

Put your deck reference into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is RingsDB (`ringsdb`).

Run the script.

```sh
python plugins/lotr_lcg/fetch.py game/decklist/deck.txt ringsdb
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

The plugin automatically copies your LOTR player or encounter back into `game/back/`.

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

RingsDB format accepts either:

- a published RingsDB decklist URL
- a RingsDB public API URL
- a bare published decklist ID

Example decklist URL:

```
https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0' ringsdb
```

You can also use a bare decklist ID.

```sh
python plugins/lotr_lcg/fetch.py 337 ringsdb
```

### `ringsdb_fellowship`

`ringsdb_fellowship` accepts either:

- a published RingsDB fellowship URL
- a bare published fellowship ID

Example fellowship URL:

```
https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship
```

```sh
python plugins/lotr_lcg/fetch.py 'https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship' ringsdb_fellowship
```

### `ringsdb_scenario`

`ringsdb_scenario` accepts either:

- a RingsDB scenario API URL
- a bare RingsDB scenario ID
- a Hall of Beorn scenario URL

Example scenario ID:

```sh
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario
```

Use a different scenario mode if needed:

```sh
python plugins/lotr_lcg/fetch.py 1 ringsdb_scenario --scenario-mode easy
```
