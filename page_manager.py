import math
from typing import List, NamedTuple

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
from PIL import Image
import io

import size_convert
from enums import Orientation


class CardLayout(NamedTuple):
    card_width_px: int
    card_height_px: int
    paper_width_px: int
    paper_height_px: int
    x_pos: List[int]
    y_pos: List[int]
    max_length_mm: float


def generate_reg_mark(
    paper_width: str,
    paper_height: str,
    inset: str,
    thickness: str,
    length: str,
    dpi: int,
) -> Image.Image:
    """Generate a registration mark image for the given paper size.

    Args:
        paper_width: Paper width as a unit string (e.g. "11in").
        paper_height: Paper height as a unit string (e.g. "8.5in").
        inset: Distance from the paper edge to the registration marks.
        thickness: Line thickness for registration marks.
        length: Line length for registration marks.
        dpi: Resolution in dots per inch.

    Returns:
        PIL Image with registration marks drawn on a white background.
    """
    paper_width_mm = size_convert.size_to_mm(paper_width)
    paper_height_mm = size_convert.size_to_mm(paper_height)
    inset_mm = size_convert.size_to_mm(inset)
    thickness_mm = size_convert.size_to_mm(thickness)
    thickness_pt = size_convert.size_to_pt(thickness)
    length_mm = size_convert.size_to_mm(length)

    # Create figure sized to the paper dimensions
    fig = plt.figure(figsize=(paper_width_mm / 25.4, paper_height_mm / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])  # Use full canvas
    ax.set_xlim(0, paper_width_mm)
    ax.set_ylim(0, paper_height_mm)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('white')

    # Add filled black square (5x5mm at inset from left and top)
    square = Rectangle(
        (inset_mm, paper_height_mm - inset_mm - 5),
        5, 5,
        facecolor='black',
        edgecolor='black',
        linewidth=thickness_pt
    )
    ax.add_patch(square)

    # Horizontal line bottom-left
    x_end = inset_mm + length_mm - (thickness_mm / 2)
    x_start = inset_mm
    y_start = inset_mm
    y_end = inset_mm
    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)

    # Vertical line bottom-left
    x_end = inset_mm
    x_start = inset_mm
    y_start = inset_mm
    y_end = inset_mm + length_mm - (thickness_mm / 2)
    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)

    # Horizontal line top-right
    x_end = paper_width_mm - inset_mm
    x_start = x_end - length_mm + (thickness_mm / 2)
    y_start = paper_height_mm - inset_mm
    y_end = paper_height_mm - inset_mm
    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)

    # Vertical line top-right
    x_end = paper_width_mm - inset_mm
    x_start = paper_width_mm - inset_mm
    y_start = paper_height_mm - inset_mm
    y_end = y_start - length_mm + (thickness_mm / 2)
    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)

    # Save output
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='jpg')
    img_buf.seek(0)
    return Image.open(img_buf)


def generate_layout(
    orientation: Orientation,
    card_width: str,
    card_height: str,
    paper_width: str,
    paper_height: str,
    inset: str,
    length: str,
    ppi: int,
) -> CardLayout:
    """Compute card positions on a page, accounting for margins and bleed.

    All dimension parameters are unit strings (e.g. "63mm", "2.5in").
    The caller is responsible for looking up values from layouts.json.

    Paper sizes in layouts.json are stored as landscape (width > height).
    For portrait orientation, this function swaps paper_width and paper_height
    so the paper is taller than wide. Card dimensions are never swapped.

    The base margin from the paper edge is just the inset. Registration
    marks also create square exclusion zones at each corner, extending
    (inset + length) from the paper edge on both axes. Cards can overlap
    the corner zone on one axis but not both simultaneously.

        paper edge
        ┌──────────────────────────┐
        │ ┌───┐            ┌───┐  │
        │ │///│            │///│  │  corner squares (blocked)
        │ └───┘            └───┘  │
        │     ← cards OK here →   │
        │ ┌───┐            ┌───┐  │
        │ │///│            │///│  │
        │ └───┘            └───┘  │
        └──────────────────────────┘

    Within the available area, cards are arranged with uniform bleed
    gaps around and between them:

        | bleed | card | bleed | card | bleed |

        n cards need: n * card + (n + 1) * bleed
        so: n <= (available - bleed) / (card + bleed)

    Args:
        orientation: Paper orientation. PORTRAIT swaps paper width/height.
        card_width: Card width as a unit string.
        card_height: Card height as a unit string.
        paper_width: Paper width as a unit string (landscape value from layouts.json).
        paper_height: Paper height as a unit string (landscape value from layouts.json).
        inset: Silhouette registration mark inset from paper edge.
        length: Silhouette registration mark line length.
        ppi: Pixels per inch for all conversions.

    Returns:
        CardLayout named tuple.
    """
    # Hardcoded layout parameters
    BLEED = "1.25mm"

    # Paper sizes in layouts.json are stored as landscape (width > height).
    # For portrait orientation, swap paper dimensions.
    if orientation == Orientation.PORTRAIT:
        page_width = paper_height
        page_height = paper_width
    else:
        page_width = paper_width
        page_height = paper_height

    # Convert dimensions to pixels
    page_width_px = size_convert.size_to_pixel(page_width, ppi)
    page_height_px = size_convert.size_to_pixel(page_height, ppi)
    card_width_px = size_convert.size_to_pixel(card_width, ppi)
    card_height_px = size_convert.size_to_pixel(card_height, ppi)
    bleed_px = size_convert.size_to_pixel(BLEED, ppi)

    # Base margin from paper edge (just the inset).
    # Cards and bleed can go right up to the inset along edges.
    inset_px = size_convert.size_to_pixel(inset, ppi)
    margin_x = inset_px
    margin_y = inset_px

    # Corner exclusion zones: each corner has a square exclusion area
    # extending (inset + length) from the paper edge on both axes.
    # Thickness doesn't affect corner zone size. A card overlaps the
    # corner if it's within length of the inset boundary on BOTH axes.
    #
    #   paper edge ──►┌─────────────────────┐
    #                 │      inset          │
    #                 │   ┌────────┐        │
    #                 │   │ corner │        │
    #                 │   │ zone   │← length│
    #                 │   └────────┘        │
    #                 │     length          │
    #                 └─────────────────────┘
    length_px = size_convert.size_to_pixel(length, ppi)

    # Default layout using minimum margins (just inset, ignoring corners).
    # Used if no strategy below avoids corner overlap.
    available_width = page_width_px - 2 * margin_x
    available_height = page_height_px - 2 * margin_y
    num_cols = max(0, math.floor((available_width - bleed_px) / (card_width_px + bleed_px)))
    num_rows = max(0, math.floor((available_height - bleed_px) / (card_height_px + bleed_px)))

    # Cards placed with minimum margins might overlap corner squares.
    # Increasing the margin on one axis pushes cards past the corners.
    # Try three strategies and pick the one with the most cards that
    # avoids corner overlap.
    margin_strategies = [
        (inset_px, inset_px),              # minimum margins
        (inset_px + length_px, inset_px),  # extra x-margin clears corners
        (inset_px, inset_px + length_px),  # extra y-margin clears corners
    ]

    best_card_count = 0
    for x_margin, y_margin in margin_strategies:
        trial_width = page_width_px - 2 * x_margin
        trial_height = page_height_px - 2 * y_margin
        if trial_width <= 0 or trial_height <= 0:
            continue

        trial_cols = max(0, math.floor((trial_width - bleed_px) / (card_width_px + bleed_px)))
        trial_rows = max(0, math.floor((trial_height - bleed_px) / (card_height_px + bleed_px)))
        if trial_cols <= 0 or trial_rows <= 0:
            continue

        # Distance from inset boundary to the nearest card edge
        grid_width = trial_cols * card_width_px + (trial_cols + 1) * bleed_px
        grid_height = trial_rows * card_height_px + (trial_rows + 1) * bleed_px
        gap_x = x_margin + (trial_width - grid_width) / 2 + bleed_px - inset_px
        gap_y = y_margin + (trial_height - grid_height) / 2 + bleed_px - inset_px
        overlaps_corner = gap_x < length_px and gap_y < length_px

        if not overlaps_corner and trial_cols * trial_rows > best_card_count:
            best_card_count = trial_cols * trial_rows
            num_cols, num_rows = trial_cols, trial_rows
            margin_x, margin_y = x_margin, y_margin
            available_width, available_height = trial_width, trial_height

    # Final grid size and centered positions
    filled_width = num_cols * card_width_px + (num_cols + 1) * bleed_px
    filled_height = num_rows * card_height_px + (num_rows + 1) * bleed_px
    start_x = round(margin_x + (available_width - filled_width) / 2 + bleed_px)
    start_y = round(margin_y + (available_height - filled_height) / 2 + bleed_px)

    # Build position arrays
    x_pos = [start_x + i * (card_width_px + bleed_px) for i in range(num_cols)]
    y_pos = [start_y + j * (card_height_px + bleed_px) for j in range(num_rows)]

    # Maximum registration mark length that fits without overlapping
    # card positions, with 2*BLEED buffer.
    max_length_px = max(0, max(start_x - inset_px, start_y - inset_px) - 2 * bleed_px)
    max_length_mm = round(max_length_px * 25.4 / ppi, 2)

    return CardLayout(
        card_width_px=card_width_px,
        card_height_px=card_height_px,
        paper_width_px=page_width_px,
        paper_height_px=page_height_px,
        x_pos=x_pos,
        y_pos=y_pos,
        max_length_mm=max_length_mm,
    )
