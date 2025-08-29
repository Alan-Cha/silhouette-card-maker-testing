# Elestrals Plugin

This plugin reads a deck id, fetches the deck and card images, and puts the card images into the proper `game/` directories.

This plugin supports the [Elestrals Play Network](https://play.elestrals.com/decks) format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Elestrals Play Network (`elestrals`).

Run the script.

```sh
python plugins/elestrals/fetch.py game/decklist/deck.txt elestrals
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {elestrals}

Options:
  --help  Show this message and exit.
```

## Formats

### `elestrals`

The format for ``Elestrals Play Network``.

```
6883b784bd9cf7315d565843
```
