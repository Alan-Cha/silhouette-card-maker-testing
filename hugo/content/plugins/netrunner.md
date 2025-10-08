---
title: 'Netrunner'
weight: 80
---

This plugin reads a decklist, fetches the card images from [NRO Proxy](https://proxy.nro.run/), and puts the card images into the proper `game/` directories.

This plugin supports many decklist formats such as `text`, `bbcode`, `markdown`, `plain_text`, and `jinteki`. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is text (`text`).

Run the script.

```sh
python plugins/netrunner/fetch.py game/decklist/deck.txt text
```

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {text|bbcode|markdown|plain_text|jinteki}

Options:
  --help  Show this message and exit.
```

## Formats

### `text`

```
-i-m-in-love-with-the-auco-by-r-e-genasis-1st-spb-mc-
AU Co.: The Gold Standard in Clones (Elevation)

Agenda (11)
1x Longevity Serum (System Gateway)
2x Regenesis (Midnight Sun)
3x Hybrid Release (Parhelion)
3x Fujii Asset Retrieval (The Automata Initiative)
2x Sericulture Expansion (Elevation)

Asset (13)
2x Spin Doctor (System Gateway) ••
3x Moon Pool (Midnight Sun)
3x Cohort Guidance Program (Rebellion Without Rehearsal)
2x Humanoid Resources (Elevation) ••••
3x Phật Gioan Baotixita (Elevation)

Upgrade (3)
1x Manegarm Skunkworks (System Gateway) •••
1x Anoetic Void (System Gateway)
1x Mavirus (Midnight Sun)

Operation (9)
3x Hansei Review (System Gateway)
3x Hedge Fund (System Gateway)
3x Petty Cash (Elevation)

Barrier (5)
2x Tatu-Bola (The Automata Initiative)
3x Boto (Rebellion Without Rehearsal)

Code Gate (4)
3x Scatter Field (Elevation) ••••• •
1x Flyswatter (Elevation)

Sentry (4)
2x Saisentan (Downfall)
2x Anemone (Midnight Sun)

15 influence spent (max 15, available 0)
20 agenda points (between 20 and 21)
49 cards (min 45)
Cards up to Elevation
```

### `bbcode`

bbCode format.

```
[b]"I'm in Love with the AuCo" by R.E. Genasis (1st @ SPb MC)[/b]

[url=https://netrunnerdb.com/en/card/35046]AU Co.: The Gold Standard in Clones[/url] (Elevation)

[b]Agenda (11)[/b]
3x [url=https://netrunnerdb.com/en/card/34040]Fujii Asset Retrieval[/url] [i](The Automata Initiative)[/i]
3x [url=https://netrunnerdb.com/en/card/33105]Hybrid Release[/url] [i](Parhelion)[/i]
1x [url=https://netrunnerdb.com/en/card/30044]Longevity Serum[/url] [i](System Gateway)[/i]
2x [url=https://netrunnerdb.com/en/card/33040]Regenesis[/url] [i](Midnight Sun)[/i]
2x [url=https://netrunnerdb.com/en/card/35049]Sericulture Expansion[/url] [i](Elevation)[/i]

[b]Asset (13)[/b]
3x [url=https://netrunnerdb.com/en/card/34108]Cohort Guidance Program[/url] [i](Rebellion Without Rehearsal)[/i]
2x [url=https://netrunnerdb.com/en/card/35039]Humanoid Resources[/url] [i](Elevation)[/i] [color=#8A2BE2]●●●●[/color]
3x [url=https://netrunnerdb.com/en/card/33042]Moon Pool[/url] [i](Midnight Sun)[/i]
3x [url=https://netrunnerdb.com/en/card/35051]Phật Gioan Baotixita[/url] [i](Elevation)[/i]
2x [url=https://netrunnerdb.com/en/card/30053]Spin Doctor[/url] [i](System Gateway)[/i] [color=#FF8C00]●●[/color]

[b]Operation (9)[/b]
3x [url=https://netrunnerdb.com/en/card/30048]Hansei Review[/url] [i](System Gateway)[/i]
3x [url=https://netrunnerdb.com/en/card/30075]Hedge Fund[/url] [i](System Gateway)[/i]
3x [url=https://netrunnerdb.com/en/card/35081]Petty Cash[/url] [i](Elevation)[/i]

[b]Upgrade (3)[/b]
1x [url=https://netrunnerdb.com/en/card/30050]Anoetic Void[/url] [i](System Gateway)[/i]
1x [url=https://netrunnerdb.com/en/card/30042]Manegarm Skunkworks[/url] [i](System Gateway)[/i] [color=#8A2BE2]●●●[/color]
1x [url=https://netrunnerdb.com/en/card/33047]Mavirus[/url] [i](Midnight Sun)[/i]

[b]Barrier (5)[/b]
3x [url=https://netrunnerdb.com/en/card/34109]Boto[/url] [i](Rebellion Without Rehearsal)[/i]
2x [url=https://netrunnerdb.com/en/card/34044]Tatu-Bola[/url] [i](The Automata Initiative)[/i]

[b]Code Gate (4)[/b]
1x [url=https://netrunnerdb.com/en/card/35079]Flyswatter[/url] [i](Elevation)[/i]
3x [url=https://netrunnerdb.com/en/card/35042]Scatter Field[/url] [i](Elevation)[/i] [color=#8A2BE2]●●●●● ●[/color]

[b]Sentry (4)[/b]
2x [url=https://netrunnerdb.com/en/card/33043]Anemone[/url] [i](Midnight Sun)[/i]
2x [url=https://netrunnerdb.com/en/card/26044]Saisentan[/url] [i](Downfall)[/i]
15 influence spent (max 15, available 0)
20 agenda points (between 20 and 21)
49 cards (min 45)
Cards up to Elevation

Decklist [url=https://netrunnerdb.com/en/decklist/1cc34350-4dfe-4d61-a87b-c1f33da2827d/-i-m-in-love-with-the-auco-by-r-e-genasis-1st-spb-mc-]published on NetrunnerDB[/url].
```

### `markdown`

Markdown (Reddit) format.

```
## "I'm in Love with the AuCo" by R.E. Genasis (1st @ SPb MC)

[AU Co.: The Gold Standard in Clones](https://netrunnerdb.com/en/card/35046) _(Elevation)_

###Agenda (11)
* 3x [Fujii Asset Retrieval](https://netrunnerdb.com/en/card/34040) _(The Automata Initiative)_
* 3x [Hybrid Release](https://netrunnerdb.com/en/card/33105) _(Parhelion)_
* 1x [Longevity Serum](https://netrunnerdb.com/en/card/30044) _(System Gateway)_
* 2x [Regenesis](https://netrunnerdb.com/en/card/33040) _(Midnight Sun)_
* 2x [Sericulture Expansion](https://netrunnerdb.com/en/card/35049) _(Elevation)_

###Asset (13)
* 3x [Cohort Guidance Program](https://netrunnerdb.com/en/card/34108) _(Rebellion Without Rehearsal)_
* 2x [Humanoid Resources](https://netrunnerdb.com/en/card/35039) _(Elevation)_ ●●●●
* 3x [Moon Pool](https://netrunnerdb.com/en/card/33042) _(Midnight Sun)_
* 3x [Phật Gioan Baotixita](https://netrunnerdb.com/en/card/35051) _(Elevation)_
* 2x [Spin Doctor](https://netrunnerdb.com/en/card/30053) _(System Gateway)_ ●●

###Operation (9)
* 3x [Hansei Review](https://netrunnerdb.com/en/card/30048) _(System Gateway)_
* 3x [Hedge Fund](https://netrunnerdb.com/en/card/30075) _(System Gateway)_
* 3x [Petty Cash](https://netrunnerdb.com/en/card/35081) _(Elevation)_

###Upgrade (3)
* 1x [Anoetic Void](https://netrunnerdb.com/en/card/30050) _(System Gateway)_
* 1x [Manegarm Skunkworks](https://netrunnerdb.com/en/card/30042) _(System Gateway)_ ●●●
* 1x [Mavirus](https://netrunnerdb.com/en/card/33047) _(Midnight Sun)_

###Barrier (5)
* 3x [Boto](https://netrunnerdb.com/en/card/34109) _(Rebellion Without Rehearsal)_
* 2x [Tatu-Bola](https://netrunnerdb.com/en/card/34044) _(The Automata Initiative)_

###Code Gate (4)
* 1x [Flyswatter](https://netrunnerdb.com/en/card/35079) _(Elevation)_
* 3x [Scatter Field](https://netrunnerdb.com/en/card/35042) _(Elevation)_ ●●●●● ●

###Sentry (4)
* 2x [Anemone](https://netrunnerdb.com/en/card/33043) _(Midnight Sun)_
* 2x [Saisentan](https://netrunnerdb.com/en/card/26044) _(Downfall)_

15 influence spent (max 15, available 0)
20 agenda points (between 20 and 21)
49 cards (min 45)
Cards up to Elevation

Decklist [published on NetrunnerDB](https://netrunnerdb.com/en/decklist/1cc34350-4dfe-4d61-a87b-c1f33da2827d/-i-m-in-love-with-the-auco-by-r-e-genasis-1st-spb-mc-).
```

### `plain_text`

```
"I'm in Love with the AuCo" by R.E. Genasis (1st @ SPb MC)

AU Co.: The Gold Standard in Clones

Agenda (11)
3x Fujii Asset Retrieval
3x Hybrid Release
1x Longevity Serum
2x Regenesis
2x Sericulture Expansion

Asset (13)
3x Cohort Guidance Program
2x Humanoid Resources ●●●●
3x Moon Pool
3x Phật Gioan Baotixita
2x Spin Doctor ●●

Operation (9)
3x Hansei Review
3x Hedge Fund
3x Petty Cash

Upgrade (3)
1x Anoetic Void
1x Manegarm Skunkworks ●●●
1x Mavirus

Barrier (5)
3x Boto
2x Tatu-Bola

Code Gate (4)
1x Flyswatter
3x Scatter Field ●●●●● ●

Sentry (4)
2x Anemone
2x Saisentan

15 influence spent (max 15, available 0)
20 agenda points (between 20 and 21)
49 cards (min 45)
Cards up to Elevation

Decklist published on https://netrunnerdb.com.
```

### `jinteki`

Jinteki format.

```
3 Fujii Asset Retrieval
3 Hybrid Release
1 Longevity Serum
2 Regenesis
2 Sericulture Expansion
3 Cohort Guidance Program
2 Humanoid Resources
3 Moon Pool
3 Phật Gioan Baotixita
2 Spin Doctor
3 Hansei Review
3 Hedge Fund
3 Petty Cash
1 Anoetic Void
1 Manegarm Skunkworks
1 Mavirus
3 Boto
2 Tatu-Bola
1 Flyswatter
3 Scatter Field
2 Anemone
2 Saisentan
```