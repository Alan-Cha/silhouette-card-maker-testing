---
title: 'Gundam'
weight: 60
---

This plugin reads a decklist and puts the card images into the proper `game/` directories.

This plugin supports many decklist formats such as, `deckplanet`, `limitless`, `egman`, and `exburst`. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is DeckPlanet (`deckplanet`).

Run the script.

```sh
python plugins/gundam/fetch.py game/decklist/deck.txt deckplanet
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {deckplanet|limitless|egman|exburst}

Options:
  --help  Show this message and exit.
```

## Formats

### `deckplanet`

DeckPlanet format.

```
2 Guntank [GD01-008]
4 Gundam (MA Form) [ST01-002]
4 Demi Trainer [ST01-008]
4 Amuro Ray [ST01-010]
1 Gundam [ST01-001]
2 Kai's Resolve [ST01-013]
1 Suletta Mercury [ST01-011]
4 White Base [ST01-015]
2 Archangel [ST04-015]
2 Aile Strike Gundam [ST04-001]
4 Kira Yamato [ST04-010]
3 Strike Gundam [ST04-002]
2 Guncannon [GD01-004]
2 Darilbalde [GD01-075]
1 Perfect Strike Gundam [GD01-068]
2 Launcher Strike Gundam [GD01-072]
1 Intercept Orders [GD01-099]
2 A Show of Resolve [GD01-100]
2 The Witch and the Bride [GD01-117]
1 Naval Bombardment [GD01-120]
4 Overflowing Affection [GD01-118]
```

### `limitless`

Limitless TCG format.

```
4 Dopp GD01-039
4 Zaku Ⅰ ST03-007
1 Pisces GD01-021
4 Zaku Ⅱ ST03-008
4 Zaku Ⅱ GD01-035
3 Guntank GD01-008
4 Char's Zaku Ⅱ ST03-006
4 Char's Zaku Ⅱ GD01-026
2 G-Fighter GD01-009
2 Gouf ST03-009
4 Char's Gelgoog GD01-023
3 Gundam ST01-001
4 Char Aznable ST03-011
4 Amuro Ray ST01-010
3 Falmel ST03-016
```

### `egman`

Egman Events format.

```
4 GD01-039 Dopp
4 ST03-007 Zaku I | MS-05
4 GD01-035 Zaku II | MS-06
4 ST03-006 Char's Zaku II | MS-06S
4 GD01-026 Char's Zaku II | MS-065
4 ST03-008 Zaku II | MS-06
1 GD01-021 Pisces | OZ-09MMS
3 GD01-008 Guntank | RX-75
2 GD01-009 G-Fighter
2 ST03-009 Gouf | MS-078
4 GD01-023 Char's Gelgoog | MS-14S
3 ST01-001 Gundam | RX-78-2
4 ST03-011 Char Aznable
4 ST01-010 Amuro Ray
3 ST03-016 Falmel
```

### `exburst`

ExBurst format.

```
4 x ST04-008
4 x ST01-005
4 x GD01-059
4 x GD01-018
4 x ST01-001
3 x GD01-044
3 x GD01-003
2 x GD01-047
4 x ST01-010
4 x GD01-093
3 x ST04-016
1 x ST01-015
2 x GD01-112
2 x GD01-111
2 x ST03-013
4 x GD01-100
```