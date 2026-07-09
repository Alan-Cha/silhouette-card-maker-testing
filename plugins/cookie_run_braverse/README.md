# Cookie Run: Braverse Plugin

This plugin reads a decklist, fetches the card image from [Cookie Run TCG](https://play.cookieruntcg.com/), and puts the card images into the proper `game/` directories.

This plugin supports the `cookieruntcg_url` format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Cookie Run TCG URL (`cookieruntcg_url`).

Run the script.

```sh
python plugins/cookie_run_braverse/application/fetch.py game/decklist/deck.txt cookieruntcg_url
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {cookieruntcg_url}

Options:
  --help  Show this message and exit.
```

## Formats

### `cookieruntcg_url`

Cookie Run TCG URL format uses the full URL of a deck from Cookie Run TCG.

```
https://play.cookieruntcg.com/decks/69f16aa5962fc145572daa03
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/cookie_run_braverse/application/fetch.py 'https://play.cookieruntcg.com/decks/69f16aa5962fc145572daa03' cookieruntcg_url
```