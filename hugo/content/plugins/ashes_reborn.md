---
title: 'Ashes Reborn'
weight: 25
---

This plugin reads decklist URLs, retrieves the decklists, fetches the card images from either [Ashes](https://ashes.live/) or [AshesDB](https://ashesdb.plaidhatgames.com/), and puts the card images into the proper `game/` directories.

This plugin supports decklist exports from [Ashes](https://ashes.live/) and [AshesDB](https://ashesdb.plaidhatgames.com/). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Ashes (`ashes_share_url`).

Run the script.

```sh
python plugins/ashes_reborn/fetch.py game/decklist/deck.txt ashes_share_url
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH
                {ashes_share_url|ashesdb_share_url}

Options:
  --source [ashes|ashesdb]  The desired image source.  [default:
                            ashes]
  --help                    Show this message and exit.
```

## Formats

### `ashes_share_url`

[Ashes](https://ashes.live) format.

```
https://ashes.live/decks/share/57be4c41-6b6f-4770-8e30-b2fe9b9a6c72/
```

You can also use the share URL directly in the command line.

```sh
python plugins/ashes_reborn/fetch.py https://ashes.live/decks/share/57be4c41-6b6f-4770-8e30-b2fe9b9a6c72/ ashes_share_url
```

### `ashesdb_share_url`

[Ashes DB](https://ashesdb.plaidhatgames.com) format.

```
https://ashesdb.plaidhatgames.com/decks/share/0f8855d9-3c02-45e8-8458-366cbd755a04/
```

You can also use the share URL directly in the command line.

```sh
python plugins/ashes_reborn/fetch.py https://ashesdb.plaidhatgames.com/decks/share/0f8855d9-3c02-45e8-8458-366cbd755a04/ ashesdb_share_url
```