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
    template: str


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
    card_size: str,
    paper_size: str,
    orientation: Orientation,
    card_width: str,
    card_height: str,
    card_radius: str,
    paper_width: str,
    paper_height: str,
    inset: str,
    thickness: str,
    length: str,
    ppi: int,
) -> CardLayout:
    """Compute card positions on a page, accounting for margins and bleed.

    All dimension parameters are unit strings (e.g. "63mm", "2.5in").
    The caller is responsible for looking up values from layouts.json.

    Paper sizes in layouts.json are stored as landscape (width > height).
    For portrait orientation, this function swaps paper_width and paper_height
    so the paper is taller than wide. Card dimensions are never swapped.

    The available area is plus-shaped. The base margin from the paper edge
    is just the inset. Registration marks create corner zones of size
    (length + thickness/2) at each corner inside the inset boundary.
    Cards can extend into the corner zone on one axis (horizontally or
    vertically) but not both simultaneously.

        ┌──────────────────────────┐
        │   ┌──┐          ┌──┐    │  corner zones (blocked)
        │   │//│          │//│    │
        │   └──┘          └──┘    │
        │      ← cards OK here →  │  edge zones (available)
        │   ┌──┐          ┌──┐    │
        │   │//│          │//│    │
        │   └──┘          └──┘    │
        └──────────────────────────┘

    Within the available area, cards are arranged with uniform bleed
    gaps around and between them:

        | bleed | card | bleed | card | bleed |

        n cards need: n * card + (n + 1) * bleed
        so: n <= (available - bleed) / (card + bleed)

    Args:
        card_size: Card size identifier (for the template name).
        paper_size: Paper size identifier (for the template name).
        orientation: Paper orientation. PORTRAIT swaps paper width/height.
        card_width: Card width as a unit string.
        card_height: Card height as a unit string.
        card_radius: Card corner radius as a unit string (unused in layout).
        paper_width: Paper width as a unit string (landscape value from layouts.json).
        paper_height: Paper height as a unit string (landscape value from layouts.json).
        inset: Silhouette registration mark inset distance.
        thickness: Silhouette registration mark line thickness.
        length: Silhouette registration mark line length.
        ppi: Pixels per inch for all conversions.

    Returns:
        CardLayout named tuple.
    """
    # Hardcoded layout parameters
    BLEED = "1.25mm"
    MARGIN = "0.25mm"

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

    # Base margin from paper edge (just the inset + extra buffer)
    inset_px = size_convert.size_to_pixel(inset, ppi)
    extra_px = size_convert.size_to_pixel(MARGIN, ppi)
    margin_x = inset_px + extra_px
    margin_y = inset_px + extra_px

    # Registration mark corner zone size (extends into the available area
    # from each corner of the inset boundary)
    corner_px = (size_convert.size_to_pixel(length, ppi)
                 + round(size_convert.size_to_pixel(thickness, ppi) / 2))

    # Available area inside base margins
    available_width = page_width_px - 2 * margin_x
    available_height = page_height_px - 2 * margin_y

    # Max cards: n * card + (n + 1) * bleed <= available
    # => n <= (available - bleed) / (card + bleed)
    num_cols = max(0, math.floor((available_width - bleed_px) / (card_width_px + bleed_px)))
    num_rows = max(0, math.floor((available_height - bleed_px) / (card_height_px + bleed_px)))

    # Check for corner registration mark overlap.
    # Cards can extend into the corner zone on one axis but not both.
    # Use centering to find the first card's position and check if it
    # overlaps a corner zone on both axes simultaneously.
    filled_width = num_cols * card_width_px + (num_cols + 1) * bleed_px
    filled_height = num_rows * card_height_px + (num_rows + 1) * bleed_px
    first_x = margin_x + (available_width - filled_width) / 2 + bleed_px
    first_y = margin_y + (available_height - filled_height) / 2 + bleed_px

    if first_x < margin_x + corner_px and first_y < margin_y + corner_px:
        # Card overlaps a corner zone on both axes.
        # Widen the margin on whichever axis preserves more cards.
        wide_margin = inset_px + corner_px + extra_px

        # Option A: widen horizontal margin
        avail_w_a = page_width_px - 2 * wide_margin
        cols_a = max(0, math.floor((avail_w_a - bleed_px) / (card_width_px + bleed_px)))

        # Option B: widen vertical margin
        avail_h_b = page_height_px - 2 * wide_margin
        rows_b = max(0, math.floor((avail_h_b - bleed_px) / (card_height_px + bleed_px)))

        if cols_a * num_rows >= num_cols * rows_b:
            num_cols = cols_a
            margin_x = wide_margin
            available_width = avail_w_a
        else:
            num_rows = rows_b
            margin_y = wide_margin
            available_height = avail_h_b

    # Final grid size and centered positions
    filled_width = num_cols * card_width_px + (num_cols + 1) * bleed_px
    filled_height = num_rows * card_height_px + (num_rows + 1) * bleed_px
    start_x = round(margin_x + (available_width - filled_width) / 2 + bleed_px)
    start_y = round(margin_y + (available_height - filled_height) / 2 + bleed_px)

    # Build position arrays
    x_pos = [start_x + i * (card_width_px + bleed_px) for i in range(num_cols)]
    y_pos = [start_y + j * (card_height_px + bleed_px) for j in range(num_rows)]

    # Build template identifier string
    custom_paper_size = ""
    if paper_size == "custom":
        custom_paper_size = f'({page_width}x{page_height})'

    custom_card_size = ""
    if card_size == "custom":
        custom_card_size = f'({card_width}x{card_height}R{card_radius})'

    orientation_text = orientation.value
    template = f"{paper_size}{custom_paper_size}_{card_size}{custom_card_size}_{orientation_text}_{len(x_pos)}x{len(y_pos)}"

    return CardLayout(
        card_width_px=card_width_px,
        card_height_px=card_height_px,
        paper_width_px=page_width_px,
        paper_height_px=page_height_px,
        x_pos=x_pos,
        y_pos=y_pos,
        template=template,
    )
