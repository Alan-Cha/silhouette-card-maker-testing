---
title: 'Riftbound'
weight: 100
---

This plugin reads a decklist, fetches the card image from either [Piltover Archive](https://piltoverarchive.com/) or [Riftmana](https://riftmana.com/), and puts the card images into the proper `game/` directories.

This plugin supports many decklist formats such as `tts`, `pixelborn`, and `piltover_archive`. To learn more, see [here](#formats).

> [!WARNING]
> `Pixelborn` will be shutdown August 7th, 2025 with Riot's announcement of their [Digital Tools Policy for Riftbound](https://developer.riotgames.com/docs/riftbound). As a result, the format itself may not receive any more support as an export option. However, the `Pixelborn` format will remain here, in the event that it still persists beyond that date.

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Tabletop Simulator (`tts`).

Run the script.

```sh
python plugins/riftbound/fetch.py game/decklist/deck.txt tts
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {tts|pixelborn|piltover_archive}

Options:
  --source [piltover_archive|riftmana]
                                  The desired image source.  [default:
                                  piltover_archive]
  --help                          Show this message and exit.
```

## Formats

### `tts`

Tabletop Simulator format.

```
OGN-265-1 OGN-246-1 OGN-245-1 OGN-245-1 OGN-245-1 OGN-095-1 OGN-095-1 OGN-095-1 OGN-213-1 OGN-213-1 OGN-213-1 OGN-266-1 OGN-266-1 OGN-266-1 OGN-216-1 OGN-216-1 OGN-216-1 OGN-209-1 OGN-209-1 OGN-209-1 OGN-096-1 OGN-096-1 OGN-096-1 OGN-211-1 OGN-211-1 OGN-211-1 OGN-218-1 OGN-218-1 OGN-218-1 OGN-208-1 OGN-208-1 OGN-208-1 OGN-239-1 OGN-239-1 OGN-239-1 OGN-233-1 OGN-233-1 OGN-233-1 OGN-234-1 OGN-234-1 OGN-234-1 OGN-289-1 OGN-294-1 OGN-284-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1 OGN-214-1
```

### `pixelborn`

Pixelborn format.

```
T0dOLTI2NS0xJE9HTi0yNDYtMSRPR04tMjQ1LTEkT0dOLTI0NS0xJE9HTi0yNDUtMSRPR04tMDk1LTEkT0dOLTA5NS0xJE9HTi0wOTUtMSRPR04tMjEzLTEkT0dOLTIxMy0xJE9HTi0yMTMtMSRPR04tMjY2LTEkT0dOLTI2Ni0xJE9HTi0yNjYtMSRPR04tMjE2LTEkT0dOLTIxNi0xJE9HTi0yMTYtMSRPR04tMjA5LTEkT0dOLTIwOS0xJE9HTi0yMDktMSRPR04tMDk2LTEkT0dOLTA5Ni0xJE9HTi0wOTYtMSRPR04tMjExLTEkT0dOLTIxMS0xJE9HTi0yMTEtMSRPR04tMjE4LTEkT0dOLTIxOC0xJE9HTi0yMTgtMSRPR04tMjA4LTEkT0dOLTIwOC0xJE9HTi0yMDgtMSRPR04tMjM5LTEkT0dOLTIzOS0xJE9HTi0yMzktMSRPR04tMjMzLTEkT0dOLTIzMy0xJE9HTi0yMzMtMSRPR04tMjM0LTEkT0dOLTIzNC0xJE9HTi0yMzQtMSRPR04tMjg5LTEkT0dOLTI5NC0xJE9HTi0yODQtMSRPR04tMjE0LTEkT0dOLTIxNC0xJE9HTi0yMTQtMSRPR04tMjE0LTEkT0dOLTIxNC0xJE9HTi0yMTQtMSRPR04tMjE0LTEkT0dOLTIxNC0xJE9HTi0yMTQtMSRPR04tMjE0LTEkT0dOLTIxNC0xJE9HTi0yMTQtMQ==
```

### `piltover_archive`

Piltover Archive format.

```
1 Viktor, Herald of the Arcane

1 Viktor, Leader

3 Seal of Unity
3 Stupefy
3 Hidden Blade
3 Siphon Power
3 Soaring Scout
3 Cull the Weak
3 Watchful Sentry
3 Faithful Manufactor
3 Vanguard Captain
3 Cruel Patron
3 Machine Evangel
3 Grand Strategem
3 Harnessed Dragon

1 Targon's Peak
1 Trifarian War Camp
1 Obelisk of Power

12 Order Rune
```