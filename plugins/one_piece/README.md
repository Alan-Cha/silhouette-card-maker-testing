# One Piece Plugin

This plugin reads a decklist, automatically fetches card art, and puts them in the proper `game/` directories.

This plugin supports many decklist formats such as `optcgsim` and `egman`. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is OPTCG Simulator (`optcgsim`).

Run the script.

```sh
python plugins/one_piece/fetch.py game/decklist/deck.txt optcgsim
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {optcgsim|egman}

Options:
  --help  Show this message and exit.
```

## Formats

### `optcgsim`

OPTCG Simulator format.

```
1xOP12-001
4xOP01-016
2xOP02-015
4xOP03-008
4xOP12-006
4xOP01-013
4xOP12-014
4xOP01-025
4xOP10-005
4xOP12-015
3xOP12-016
3xOP12-017
4xOP12-018
3xOP12-019
2xOP06-018
1xST21-017
```

### `egman`

Egman Events format.

```
4 OP01-016 Nami
4 OP03-008 Buggy
4 OP01-013 Sanji
4 OP10-005 Sanji
2 OP06-018 Gum-Gum King Kong Gatling
2 ST21-017 Gum-Gum Mole Pistol
4 OP12-006 Shakuyaku
2 OP12-009 Jinbe
4 OP12-014 Boa Hancock
4 OP12-015 Monkey.D.Luffy
4 OP12-016 To Never Doubt--That Is Power!
4 OP12-017 Color of Observation Haki
3 OP12-018 Color of the Supreme King Haki
3 OP12-019 Color of Arms Haki
2 OP01-025 Roronoa Zoro
1 OP12-001 Silvers Rayleigh
```