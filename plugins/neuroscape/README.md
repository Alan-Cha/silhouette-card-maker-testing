# Neuroscape Plugin

This plugin reads a decklist, fetches the card image from [Neuroscape TCG](https://www.neuroscapetcg.com/), and puts the card images into the proper `game/` directories.

This plugin supports the `deckscape` and `deckplanet` formats. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is DeckPlanet (`deckplanet`).

Run the script.

```sh
python plugins/neuroscape/application/fetch.py game/decklist/deck.txt deckplanet
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {deckplanet}

Options:
  --help  Show this message and exit.
```

## Formats

### `deckplanet`

DeckPlanet format.

```
Name (Rotter's Radiant Mystic)
# Mainframe
1 RADIANT [GEN]
# Cyberdeck
3 SEER [GEN]
4 ASTRA, COSMIC KITTY [GEN]
3 LILITH, THE DARK MOON [GEN]
2 MOONSTONE DATASHARD [GEN]
3 DARKSTONE DATASHARD [GEN]
4 THE FOOL [GEN]
2 THE MAGICIAN [GEN]
2 THE HIGH PRIESTESS [GEN]
2 THE EMPRESS [GEN]
4 THE EMPEROR [GEN]
2 THE CHARIOT [GEN]
4 THE HERMIT [GEN]
4 THE TOWER [GEN]
4 THE STAR [GEN]
1 ZEN GARDEN [GEN]
2 AMETHYST DATASHARD [GEN]
2 B.O.B. [GEN]
2 THE GRID [GEN]
# RAM Deck
25 Basic Ram [GEN]
# Sideboard
2 LUNA, THE SACRED MOON [GEN]
2 ZEN GARDEN [GEN]
2 RIOT POLICE [GEN]
2 THE MAGICIAN [GEN]
2 TERMINATE [GEN]
2 SHORT CIRCUIT [GEN]
```

### `deckscape`

Deckscape format.

```
// Mainframe
1x Firestarter

// Cyberdeck (50)
1x The Grid
1x Delete
1x Nova, the White Rabbit
1x Hex, Codemancer
1x Redirect
1x Binary Blast
1x The Net
2x Black Hat
2x Fatal Error 75
2x Phantom OS
2x Phishing
2x Quantum Encryption
2x Memory Leak
3x Deep Diver
3x Cortex Crab
3x Overload Mk. II
3x Overload Mk. I
3x Digital Spectre
3x Coder
3x System Error
3x Tagger
3x Power Spike
4x Admin

// RAM (25)
25x Basic RAM
```