# Cyberpunk 2077 Plugin

This plugin reads a decklist, fetches the card image from [Cyberpunk 2077 TCG](https://cyberpunktcg.com/cards), and puts the card images into the proper `game/` directories.

This plugin supports the `limitless` format. To learn more, see [here](#formats).

> [!WARNING]
> This plugin may have issues since some cards are no longer present on the Cyberpunk website. When this happens, you can add the card's image to the plugin's cache to skip retrieval attempts.

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Limitless (`limitless`).

Run the script.

```sh
python plugins/cyberpunk/application/fetch.py game/decklist/deck.txt limitless
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {limitless}

Options:
  --help  Show this message and exit.
```

## Formats

### `limitless`

Limitless format uses the Limitless output from ExBurst.

```
// Main Deck
3 Mantis Blades A019
2 Satori - Sword of Saburo A020
3 Industrial Assembly A021
3 Corporate Surveillance A025
3 Corpo Security A016
2 Ruthless Lowlife A008
2 Sandevistan A024
3 Swordwise Huscle A009
3 Emergency Atlus A017
2 Goro Takemura - Losing His Way A018
1 Armored Minotaur A007
1 Yorinobu Arasaka - Embracing Destruction A001
1 Goro Takemura - Hands Unclean A004
1 Saburo Arasaka - Stubborn Patriach A005
```