---
title: 'Flesh and Blood'
weight: 40
---

This plugin reads a decklist, fetches card art from [Fabrary](https://fabrary.net/), and puts the card images into the proper `game/` directories.

This plugin supports decklist exports from [Fabrary](https://fabrary.net/). To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Fabrary (`fabrary`).

Run the script.

```sh
python plugins/flesh_and_blood/fetch.py game/decklist/deck.txt fabrary
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {fabrary}

Options:
  --help  Show this message and exit.
```

## Formats

### `fabrary`

[Fabrary](https://fabrary.net) format.

```
Name: Sweden National Championship 2025 1st 🇸🇪
Hero: Cindra, Dracai of Retribution
Format: Classic Constructed

Arena cards
1x Blood Splattered Vest
1x Claw of Vynserakai
1x Dragonscaler Flight Path
1x Flick Knives
2x Kunai of Retribution
1x Mask of Momentum
1x Mask of the Pouncing Lynx
1x Tide Flippers

Deck cards
3x Ancestral Empowerment (red)
3x Art of the Dragon: Blood (red)
3x Blaze Headlong (red)
2x Blood Runs Deep (red)
3x Brand with Cinderclaw (red)
2x Breaking Point (red)
3x Cut Through (red)
3x Demonstrate Devotion (red)
3x Display Loyalty (red)
3x Fire Tenet: Strike First (red)
3x Hot on Their Heels (red)
2x Hunt the Hunter (red)
3x Ignite (red)
1x Imperial Seal of Command (red)
2x Lava Burst (red)
2x Oath of Loyalty (red)
3x Rally the Coast Guard (red)
3x Ravenous Rabble (red)
3x Rising Resentment (red)
3x Ronin Renegade (red)
3x Shelter from the Storm (red)
2x Sink Below (red)
2x Snatch (red)
2x Spreading Flames (red)
1x Wrath of Retribution (red)
1x Salt the Wound (yellow)
1x Tenacity (yellow)
2x Concealed Blade (blue)
1x Dragon Power (blue)
3x Throw Dagger (blue)

Made with ❤️ at the FaBrary
See the full deck @ https://fabrary.net/decks/01JZKYA2135MAN58K9VKKR4JYA
```