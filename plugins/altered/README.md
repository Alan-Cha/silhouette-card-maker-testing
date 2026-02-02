# Altered Plugin

This plugin reads a decklist, automatically fetches card art from [Altered](https://www.altered.gg/) and puts them in the proper `game/` directories.

This plugin supports decklist exports from [Ajordat](https://altered.ajordat.com/). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Ajordat (`ajordat`).

Run the script.

```sh
python plugins/altered/fetch.py game/decklist/deck.txt ajordat
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {ajordat}

Options:
  --help  Show this message and exit.
```

## Formats

### `ajordat`

Ajordat format.

```
1 ALT_COREKS_B_OR_01_C
3 ALT_ALIZE_B_MU_31_R2
2 ALT_ALIZE_B_OR_42_R1
2 ALT_ALIZE_B_OR_44_C
2 ALT_BISE_B_OR_49_C
3 ALT_BISE_B_OR_54_C
3 ALT_BISE_B_OR_59_C
2 ALT_CORE_B_LY_15_R2
2 ALT_CORE_B_OR_08_C
2 ALT_CORE_B_OR_09_C
1 ALT_CORE_B_OR_20_U_7022
2 ALT_CORE_B_OR_30_C
2 ALT_CORE_B_YZ_20_R2
1 ALT_COREKS_B_BR_09_U_4235
3 ALT_COREKS_B_OR_05_R1
2 ALT_COREKS_B_OR_14_C
3 ALT_COREKS_B_OR_16_R1
1 ALT_COREKS_B_OR_18_U_1071
3 ALT_COREKS_B_OR_24_C
```