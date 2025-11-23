---
title: 'Sorcery: Contested Realm'
weight: 120
---

This plugin reads a decklist, automatically fetches card art from [Curiosa](https://curiosa.io/) and puts them in the proper `game/` directories.

This plugin supports decklist exports from [Curiosa](https://curiosa.io/). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugin directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Curiosa (`curiosa`).

Run the script.

```sh
python plugins/sorcery_contested_realm/fetch.py game/decklist/deck.txt curiosa
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {curiosa}

Options:
  --help  Show this message and exit.
```

## Format

### `curiosa`

Curiosa format.

```
cme5x329q00k9jo04ouuycsek
```
