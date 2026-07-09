# Chrono Core TCG Plugin

This plugin reads a decklist, fetches the card image from [Sleeved](https://sleeved.gg/chrono-core), and puts the card images into the proper `game/` directories.

This plugin supports the `sleeved_url`, `text`, and `json` format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Text (`text`).

Run the script.

```sh
python plugins/chrono_core/application/fetch.py game/decklist/deck.txt text
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {sleeved_url|text|json}

Options:
  --help  Show this message and exit.
```

## Formats

### `text`

Text format uses the Text output from Sleeved.

```
// Starting Loadout
1 Basilisk Core V.1 (WNR01-002)
1 Basilisk Visor V1 (WNR01-009)
1 Basilisk Greaves V.1 (WNR01-010)
1 Basilisk Gauntlets V.1 (WNR01-013)
1 The Fang V.1 (WNR01-025)
1 Allura Nekris (WNR01-001)
// Main Deck
2 Temporal Spike V.1 (WNR01-022)
1 Temporal Spike V.1 (WNR01-027)
1 Basilisk Visor V.1 (WNR01-020)
3 Basilisk Greaves V.1 (WNR01-018)
3 Basilisk Gauntlets V.1 (WNR01-017)
3 Basilisk Visor V.1 (WNR01-014)
2 Basilisk Visor V.1 (WNR01-015)
3 Basilisk Greaves V.1 (WNR01-012)
3 Basilisk Gauntlets V.1 (WNR01-011)
1 The Fang V.1 (WNR01-028)
3 The Fang V.1 (WNR01-029)
3 All Consuming V.1 (WNR01-026)
3 Core Control (WNR01-098)
2 Disengage (SD01-029)
3 Core Override (WNR01-101)
3 Overcharge (WNR01-102)
1 All Consuming V.1 (WNR01-024)
2 All Consuming V.1 (WNR01-023)
1 Upgrade Protocol (WNR01-113)
2 Shield Drone (SD01-032)
1 Or Maybe Two (WNR01-109)
2 Orbital Devastation (SD01-033)
2 Memory Wipe (WNR01-116)
// Sideboard
2 Scry (WNR01-106)
1 Retribution (WNR01-103)
1 Temporal Spike V.1 (WNR01-022)
2 Temporal Spike V.1 (WNR01-027)
2 Maintenance Hangar (SD01-031)
2 Overwhelm (SD01-026)
```

### `json`

JSON format uses the JSON output from Sleeved.

```
{
  "source": "Exported from Sleeved",
  "zones": {
    "loadout": [
      "SD03-004",
      "WNR01-032",
      "WNR01-036",
      "SD03-002",
      "WNR01-021",
      "WNR01-003",
      "SD03-007"
    ],
    "main": [
      "WNR01-051",
      "WNR01-042",
      "SD01-032",
      "SD01-032",
      "SD01-032",
      "SD01-031",
      "SD01-031",
      "SD01-031",
      "SD01-027",
      "SD01-027",
      "SD01-027",
      "SD01-029",
      "SD01-029",
      "WNR01-116",
      "WNR01-116",
      "WNR01-116",
      "WNR01-113",
      "WNR01-113",
      "WNR01-109",
      "WNR01-109",
      "SD01-033",
      "SD01-033",
      "SD01-033",
      "WNR01-101",
      "WNR01-101",
      "WNR01-101",
      "SD01-028",
      "SD01-028",
      "SD01-028",
      "SD01-030",
      "SD01-030",
      "SD01-030",
      "WNR01-067",
      "WNR01-067",
      "SD01-012",
      "SD01-012",
      "SD01-012",
      "WNR01-034",
      "WNR01-034",
      "WNR01-033",
      "WNR01-033",
      "WNR01-037",
      "WNR01-037",
      "WNR01-040",
      "WNR01-040",
      "WNR01-041",
      "WNR01-041",
      "WNR01-029",
      "WNR01-029",
      "WNR01-029"
    ],
    "sideboard": [
      "WNR01-107",
      "WNR01-107",
      "SD01-029",
      "WNR01-098",
      "WNR01-098",
      "WNR01-098",
      "SD03-010",
      "WNR01-004",
      "WNR01-100",
      "WNR01-100"
    ]
  }
}
```

### `sleeved_url`

Sleeved URL format uses the full URL of a deck from Sleeved.

```
https://sleeved.gg/chrono-core/decks/6b4c41da-c5de-4cae-9aa6-ecc86d9d6960
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/chrono_core/application/fetch.py 'https://sleeved.gg/chrono-core/decks/6b4c41da-c5de-4cae-9aa6-ecc86d9d6960' sleeved_url
```