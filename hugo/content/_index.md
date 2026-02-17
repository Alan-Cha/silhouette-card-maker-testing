---
title: 'Silhouette Card Maker'
cascade:
  type: docs
---

![](/images/display.jpg)

Ever wanted to make your own custom card game but without the hassle of a craft knife, a rotary cutter, or a paper guillotine? How about making your own proxies to playtest your favorite TCG?

You can do it all with the press of a button and a cutting machine! And I can show you how!

If this is your first time here, check out the [tutorial]({{% ref "tutorial/" %}})! Please join our [Discord server](https://discord.gg/jhsKmAgbXc) too!

## Demo

Watch me cut **104 cards in 26 minutes** without breaking a sweat!

{{< youtube RVHtqsRW8t8 >}}

## Purpose

The purpose of this repo is to enable you to use a Silhouette cutting machine to create card games and proxies. Proxies are only intended to be used for casual play and playtesting.

Proxies should be easily identifiable as proxies. You may not use this repo to create counterfeit cards to decieve people or to play in sanctioned tournaments. You are only permitted to sell cards if you are the full privileged copyright holder.

## Contents

* [code repository](https://github.com/Alan-Cha/silhouette-card-maker)
* [tutorial]({{% ref "tutorial/" %}})
* [supply list]({{% ref "tutorial/supplies.md" %}})
* [create_pdf.py]({{% ref "docs/create.md" %}}), a script for laying out your cards in a PDF
* [offset_pdf.py]({{% ref "docs/offset.md" %}}), a script for adding an offset to your PDF
* [cutting_templates/](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/cutting_templates), a directory containing Silhoutte Studio cutting templates
* [calibration/](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/calibration), a directory containing offset calibration sheets
* [examples/](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/examples), a directory containing sample games
* [plugins/]({{% ref "plugins/" %}}), a directory containing scripts for streamlining card image acquisition


## Supported Sizes

The most common card sizes for games are:
* `standard`, for standard TCG cards
* `poker`
* `bridge`

Other notable card sizes include:
* `business`
* `euro_business`
* `credit`
* `photo`, for K-pop photocards

The table below shows all possible paper and card size combinations and the layout of the cards.

| Size | `letter` | `tabloid` | `a4` | `a3` | `arch_b` |
|---|---|---|---|---|---|
| `bridge` | 4x2 (8) | 4x4 (16) | 4x2 (8) | 6x3 (18) | 7x3 (21) |
| `bridge_square` | 3x4 (12) | 4x7 (28) | 3x4 (12) | 4x6 (24) | 4x7 (28) |
| `business` | 2x5 (10) | 4x5 (20) | 2x5 (10) | 3x7 (21) | 3x8 (24) |
| `credit` | 2x4 (8) | 4x4 (16) | 2x5 (10) | 3x7 (21) | 3x7 (21) |
| `domino` | 5x2 (10) | 5x4 (20) | 5x2 (10) | 8x3 (24) | 9x3 (27) |
| `domino_square` | 4x5 (20) | 5x9 (45) | 4x5 (20) | 6x8 (48) | 6x9 (54) |
| `euro_business` | 3x3 (9) | 3x7 (21) | 3x3 (9) | 3x7 (21) | 3x7 (21) |
| `euro_mini` | 4x3 (12) | 9x3 (27) | 6x2 (12) | 8x4 (32) | 9x4 (36) |
| `euro_poker` | 4x2 (8) | 4x4 (16) | 4x2 (8) | 4x4 (16) | 6x3 (18) |
| `japanese` | 4x2 (8) | 4x4 (16) | 4x2 (8) | 6x3 (18) | 7x3 (21) |
| `jumbo` | 2x1 (2) | 4x1 (4) | 3x1 (3) | 3x2 (6) | 4x2 (8) |
| `micro` | 7x4 (28) | 7x9 (63) | 5x6 (30) | 11x6 (66) | 12x6 (72) |
| `mini` | 5x3 (15) | 8x4 (32) | 4x4 (16) | 8x4 (32) | 9x4 (36) |
| `photo` | 3x3 (9) | 7x3 (21) | 3x3 (9) | 7x3 (21) | 7x3 (21) |
| `poker` | 4x2 (8) | 4x4 (16) | 4x2 (8) | 4x4 (16) | 6x3 (18) |
| `standard` | 4x2 (8) | 4x4 (16) | 4x2 (8) | 4x4 (16) | 6x3 (18) |
| `standard_double` | 2x2 (4) | 4x2 (8) | 2x2 (4) | 3x3 (9) | 3x3 (9) |
| `tarot` | 2x2 (4) | 5x2 (10) | 2x2 (4) | 5x2 (10) | 4x3 (12) |

The table below shows each card size, sorted by size.

| Card size | Inches | Millimeters | Aspect Ratio | Notes |
| --- | --- | --- | --- | --- |
| `jumbo` | **3.5 x 5.5** | 88.9 x 139.7 | 0.6364 | |
| `standard_double` | 3.46 x 4.96 | **88 x 126** | 0.6984 | {{< renderhtml `<strong>Magic: the Gathering</strong> oversized <ul><li>Planechase</strong></li> <li>Archenemy</strong></li> <li>Commander</strong></li></ui>` >}} |
| `tarot` | **2.75 x 4.75** | 69.85 x 120.65 | 0.5789 | |
| `poker` | **2.5 x 3.5** | 63.5 x 88.9 | 0.7143 | |
| `bridge` | **2.25 x 3.5** | 57.15 x 88.9 | 0.6429 | |
| `business` | **2 x 3.5** | 50.8 x 88.9 | 0.5714 | Business cards |
| `domino` | **1.75 x 3.5** | 44.45 x 88.9 | 0.5000 | |
| `euro_poker` | 2.48 x 3.46 | **63 x 88** | 0.7159 | |
| `standard` | 2.48 x 3.46 | **63 x 88** | 0.7159 | {{< renderhtml `Standard TCG cards <ul><li><strong>Magic: the Gathering</strong></li><li><strong>Pokémon</strong></li><li><strong>Lorcana</strong></li><li><strong>One Piece</strong></li><li><strong>Riftbound</strong></li></ui>` >}} |
| `japanese` | 2.32 x 3.39 | **59 x 86** | 0.6860 | **Yu-Gi-Oh!** |
| `credit` | **2.12 x 3.38** | 53.97 x 85.72 | 0.6296 | {{< renderhtml `Credit cards <ul><li>CR80</li><li>ISO/IEC 7810</li></ul>` >}} |
| `euro_business` | 2.17 x 3.35 | **55 x 85** | 0.6471 | EU business cards |
| `photo` | 2.17 x 3.35 | **55 x 85** | 0.6471 | K-pop photocards |
| `euro_mini` | 1.73 x 2.68 | **44 x 68** | 0.6471 | |
| `mini` | **1.75 x 2.5** | 44.45 x 63.5 | 0.7000 | |
| `bridge_square` | **2.25 x 2.25** | 57.15 x 57.15 | 1.0000 | |
| `domino_square` | **1.75 x 1.75** | 44.45 x 44.45 | 1.0000 | |
| `micro` | **1.25 x 1.75** | 31.75 x 44.45 | 0.7143 | |

The table below shows each paper size, sorted by size and standard.

| Paper size | Inches | Millimeters |
| --- | --- | --- |
| `letter` | **8.5 x 11** | 215.9 x 279.4 |
| `tabloid` | **11 x 17** | 279.4 x 431.8 |
| `a4` | 8.27 x 11.69 | **210 x 297** |
| `a3` | 11.69 x 16.54 | **297 x 420** |
| `arch_b` | **12 x 18** | 304.8 x 457.2 |