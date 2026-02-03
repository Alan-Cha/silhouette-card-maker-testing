---
title: 'Echoes of Astra'
weight: 120
---

This plugin reads a decklist, fetches the card image from the [AstraBuilder](https://www.astra-builder.com/en), and puts the card images into the proper `game/` directories.

This plugin supports the `astrabuilder_url` format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugin directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is AstraBuilder URL (`astrabuilder_url`).

Run the script.

```sh
python plugins/echoes_of_astra/fetch.py game/decklist/deck.txt astrabuilder_url
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {astrabuilder_url}

Options:
  --help  Show this message and exit.
```

## Formats

### `astrabuilder_url`

AstraBuilder URL format uses the full URL of a deck from AstraBuilder.

```
https://www.astra-builder.com/en/create?deck=122
```

You can also use the URL directly in the command line. Note the single quotes around the URL.

```sh
python plugins/echoes_of_astra/fetch.py 'https://www.astra-builder.com/en/create?deck=122' astrabuilder_url
```
