#!/usr/bin/env python3
"""
Print and Play (PnP) PDF Extractor

Extracts card images from PnP game PDFs and organizes them into
front, back, and double-sided directories for processing.
"""

import os
from typing import List, Tuple, Optional

import click
import fitz  # PyMuPDF

# Output directories
FRONT_DIR = os.path.join("game", "front")
BACK_DIR = os.path.join("game", "back")
DOUBLE_SIDED_DIR = os.path.join("game", "double_sided")

# Minimum image dimension to be considered a card (filters out logos, icons)
MIN_CARD_DIMENSION = 200


def ensure_directories():
    """Create output directories if they don't exist."""
    for dir_path in [FRONT_DIR, BACK_DIR, DOUBLE_SIDED_DIR]:
        os.makedirs(dir_path, exist_ok=True)


def get_card_images_from_page(
    doc: fitz.Document,
    page: fitz.Page,
    min_dimension: int = MIN_CARD_DIMENSION
) -> List[dict]:
    """
    Extract card-sized images from a page with their positions.

    Returns a list of dicts with keys: xref, width, height, x, y, image_bytes, ext
    Sorted by position (top-to-bottom, left-to-right).
    """
    cards = []

    for img in page.get_images(full=True):
        xref = img[0]
        base_image = doc.extract_image(xref)
        width = base_image["width"]
        height = base_image["height"]

        # Filter out small images (logos, icons)
        if width < min_dimension or height < min_dimension:
            continue

        # Get all positions where this image appears on the page
        rects = page.get_image_rects(xref)
        for rect in rects:
            x0, y0, _, _ = rect

            # Filter out images in header/footer area (top 15% or bottom 5%)
            page_height = page.rect.height
            if y0 < page_height * 0.10:  # Header area
                continue

            cards.append({
                "xref": xref,
                "width": width,
                "height": height,
                "x": x0,
                "y": y0,
                "image_bytes": base_image["image"],
                "ext": base_image["ext"]
            })

    # Sort by position: top-to-bottom (y), then left-to-right (x)
    # Use a tolerance for y-coordinate to group rows
    y_tolerance = 20
    cards.sort(key=lambda c: (round(c["y"] / y_tolerance) * y_tolerance, c["x"]))

    return cards


def detect_grid_size(cards: List[dict], tolerance: float = 30) -> Tuple[int, int]:
    """
    Auto-detect grid size from card positions.

    Returns (columns, rows) tuple.
    """
    if not cards:
        return (0, 0)

    # Group by rows using y-coordinate clustering
    rows = []
    current_row = [cards[0]]
    current_y = cards[0]["y"]

    for card in cards[1:]:
        if abs(card["y"] - current_y) < tolerance:
            current_row.append(card)
        else:
            rows.append(current_row)
            current_row = [card]
            current_y = card["y"]
    rows.append(current_row)

    num_rows = len(rows)
    num_cols = max(len(row) for row in rows) if rows else 0

    return (num_cols, num_rows)


def save_image(image_bytes: bytes, ext: str, output_path: str) -> None:
    """Save image bytes to file."""
    # Normalize extension
    if ext == "jpeg":
        ext = "jpg"

    full_path = f"{output_path}.{ext}"
    with open(full_path, "wb") as f:
        f.write(image_bytes)

    return full_path


def process_pdf(
    pdf_path: str,
    grid: Optional[str] = None,
    short_edge_flip: bool = False,
    min_dimension: int = MIN_CARD_DIMENSION
) -> None:
    """
    Process a PnP PDF and extract card images.

    Args:
        pdf_path: Path to the PDF file
        grid: Optional grid size override (e.g., "3x3")
        short_edge_flip: If True, reverse position order on back pages
        min_dimension: Minimum dimension for card images
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    ensure_directories()

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print(f"Processing: {pdf_path}")
    print(f"Total pages: {total_pages}")

    # Parse grid override if provided
    grid_cols, grid_rows = None, None
    if grid:
        try:
            parts = grid.lower().split("x")
            grid_cols, grid_rows = int(parts[0]), int(parts[1])
            print(f"Using grid override: {grid_cols}x{grid_rows}")
        except (ValueError, IndexError):
            print(f"Warning: Invalid grid format '{grid}', using auto-detection")

    # Track all fronts for pairing with backs
    # Key: (front_page, position_index) -> (image_bytes, ext, output_name)
    front_cards = {}

    # Process pages
    for page_num in range(total_pages):
        page = doc[page_num]
        is_front_page = (page_num % 2 == 0)  # 0-indexed: even = front, odd = back
        page_display = page_num + 1  # 1-indexed for display

        cards = get_card_images_from_page(doc, page, min_dimension)

        if not cards:
            print(f"Page {page_display}: No cards found, skipping")
            continue

        # Detect or use grid
        detected_cols, detected_rows = detect_grid_size(cards)
        actual_count = len(cards)

        if grid_cols and grid_rows:
            expected_count = grid_cols * grid_rows
            if actual_count > expected_count:
                print(f"Page {page_display}: Found {actual_count} cards, expected max {expected_count} from grid")
        else:
            print(f"Page {page_display}: Detected {detected_cols}x{detected_rows} grid ({actual_count} cards)")

        # For short-edge flip, reverse the card order on back pages
        if short_edge_flip and not is_front_page:
            cards = list(reversed(cards))

        # Process each card
        for idx, card in enumerate(cards):
            position = idx + 1  # 1-indexed position

            if is_front_page:
                # Save front image
                output_name = f"{page_display}_{position}"
                output_path = os.path.join(FRONT_DIR, output_name)
                saved_path = save_image(card["image_bytes"], card["ext"], output_path)
                print(f"  Front: {os.path.basename(saved_path)}")

                # Store for back pairing
                front_cards[(page_display, position)] = (
                    card["image_bytes"],
                    card["ext"],
                    output_name
                )
            else:
                # Back page - find matching front
                front_page = page_display - 1  # Previous page is the front
                front_key = (front_page, position)

                if front_key in front_cards:
                    _, _, front_name = front_cards[front_key]
                    # Use front name for the back (for matching)
                    output_path = os.path.join(DOUBLE_SIDED_DIR, front_name)
                    saved_path = save_image(card["image_bytes"], card["ext"], output_path)
                    print(f"  Back:  {os.path.basename(saved_path)} (matches front {front_name})")
                else:
                    # No matching front - save with back page naming
                    output_name = f"{page_display}_{position}"
                    output_path = os.path.join(DOUBLE_SIDED_DIR, output_name)
                    saved_path = save_image(card["image_bytes"], card["ext"], output_path)
                    print(f"  Back:  {os.path.basename(saved_path)} (no matching front)")

    doc.close()

    # Summary
    front_count = len([f for f in os.listdir(FRONT_DIR) if not f.startswith(".")])
    back_count = len([f for f in os.listdir(DOUBLE_SIDED_DIR) if not f.startswith(".")])

    print()
    print(f"Extraction complete!")
    print(f"  Fronts: {front_count} images in {FRONT_DIR}/")
    print(f"  Backs:  {back_count} images in {DOUBLE_SIDED_DIR}/")


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option(
    "--grid",
    default=None,
    help="Grid size override (e.g., '3x3', '2x4'). Auto-detected if not specified."
)
@click.option(
    "--short-edge-flip",
    is_flag=True,
    default=False,
    help="Use short-edge flip matching (reverses back card order)."
)
@click.option(
    "--min-size",
    default=MIN_CARD_DIMENSION,
    help=f"Minimum image dimension to be considered a card (default: {MIN_CARD_DIMENSION}px)."
)
def cli(pdf_path: str, grid: Optional[str], short_edge_flip: bool, min_size: int):
    """
    Extract card images from a Print-and-Play PDF.

    Assumes alternating front/back pages (odd pages = fronts, even pages = backs).
    Card images are saved to game/front/ and game/double_sided/ directories.
    """
    try:
        process_pdf(pdf_path, grid=grid, short_edge_flip=short_edge_flip, min_dimension=min_size)
    except Exception as e:
        print(f"Error: {e}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
