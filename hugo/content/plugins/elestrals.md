---
title: 'Elestrals'
weight: 35
---

This plugin reads a decklist, fetches the card images, and puts the card images into the proper `game/` directories.

This plugin supports the [Elestrals Play Network](https://play.elestrals.com/decks) format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Elestrals Play Network (`elestrals`).

Run the script.

```sh
python plugins/elestrals/fetch.py game/decklist/deck.txt elestrals
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {tts|digimoncardio|digimoncarddev|digimonc
                ardapp|digimonmeta|untap}

Options:
  --help  Show this message and exit.
```

## Formats

### `elestrals`

The format for Elestrals Play Network.

```
6883b784bd9cf7315d565843
```

You can also use YDKE directly in the command line. Note the single quotes around the YDKE.

```sh
python plugins/elestrals/fetch.py 6883b784bd9cf7315d565843 elestrals