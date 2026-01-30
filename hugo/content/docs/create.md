---
title: 'create_pdf.py'
weight: 1
---

`create_pdf.py` is a CLI tool that layouts your card images into a PDF with registration marks that can be cut out with the appropriate cutting template in [`cutting_templates/`](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/cutting_templates).

![Example PDF](/images/create_pdf.png)

## Basic Usage

### Create a Python virtual environment
```sh
python -m venv venv
```

### Activate the Python virtual environment
{{< tabs items="macOS/Linux,Windows" defaultIndex="0" >}}

  {{< tab >}}
```sh
. venv/bin/activate
```
  {{< /tab >}}
  {{< tab >}}
```powershell
.\venv\Scripts\Activate.ps1
```

> [!NOTE]
> You may see a **security error**. If you do, run the following, then try activating the environment again.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
  {{< /tab >}}

{{< /tabs >}}

### Install Python packages

```shell
pip install -r requirements.txt
```

### Prepare images

Put your front images in the `game/front/` folder.

Put your back image in the `game/back/` folder.

### Run the script

{{< tabs items="Letter size paper,A4 size paper" defaultIndex="0" >}}

  {{< tab >}}
```sh
python create_pdf.py
```
  {{< /tab >}}
  {{< tab >}}
```sh
python create_pdf.py --paper_size a4
```
  {{< /tab >}}

{{< /tabs >}}

Get your PDF at `game/output/game.pdf`.

## Plugins

Plugins streamline the process for acquiring card images for various games.

The [Magic: The Gathering]({{% ref "../plugins/mtg" %}}) plugin supports various decklist formats, including **MTGA**, **MTGO**, **Archidekt**, **Deckstats**, **Moxfield**, and **Scryfall**.

The [Yu-Gi-Oh!]({{% ref "../plugins/yugioh" %}}) plugin supports **YDK** and **YDKE** formats.

The [Lorcana]({{% ref "../plugins/lorcana" %}}) plugin supports **Dreamborn** format.

The [Riftbound plugin]({{% ref "../plugins/riftbound" %}}) supports **Tabletop Simulator**, **Pixelborn**, and **Piltover Archive** formats.

The [Altered plugin]({{% ref "../plugins/altered" %}}) supports **Ajordat** format.

## Double-Sided Cards

To create double-sided cards, put front images in the `game/front/` folder and back images in the `game/double_sided/` folder. The filenames (and file extensions) must match for each pair.

## Corner Artifacts

If your card images have rounded corners, they may be missing print bleed in the PDF. You may have seen white Xs appear in your PDF; these are artifacts from rounded corners. Because of the missing print bleed, when these cards are cut, they may have a sliver of white on the corners.

![Extend corners](/images/extend_corners.jpg)

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

![Skip front](/images/skip_front.png)

If you cut from the back, you might consider:

```sh
python create_pdf.py --skip 0
```

![Skip back](/images/skip_back.png)

## CLI Options

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

## Examples

Create poker-sized cards with A4 sized paper.

```sh
python create_pdf.py --card_size poker --paper_size a4
```

Crop the borders of the front and double-sided images by 3 mm on all sides. This option is useful if your images already have print bleed like those from [MPCFill](https://mpcfill.com/).

```sh
python create_pdf.py --crop 3mm
```

Remove the [rounded corners](#corner-artifacts) from the PDF and load the saved offset from [`offset_pdf.py`]({{% ref "offset.md" %}}).

```sh
python create_pdf.py --extend_corners 10 --load_offset
```

Produce a 600 pixels per inch (PPI) file with minimal compression.

```sh
python create_pdf.py --ppi 600 --quality 100
```