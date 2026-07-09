# Echoes of Astra Plugin

This plugin reads a decklist, fetches the card image from [Echoes of Astra's Card Database](https://app.echoesofastra.com/cards-viewer), and puts the card images into the proper `game/` directories.

This plugin supports the `tts` and `text` formats. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Text (`text`).

Run the script.

```sh
python plugins/echoes_of_astra/application/fetch.py game/decklist/deck.txt text
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {tts|text}

Options:
  --help  Show this message and exit.
```

## Formats

### `tts`

Tabletop Simulator export of a deck from AstraBuilder.

```
[
  {
    "count": 3,
    "name": "Cadaver Supplier"
  },
  {
    "count": 2,
    "name": "Ebonblight Invoker"
  },
  {
    "count": 3,
    "name": "Guinea Pig"
  },
  {
    "count": 3,
    "name": "Jormun, Feldragon of Wyrmscar"
  },
  {
    "count": 3,
    "name": "Lucille, Blood Baroness"
  },
  {
    "count": 3,
    "name": "Noxhaven Researcher"
  },
  {
    "count": 2,
    "name": "Demonic Advance"
  },
  {
    "count": 3,
    "name": "Experimental Augment"
  },
  {
    "count": 3,
    "name": "Courier Drone"
  },
  {
    "count": 3,
    "name": "Imperial Skyfortress"
  },
  {
    "count": 3,
    "name": "Inquisition Drone"
  },
  {
    "count": 3,
    "name": "Lockdown Enforcer"
  },
  {
    "count": 2,
    "name": "Valeria, Dragoon Knight"
  },
  {
    "count": 2,
    "name": "Wingshield Transport"
  },
  {
    "count": 3,
    "name": "Airdrop"
  },
  {
    "count": 3,
    "name": "Void Warp"
  },
  {
    "count": 3,
    "name": "Freight Module"
  },
  {
    "count": 3,
    "name": "Radar Beacon"
  }
]
```

### `text`

Text export of a deck from AstraBuilder.

```
3 Cadaver Supplier
2 Ebonblight Invoker
3 Guinea Pig
3 Jormun, Feldragon of Wyrmscar
3 Lucille, Blood Baroness
3 Noxhaven Researcher
2 Demonic Advance
3 Experimental Augment
3 Courier Drone
3 Imperial Skyfortress
3 Inquisition Drone
3 Lockdown Enforcer
2 Valeria, Dragoon Knight
2 Wingshield Transport
3 Airdrop
3 Void Warp
3 Freight Module
3 Radar Beacon
```