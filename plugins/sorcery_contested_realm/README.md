# Sorcery: Contested Realm Plugin

This plugin reads a decklist, automatically fetches card art from [Curiosa](https://curiosa.io/) and puts them in the proper `game/` directories.

This plugin supports decklist exports from [Curiosa](https://curiosa.io/). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Curiosa (`curiosa_url`).

Run the script.

```sh
python plugins/sorcery_contested_realm/application/fetch.py game/decklist/deck.txt curiosa_url
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {curiosa_url}

Options:
  --help  Show this message and exit.
```

## Formats

### `curiosa_url`

Curiosa URL format uses the full URL of a deck from [Curiosa](https://curiosa.io).

```
https://curiosa.io/decks/cme5x329q00k9jo04ouuycsek
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/sorcery_contested_realm/fetch.py 'https://curiosa.io/decks/cme5x329q00k9jo04ouuycsek' curiosa_url
```