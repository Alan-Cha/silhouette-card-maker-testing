---
title: 'create_pdf.py'
weight: 1
---

`create_pdf.py` is a CLI tool that layouts your card images into a printable PDF. Then, you can cut out the cards with the appropriate cutting template in [`cutting_templates/`](https://github.com/Alan-Cha/silhouette-card-maker-testing/tree/main/cutting_templates).

## Basic Usage

### Create a Python virtual environment
```shell
python -m venv venv
```

### Activate the Python virtual environment
{{< tabs items="macOS/Linux,Windows" defaultIndex="1" >}}

  {{< tab >}}
```shell
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

### Prepare images

Put your front images in `game/front`.

Put your back image in `game/back`.

### Run the script
```shell
python create_pdf.py
```

Get your PDF at `game/output/game.pdf`.

## Plugins

Plugins streamline the process for acquiring card image for various games.

The MTG plugin is currently available, which can automatically acquire card images based on a decklist. Various decklist formats are supported, including MTGA, MTGO, Archidekt, Deckstats, and Moxfield. To learn more, see [here]({{% ref "../plugins" %}}).

## Double-Sided Cards

To create double-sided cards, put front images in `game/front` and back images in `game/double_sided`. The filenames must match for each pair.

## White Corners

If your card images have rounded corners, they may be missing print bleed in the PDF. You may have seen white Xs appear in your PDF; these are artifacts from rounded corners. Because of the missing print bleed, when these cards are cut, they may have a sliver of white on the corners.

![Extend corners](/images/extend_corners.jpg)

The `--extend_corners` option can ameliorate this issue. You may need to experiment with the value but I recommend starting with `10`

```shell
python create_pdf.py --extend_corners 10
```

## CLI Options

```
Usage: create_pdf.py [OPTIONS]

Options:
  --front_dir_path TEXT           The path to the directory containing the
                                  card fronts.  [default: game/front]
  --back_dir_path TEXT            The path to the directory containing one or
                                  no card backs.  [default: game/back]
  --double_sided_dir_path TEXT    The path to the directory containing card
                                  backs for double-sided cards.  [default:
                                  game/double_sided]
  --output_path TEXT              The desired path to the output PDF.
                                  [default: game/output/game.pdf]
  --output_images                 Create images instead of a PDF.
  --card_size [standard|japanese|poker|poker_half|bridge]
                                  The desired card size.  [default: standard]
  --paper_size [letter|tabloid|a4|a3|archb]
                                  The desired paper size.  [default: letter]
  --only_fronts                   Only use the card fronts, exclude the card
                                  backs.
  --crop FLOAT RANGE              Crop a percentage of the outer portion of
                                  front and double-sided images, useful for
                                  existing print bleed.  [0<=x<=100]
  --extend_corners INTEGER RANGE  Reduce artifacts produced by rounded corners
                                  in card images.  [default: 0; x>=0]
  --ppi INTEGER RANGE             Pixels per inch (PPI) when creating PDF.
                                  [default: 300; x>=0]
  --quality INTEGER RANGE         File compression. A higher value corresponds
                                  to better quality and larger file size.
                                  [default: 75; 0<=x<=100]
  --load_offset                   Apply saved offsets. See `offset_pdf.py` for
                                  more information.
  --name TEXT                     Label each page of the PDF with a name.
  --help                          Show this message and exit.
```

## Examples

Do not generate the back side. This option is useful if you want to save ink and produce single-sided cards.

```shell
python create_pdf.py --only_fronts
```

Create poker-sized cards with A4 sized paper.

```shell
python create_pdf.py --card_size poker --paper_size a4
```

Crop the borders of the front and double-sided images. This option is useful if your images already have print bleed.

```shell
python create_pdf.py --crop 6.5
```

Remove the [white corners](#white-corners) from the PDF and load the saved offset from [`offset_pdf.py`]({{% ref "offset.md" %}}).

```shell
python create_pdf.py --extend_corners 10 --load_offset
```

Produce a 600 pixels per inch (PPI) file with minimal compression.

```shell
python create_pdf.py --ppi 600 --quality 100
```