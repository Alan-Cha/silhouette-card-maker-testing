# Arkham Horror LCG Plugin

This plugin reads a decklist, automatically fetches card art from [ArkhamDB](https://arkhamdb.com/) and puts them in the proper `game/` directories.

This plugin supports the **ArkhamDB JSON** decklist export and **ArkhamDB deck URLs**. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Export your deck from [ArkhamDB](https://arkhamdb.com) (**Export JSON** on any deck page) and save it into [game/decklist](../game/decklist/). In this example, the filename is `deck.json` and the decklist format is ArkhamDB JSON (`arkhamdb_json`).

Run the script.

```sh
python plugins/arkham_horror_lcg/fetch.py game/decklist/deck.json arkhamdb_json
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {arkhamdb_json|arkhamdb_url}

Options:
  --help  Show this message and exit.
```

### Examples

Use an ArkhamDB deck link saved into a text file instead of an exported JSON file.

```sh
python plugins/arkham_horror_lcg/fetch.py game/decklist/deck.txt arkhamdb_url
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/arkham_horror_lcg/fetch.py 'https://arkhamdb.com/deck/view/12345' arkhamdb_url
```

## Formats

### `arkhamdb_json`

[ArkhamDB](https://arkhamdb.com) deck export format. Export from any deck page using **Export JSON**.

```json
{
  "investigator_code": "01001",
  "slots": {
    "01006": 1,
    "01016": 1,
    "01086": 2
  }
}
```

The investigator is fetched automatically alongside the rest of the deck.

### `arkhamdb_url`

ArkhamDB URL format uses the full URL of a deck or published decklist from [ArkhamDB](https://arkhamdb.com).

```
https://arkhamdb.com/deck/view/12345
https://arkhamdb.com/decklist/view/12345
```

Published decklists (`/decklist/view/`) are always public. Personal decks (`/deck/view/`) are only reachable this way if their owner has enabled public sharing on that deck; otherwise the request will fail.

## Double-Sided Cards

Investigators and other double-sided cards (acts, agendas, and some player/encounter cards) automatically fetch both faces. The back is placed in [`game/double_sided`](../../game/double_sided/) under the same filename as the front, per [`create_pdf.py`](../../README.md#double-sided-cards)'s pairing convention.
