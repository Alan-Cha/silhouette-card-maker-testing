# Echoes of Astra Plugin

This plugin reads a decklist, fetches the card image from the [AstraBuilder](https://www.astra-builder.com/en), and puts the card images into the proper `game/` directories.

This plugin supports the `astra` format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is AstraBuilder (`astrabuilder`).

Run the script.

```sh
python plugins/echoes_of_astra/fetch.py game/decklist/deck.txt astrabuilder
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {astrabuilder}

Options:
  --help  Show this message and exit.
```

## Formats

### `astrabuilder`

AstraBuilder format utilizes the deck ID found at the end of the URL of a deck.

For example: https://www.astra-builder.com/en/create?deck=122

```
122
```