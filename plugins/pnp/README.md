# PnP (Print and Play) Plugin

This plugin extracts card images from Print-and-Play game PDFs and organizes them into the appropriate directories for processing with `create_pdf.py`.

## Requirements

- PyMuPDF (`pip install pymupdf`)

## Basic Usage

```sh
python plugins/pnp/extract.py path/to/game.pdf
```

This will extract card images and place them in:
- `game/front/` - Front card images
- `game/double_sided/` - Back card images (named to match fronts)

## CLI Options

```
Usage: extract.py [OPTIONS] PDF_PATH

  Extract card images from a Print-and-Play PDF.

  Assumes alternating front/back pages (odd pages = fronts, even pages = backs).
  Card images are saved to game/front/ and game/double_sided/ directories.

Options:
  --grid TEXT          Grid size override (e.g., '3x3', '2x4'). Auto-detected
                       if not specified.
  --short-edge-flip    Use short-edge flip matching (reverses back card order).
  --min-size INTEGER   Minimum image dimension to be considered a card
                       (default: 200px).
  --help               Show this message and exit.
```

## How It Works

1. **Image Extraction**: Extracts all images from the PDF using PyMuPDF
2. **Filtering**: Removes small images (logos, icons) based on minimum size threshold
3. **Grid Detection**: Auto-detects the card grid layout per page (e.g., 2x3, 3x3)
4. **Position Sorting**: Sorts cards top-to-bottom, left-to-right
5. **Front/Back Pairing**: Assumes odd pages are fronts, even pages are backs
6. **Naming**: Files are named `{page}_{position}.{ext}` (e.g., `1_3.png`)

## Examples

### Basic extraction
```sh
python plugins/pnp/extract.py game/output/my_game.pdf
```

### With grid override
If auto-detection fails, specify the grid manually:
```sh
python plugins/pnp/extract.py game/output/my_game.pdf --grid 3x3
```

### Short-edge flip
For PDFs designed for short-edge flip printing:
```sh
python plugins/pnp/extract.py game/output/my_game.pdf --short-edge-flip
```

### Adjust minimum card size
If small cards aren't being detected:
```sh
python plugins/pnp/extract.py game/output/my_game.pdf --min-size 100
```

## Limitations

- Assumes alternating front/back pages (page 1 = fronts, page 2 = backs, etc.)
- May not work with PDFs that have non-standard layouts
- Does not currently sort by card size/aspect ratio (all cards go to same directory)
- Does not detect common backs (all backs go to `double_sided/`)

## Output Naming Convention

- Front images: `{front_page}_{position}.{ext}` (e.g., `1_1.png`, `1_2.png`)
- Back images: Same name as matching front (e.g., `1_1.png` in `double_sided/`)
- Position is 1-indexed, ordered top-to-bottom, left-to-right
