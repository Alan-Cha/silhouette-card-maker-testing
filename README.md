# Custom Card Games with Silhouette Cutting Machines

![](hugo/static/images/display.jpg)

Ever wanted to make your own custom card game but without the hassle of a craft knife, a rotary cutter, or a paper guillotine? How about making your own proxies to playtest your favorite TCG?

You can do it all with the press of a button and a cutting machine! And I can show you how!

If this is your first time here, check out the [tutorial](https://alan-cha.github.io/silhouette-card-maker/tutorial/)! Please join our [Discord server](https://discord.gg/jhsKmAgbXc) too!

## Demo

Watch me cut **104 cards in 26 minutes** without breaking a sweat!

[![Proxying a MTG Commander Deck in 26 minutes](hugo/static/images/youtube_demo.png)](https://www.youtube.com/watch?v=RVHtqsRW8t8)

## Purpose

The purpose of this repo is to enable you to use a Silhouette cutting machine to create card games and proxies. Proxies are only intended to be used for casual play and playtesting.

Proxies should be easily identifiable as proxies. You may not use this repo to create counterfeit cards to deceive people or to play in sanctioned tournaments. You are only permitted to sell cards if you are the full privileged copyright holder.

## Contents

* [documentation](https://alan-cha.github.io/silhouette-card-maker)
* [tutorial](https://alan-cha.github.io/silhouette-card-maker/tutorial/)
* [supply list](https://alan-cha.github.io/silhouette-card-maker/tutorial/supplies/)
* [create_pdf.py](#create_pdfpy), a script for laying out your cards in a PDF
* [offset_pdf.py](#offset_pdfpy), a script for adding an offset to your PDF
* [cutting_templates/](cutting_templates/), a directory containing Silhoutte Studio cutting templates
* [calibration/](calibration/), a directory containing offset calibration sheets
* [examples/](examples/), a directory containing sample games
* [plugins/](plugins/), a directory containing scripts for streamlining card image acquisition

## Supported Sizes

This project supports the following card and paper sizes, with more in the future:

| Format            | `letter` | `tabloid` | `a4` | `a3` | `archb` |
|-------------------|----------|-----------|------|------|---------|
| `standard`        | ✅       | ✅        | ✅   | ✅   | ✅      |
| `standard_double` | ✅       | ❌        | ✅   | ❌   | ❌      |
| `japanese`        | ✅       | ❌        | ✅   | ❌   | ❌      |
| `poker`           | ✅       | ✅        | ✅   | ❌   | ❌      |
| `poker_half`      | ✅       | ❌        | ✅   | ❌   | ❌      |
| `bridge`          | ✅       | ✅        | ✅   | ❌   | ❌      |
| `bridge_square`   | ✅       | ❌        | ❌   | ❌   | ❌      |
| `tarot`           | ✅       | ✅        | ✅   | ❌   | ❌      |
| `domino`          | ✅       | ❌        | ❌   | ❌   | ❌      |
| `domino_square`   | ✅       | ✅        | ❌   | ❌   | ❌      |

| Card size         | Inches          | Millimeters    | Notes |
| ----------------- | --------------- | -------------- | ----- |
| `standard`        | 2.48 x 3.46     | **63 x 88**    | <ul><li>**Magic: the Gathering**</li><li>**Pokémon**</li><li>**Lorcana**</li><li>**One Piece**</li><li>**Digimon**</li><li>**Star Wars: Unlimited**</li><li>**Flesh and Blood**</li></ui> |
| `standard_double` | 4.96 x 3.46     | **126 x 88**   | <ul><li>**Magic: the Gathering** oversized <ul><li>Planechase</li> <li>Archenemy</li> <li>Commander</li></ui> </li></ui> |
| `japanese`        | 2.32 x 3.39     | **59 x 86**    | <ul><li>**Yu-Gi-Oh!**</li></ui> |
| `poker`           | **2.5 x 3.5**   | 63.5 x 88.9    |       |
| `poker_half`      | **1.75 x 2.45** | 44.45 x 62.23  |       |
| `bridge`          | **2.25 x 3.5**  | 57.15 x 88.9   |       |
| `bridge_square`   | **2.25 x 2.25** | 57.15 x 57.15  |       |
| `tarot`           | **2.75 x 4.75** | 69.85 x 120.65 |       |
| `domino`          | **1.75 x 3.5**  | 44.45 x 88.9   |       |
| `domino_square`   | **1.75 x 1.75** | 44.45 x 44.45  |       |

| Paper size | Inches       | Millimeters   |
| ---------- | ------------ | ------------- |
| `letter`   | **8.5 x 11** | 215.9 x 279.4 |
| `tabloid`  | **11 x 17**  | 279.4 x 431.8 |
| `a4`       | 8.3 x 11.7   | **210 x 297** |
| `a3`       | 11.7 x 16.5  | **297 x 420** |
| `archb`    | **12 x 18**  | 304.8 x 457.2 |

You can find all the cutting templates for Silhouette Studio in [`cutting_templates/`](cutting_templates/).

## Donate

If you enjoyed using Silhouette Card Maker, consider [donating](https://www.paypal.com/donate/?hosted_button_id=ZH2XCSLXERBW8) to help support me and the project. Thank you!

## create_pdf.py
`create_pdf.py` is a CLI tool that layouts your card images into a PDF with registration marks that can be cut out with the appropriate cutting template in [`cutting_templates/`](cutting_templates/).

![Example PDF](hugo/static/images/create_pdf.png)

### Basic Usage

Create a Python virtual environment.
```sh
python -m venv venv
```

Activate the Python virtual environment.

**Terminal (macOS/Linux):**
```sh
. venv/bin/activate
```

**PowerShell (Windows):**
```powershell
.\venv\Scripts\Activate.ps1
```

Download Python packages.
```sh
pip install -r requirements.txt
```

Put your front images in the `game/front/` folder.

Put your back image in the `game/back/` folder.

Run the script.

**Letter size paper:**
```sh
python create_pdf.py
```

**A4 size paper:**
```sh
python create_pdf.py --paper_size a4
```

Get your PDF at `game/output/game.pdf`.

### Plugins

Plugins streamline the process for acquiring card images for various games.

The [Magic: The Gathering plugin](plugins/mtg/README.md) supports various decklist formats, including **MTGA**, **MTGO**, **Archidekt**, **Deckstats**, **Moxfield**, and **Scryfall**.

The [Pokemon plugin](plugins/pokemon/README.md) supports **Limitless TCG** format.

The [Yu-Gi-Oh! plugin](plugins/yugioh/README.md) supports **YDK** and **YDKE** formats.

The [Altered plugin](plugins/altered/README.md) supports **Ajordat** format.

The [Ashes Reborn plugin](plugins/ashes_reborn/README.md) supports **Ashes** and **Ashes DB** formats.

The [Digimon plugin](plugins/digimon/README.md) supports **Tabletop Simulator**, **Digimoncard.io**, **Digimoncard.dev**, **Digimoncard.app**, **DigimonMeta**, and **Untap** formats.

The [Elestrals plugin](plugins/elestrals/README.md) supports **Elestrals** format.

The [Final Fantasy plugin](plugins/final_fantasy/README.md) supports **Tabletop Simulator** and **Untap** formats.

The [Flesh and Blood plugin](plugins/flesh_and_blood/README.md) supports **Fabrary** format.

The [Grand Archive plugin](plugins/grand_archive/README.md) supports **Omnideck** format.

The [Gundam plugin](plugins/gundam/README.md) supports **DeckPlanet**, **Limitless TCG**, **Egman Events**, and **ExBurst** formats.

The [Lorcana plugin](plugins/lorcana/README.md) supports **Dreamborn** format.

The [Netrunner plugin](plugins/netrunner/README.md) supports **text**, **bbCode**, **markdown**, **plain text**,  and **Jinteki** formats.

The [One Piece plugin](plugins/one_piece/README.md) supports **OPTCG Simulator** and **Egman Events** formats.

The [Riftbound plugin](plugins/riftbound/README.md) supports **Tabletop Simulator**, **Pixelborn**, and **Piltover Archive** formats.

The [Sorcery: Contested Realm plugin](plugins/sorcery_contested_realm/README.md) supports **Curiosa** format.

The [Star Wars Unlimited plugin](plugins/star_wars_unlimited/README.md) supports **SWUDB JSON**, **Melee**, and **Picklist** formats.

### Double-Sided Cards

To create double-sided cards, put front images in the `game/front/` folder and back images in the `game/double_sided/` folder. The filenames (and file extensions) must match for each pair.

### Corner Artifacts

If your card images have rounded corners, they may be missing print bleed in the PDF. Because of the missing print bleed, when the cards are cut, they may have a sliver of white on the corners.

![Extend corners](hugo/static/images/extend_corners.jpg)

The `--extend_corners` option can ameliorate this issue. You may need to experiment with the value but I recommend starting with `10`

```sh
python create_pdf.py --extend_corners 10
```

### Skip Cards

One solution for registration issues is to use a Post-It note to cover up cards near the registration marks.

However, if you would prefer to skip this manual step, you can skip the card near registration marks using the `--skip` option.

```sh
python create_pdf.py --skip 4
```

![Skip front](hugo/static/images/skip_front.png)

If you cut from the back, you might consider:

```sh
python create_pdf.py --skip 0
```

![Skip back](hugo/static/images/skip_back.png)

### CLI Options

```
Usage: create_pdf.py [OPTIONS]

Options:
  --front_dir_path TEXT           The path to the directory containing the
                                  card fronts.  [default: game/front]
  --back_dir_path TEXT            The path to the directory containing one or
                                  more card backs.  [default: game/back]
  --double_sided_dir_path TEXT    The path to the directory containing card
                                  backs for double-sided cards.  [default:
                                  game/double_sided]
  --output_path TEXT              The desired path to the output PDF.
                                  [default: game/output/game.pdf]
  --output_images                 Create images instead of a PDF.
  --card_size [standard|standard_double|japanese|poker|poker_half|bridge|bridge_square|tarot|domino|domino_square]
                                  The desired card size.  [default: standard]
  --paper_size [letter|tabloid|a4|a3|archb]
                                  The desired paper size.  [default: letter]
  --registration [3|4]            The desired registration.  [default: 3]
  --only_fronts                   Only use the card fronts, exclude the card
                                  backs.
  --crop TEXT                     Crop the outer portion of front and double-
                                  sided images. Examples: 3mm, 0.125in, 6.5.
  --crop_backs TEXT               Crop the outer portion of back images.
                                  Examples: 3mm, 0.125in, 6.5.
  --extend_corners INTEGER RANGE  Reduce artifacts produced by rounded corners
                                  in card images.  [default: 0; x>=0]
  --ppi INTEGER RANGE             Pixels per inch (PPI) when creating PDF.
                                  [default: 300; x>=0]
  --quality INTEGER RANGE         File compression. A higher value corresponds
                                  to better quality and larger file size.
                                  [default: 75; 0<=x<=100]
  --load_offset                   Apply saved offsets. See `offset_pdf.py` for
                                  more information.
  --skip INTEGER RANGE            Skip a card based on its index. Useful for
                                  registration issues. Examples: 0, 4.  [x>=0]
  --name TEXT                     Label each page of the PDF with a name.
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

### Examples

Create poker-sized cards with A4 sized paper.

```sh
python create_pdf.py --card_size poker --paper_size a4
```

Crop the borders of the front and double-sided images by 3 mm on all sides. This option is useful if your images already have print bleed like those from [MPCFill](https://mpcfill.com/).

```sh
python create_pdf.py --crop 3mm
```

Remove the [rounded corners](#corner-artifacts) from the PDF and load the saved offset from [`offset_pdf.py`](#offset_pdfpy).

```sh
python create_pdf.py --extend_corners 10 --load_offset
```

Produce a 600 pixels per inch (PPI) file with minimal compression.

```sh
python create_pdf.py --ppi 600 --quality 100
```

## offset_pdf.py

It's pivotal to ensure that your card fronts and backs are aligned. The front and back alignment is mainly determined by your printer, but it's not always possible to calibrate it.

`offset_pdf.py` is a CLI tool that adds an offset to every other page in a PDF. This offset can compensate for the natural offset of your printer, allowing you to have good front and back alignment. It also supports an angle offset to correct for rotational misalignment.

### Basic Usage

First, you must determine the offset by using the [calibration sheets](calibration/).

`<paper size>_calibration.pdf` has a front page and a back page.

![Calibration](hugo/static/images/calibration.png)

The front page is a simple grid of squares.

The back page is the same grid of squares, except each square has a slight offset. The following grid illustrates the applied offsets.

```
| (-2, -2) | (-1, -2) | ( 0, -2) | ( 1, -2) | ( 2, -2) |
--------------------------------------------------------
| (-2, -1) | (-1, -1) | ( 0, -1) | ( 1, -1) | ( 2, -1) |
--------------------------------------------------------
| (-2,  0) | (-1,  0) |  Center  | ( 1,  0) | ( 2,  0) |
--------------------------------------------------------
| (-2,  1) | (-1,  1) | ( 0,  1) | ( 1,  1) | ( 2,  1) |
--------------------------------------------------------
| (-2,  2) | (-1,  2) | ( 0,  2) | ( 1,  2) | ( 2,  2) |
```

To determine the required offset, print out `<paper size>_calibration.pdf` with the card stock you plan to use.

Shine a strong light on the front so you can see the shadows on the back. Determine which set of front and back squares are aligned. This set will provide your offset.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](#basic-usage) for more information.

Run the script with your offset. This will move all your back sheets in the direction of your offset.
```sh
python offset_pdf.py --x_offset -5 --y_offset 10
```

You can also apply an angle offset to correct for rotational misalignment. This will rotate all your back sheets clockwise in addition to offset.
```sh
python offset_pdf.py --x_offset -5 --y_offset 10 --angle 0.5
```

Get your offset PDF at `game/output/game_offset.pdf`.

### Large offset

If no square on your calibration sheet matches, then you'll need to create a new calibration sheet with an arbitrary offset. After determining the offset using the offset calibration sheet, you can add the two offsets to determine your true offset.

To create an offset calibration sheet, use the `--pdf_path` option, targeting the calibration sheet of your paper size. For example:

```sh
python offset_pdf.py --pdf_path calibration/letter_calibration.pdf --x_offset 30 --y_offset -10
```

This will produce `calibration/letter_calibration_offset.pdf`, which is the same as calibration sheet but with an offset of (30, -10).

Print this out and determine which set of front and back squares are aligned. If none are aligned, try generating another offset calibration sheet with a different arbitrary offset.

Let's say there is a set of a front and back squares and the offset is (5, 5). You can add the arbitrary offset with this offset to find the true offset.

```
(30, -10) + (5, 5) = (35, -5)
```

The true offset if (35, -5).

You can verify this is true by generating a offset calibration sheet using this offset.

```sh
python offset_pdf.py --pdf_path calibration/letter_calibration.pdf --x_offset 35 --y_offset -5
```

Print this out and the center set of front and back squares, (0, 0), should be aligned.

### Save Offset

You can save your x, y, and angle offset with the `--save` option. After saving your offset, it'll be automatically applied every time you run `offset_pdf.py`. You can override the loaded offset using `--x_offset`, `--y_offset`, and `--angle`.

```sh
python offset_pdf.py --x_offset -5 --y_offset 10 --angle 0.5 --save
```

Additionally, you can automatically apply a saved offset in [`create_pdf.py`](#create_pdfpy) by using the `--load_offset` option.

```sh
python create_pdf.py --load_offset
```

### CLI Options

```
Usage: offset_pdf.py [OPTIONS]

Options:
  --pdf_path TEXT         The path of the input PDF.
  --output_pdf_path TEXT  The desired path of the offset PDF.
  -x, --x_offset INTEGER  The desired offset in the x-axis.
  -y, --y_offset INTEGER  The desired offset in the y-axis.
  -a, --angle FLOAT       The desired angle offset in degrees (positive =
                          clockwise).
  -s, --save              Save the offset values.
  --ppi INTEGER RANGE     Pixels per inch (PPI) when creating PDF.  [default:
                          300; x>=0]
  --help                  Show this message and exit.
```