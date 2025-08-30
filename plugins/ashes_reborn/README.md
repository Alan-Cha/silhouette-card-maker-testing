# Ashes Reborn Plugin

This plugin reads decklist URLs, retrieves the decklists, fetches the card images, and puts the card images into the proper `game/` directories.

This plugin supports decklist exports from [Ashes](https://ashes.live/). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Ashes (`ashes`).

Run the script.

```sh
python plugins/ashes_reborn/fetch.py game/decklist/deck.txt ashes
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {ashes}

Options:
  --help  Show this message and exit.
```

## Formats

### `ashes`

The format for ``Ashes``.

```
https://ashes.live/decks/share/57be4c41-6b6f-4770-8e30-b2fe9b9a6c72/
```
