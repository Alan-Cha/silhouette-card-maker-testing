---
title: 'Grand Archive'
weight: 50
---

This plugin reads a decklist, fetches the card image from the [Grand Archive website](https://gatcg.com), and puts the card images into the proper `game/` directories.

This plugin supports the `omnideck` format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Omnideck (`omnideck`).

Run the script.

```sh
python plugins/grand_archive/fetch.py game/decklist/deck.txt omnideck
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {omnideck}

Options:
  --help  Show this message and exit.
```

## Formats

### `omnideck`

Omnideck format.
```
# Main Deck
3 Incapacitate
4 Sable Remnant
4 Slice and Dice
2 Aesan Protector
3 Blackmarket Broker
4 Dream Fairy
4 Fairy Whispers
4 Galewhisper Rogue
4 Reclaim
4 Shimmercloak Assassin
3 Stifling Trap
4 Surveil the Winds
3 Tempest Downfall
3 Veiling Breeze
4 Winbless Lookout
4 Windmill Engineer
3 Zephyr

# Material Deck
1 Spirit of Wind
1 Tristan, Underhanded
1 Tristan, Hired Blade
1 Assassin's Ripper
1 Bauble of Abundance
1 Blinding Orb
1 Curved Dagger
1 Poisoned Coating Oil
1 Poisoned Dagger
1 Smoke Bombs
1 Tariff Ring
1 Windwalker Boots
```