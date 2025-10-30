# Pokemon Plugin

This plugin reads a decklist, automatically fetches card art from [Limitless](https://limitlesstcg.com/) and puts them in the proper `game/` directories.

This plugin supports decklist exports from [Limitless](https://limitlesstcg.com/) for both Pokemon TCG and Pokemon Pocket. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Limitless (`limitless`).

Run the script.

```sh
python plugins/pokemon/fetch.py game/decklist/deck.txt limitless
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {limitless}

Options:
  --help  Show this message and exit.
```

## Format

### `limitless`

Limitless format.

```
Pokémon: 13
3 Charcadet SSP 32
1 Charcadet PAR 26
3 Ceruledge ex SSP 36
2 Solrock MEG 75
2 Lunatone MEG 74
1 Squawkabilly ex PAL 169
1 Fezandipiti ex SFA 38

Trainer: 27
3 Carmine TWM 145
3 Boss's Orders MEG 114
2 Professor's Research JTG 155
1 Briar SCR 132
1 Professor Turo's Scenario PAR 171
4 Ultra Ball MEG 131
4 Nest Ball SVI 181
3 Night Stretcher SFA 61
2 Earthen Vessel PAR 163
2 Fighting Gong MEG 116
1 Pal Pad SVI 182
1 Jamming Tower TWM 153

Energy: 20
10 Fighting Energy SVE 22
6 Fire Energy SVE 18
2 Jet Energy PAL 190
1 Mist Energy TEF 161
1 Legacy Energy TWM 167
```
