import math
from typing import Dict, Any

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
from PIL import Image
import io

import size_convert
from enums import Orientation, CardSize, PaperSize


def generate_layout(
    card_size: CardSize,
    paper_size: PaperSize,
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
) -> Dict[str, Any]:
    """Compute the card layout for a given card size on a given paper size.

    All dimension parameters are unit strings (e.g. "63mm", "2.5in").
    The caller is responsible for looking up values from layouts.json.

    Args:
        card_size: Card size identifier (for the template name).
        paper_size: Paper size identifier (for the template name).
        orientation: Paper orientation. PORTRAIT swaps paper width/height
            (paper sizes in layouts.json are stored as landscape).
        card_width: Card width as a unit string.
        card_height: Card height as a unit string.
        card_radius: Card corner radius as a unit string.
        paper_width: Paper width as a unit string (landscape value from layouts.json).
        paper_height: Paper height as a unit string (landscape value from layouts.json).
        inset: Silhouette registration mark inset as a unit string.
        thickness: Silhouette registration mark thickness as a unit string.
        length: Silhouette registration mark length as a unit string.
        ppi: Pixels per inch for pixel conversion.

    Returns:
        Dict with keys:
            card_width_px (int): Card width in pixels.
            card_height_px (int): Card height in pixels.
            paper_width_px (int): Paper width in pixels.
            paper_height_px (int): Paper height in pixels.
            x_pos (List[int]): X pixel positions for each column of cards.
            y_pos (List[int]): Y pixel positions for each row of cards.
            template (str): Template identifier string.
    """
    # Paper sizes in layouts.json are stored as landscape (width > height).
    # For portrait orientation, swap paper dimensions.
    if orientation == Orientation.PORTRAIT:
        effective_paper_width = paper_height
        effective_paper_height = paper_width
    else:
        effective_paper_width = paper_width
        effective_paper_height = paper_height

    return _compute_layout(
        card_width=card_width,
        card_height=card_height,
        card_radius=card_radius,
        page_width=effective_paper_width,
        page_height=effective_paper_height,
        orientation=orientation,
        ppi=ppi,
        card_size=card_size,
        paper_size=paper_size,
        inset=inset,
        thickness=thickness,
        length=length,
    )


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


def _compute_layout(
    card_width: str,
    card_height: str,
    card_radius: str,
    page_width: str,
    page_height: str,
    orientation: Orientation,
    ppi: int,
    card_size: str,
    paper_size: str,
    inset: str,
    thickness: str,
    length: str,
) -> Dict[str, Any]:
    """Compute card positions on a page, accounting for margins, bleed, and registration marks.

    The algorithm works as follows:
    1. Convert all dimensions from unit strings to pixels at the given PPI.
    2. Calculate the printable area by subtracting margins required for
       Silhouette registration marks (inset + mark length + half thickness).
    3. Determine how many card rows and columns fit within the printable area.
    4. Check if additional rows/columns could fit by relaxing to the minimum
       margin (just the inset). If so, expand in the direction that has the
       most spare room, to maximize bleed space on the other axis.
    5. Calculate bleed (gap between cards) and space to registration marks,
       reducing bleed first if cards don't fit, then reducing reg mark space.
    6. Center the card grid within the available area.

    Args:
        card_width: Card width as a unit string.
        card_height: Card height as a unit string.
        card_radius: Card corner radius as a unit string (unused in layout, kept for template name).
        page_width: Paper width as a unit string (already adjusted for orientation).
        page_height: Paper height as a unit string (already adjusted for orientation).
        orientation: Paper orientation (used only for the template name).
        ppi: Pixels per inch for all conversions.
        card_size: Card size identifier string (for template name).
        paper_size: Paper size identifier string (for template name).
        inset: Silhouette registration mark inset distance.
        thickness: Silhouette registration mark line thickness.
        length: Silhouette registration mark line length.

    Returns:
        Dict with: card_width_px, card_height_px, paper_width_px, paper_height_px,
                   x_pos, y_pos, template.
    """
    # Maximum bleed of 1mm between cards and 2mm space to registration marks
    bleed_x_px = size_convert.size_to_pixel("1mm", ppi)
    bleed_y_px = bleed_x_px
    space_x_px = size_convert.size_to_pixel("2mm", ppi)
    space_y_px = space_x_px

    # Convert page size to pixels
    page_width_px = size_convert.size_to_pixel(page_width, ppi)
    page_height_px = size_convert.size_to_pixel(page_height, ppi)

    # Calculate margins for registration marks:
    # min_margin = just the inset (closest cards can get to paper edge)
    # margin = inset + mark length + half thickness (standard safe area)
    min_margin = size_convert.size_to_pixel(inset, ppi)
    margin_x = (size_convert.size_to_pixel(inset, ppi)
                + size_convert.size_to_pixel(length, ppi)
                + round(size_convert.size_to_pixel(thickness, ppi) / 2))
    margin_y = margin_x

    # Convert card dimensions to pixels (card dimensions are never swapped)
    card_width_px = size_convert.size_to_pixel(card_width, ppi)
    card_height_px = size_convert.size_to_pixel(card_height, ppi)

    # Calculate available area within standard margins
    available_width = page_width_px - (2 * margin_x)
    available_height = page_height_px - (2 * margin_y)

    # Calculate available area within minimum margins (inset only)
    min_available_width = page_width_px - (2 * min_margin)
    min_available_height = page_height_px - (2 * min_margin)

    # Determine how many rows/columns fit within standard margins
    num_rows = math.floor(available_height / card_height_px)
    num_cols = math.floor(available_width / card_width_px)

    # Check how many rows/columns could fit within minimum margins
    max_num_rows = math.floor(min_available_height / card_height_px)
    max_num_cols = math.floor(min_available_width / card_width_px)

    # If we can fit more cards by relaxing one axis to minimum margin,
    # expand the axis with the most spare room (to preserve bleed on the other)
    if num_rows < max_num_rows and num_cols < max_num_cols:
        # Both axes could gain cards; expand the one with bigger spare room
        filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))
        filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))
        if (filled_height - available_height) > (filled_width - available_width):
            num_rows = max_num_rows
            margin_y = min_margin
            space_y_px = 0
            available_height = min_available_height
        else:
            num_cols = max_num_cols
            margin_x = min_margin
            space_x_px = 0
            available_width = min_available_width
    elif num_rows < max_num_rows and num_cols == max_num_cols:
        # Only rows can gain; expand vertically
        num_rows = max_num_rows
        margin_y = min_margin
        space_y_px = 0
        available_height = min_available_height
    elif num_rows == max_num_rows and num_cols < max_num_cols:
        # Only columns can gain; expand horizontally
        num_cols = max_num_cols
        margin_x = min_margin
        space_x_px = 0
        available_width = min_available_width
    else:
        # No additional cards from relaxing margins; check if we can still
        # relax margins to increase bleed space
        filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))
        filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))
        if 2 * bleed_x_px < available_width - filled_width:
            margin_y = min_margin
            available_height = min_available_height
        if 2 * bleed_y_px < available_height - filled_height:
            available_width = min_available_width
            margin_x = min_margin

    # Reduce bleed and registration mark space until cards fit
    # Priority: reduce bleed first, then registration mark space
    filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))
    filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))

    while available_height < filled_height:
        if bleed_y_px == 0:
            space_y_px = space_y_px - 1
        else:
            bleed_y_px = bleed_y_px - 1
        filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))

    while available_width < filled_width:
        if bleed_x_px == 0:
            space_x_px = space_x_px - 1
        else:
            bleed_x_px = bleed_x_px - 1
        filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))

    # Center the card grid within the available area
    start_x = round(margin_x + space_x_px + ((available_width - filled_width) / 2))
    start_y = round(margin_y + space_y_px + ((available_height - filled_height) / 2))

    # Build position arrays for each column and row
    x_pos = [start_x]
    y_pos = [start_y]

    for x in range(1, num_cols):
        x_pos.append(start_x + (x * (card_width_px + bleed_x_px)))

    for y in range(1, num_rows):
        y_pos.append(start_y + (y * (card_height_px + bleed_y_px)))

    # Build template identifier string
    custom_paper_size = ""
    if paper_size == "custom":
        custom_paper_size = f'({page_width}x{page_height})'

    custom_card_size = ""
    if card_size == "custom":
        custom_card_size = f'({card_width}x{card_height}R{card_radius})'

    orientation_text = orientation.value
    template = f"{paper_size}{custom_paper_size}_{card_size}{custom_card_size}_{orientation_text}_{len(x_pos)}x{len(y_pos)}"

    return {
        "card_width_px": card_width_px,
        "card_height_px": card_height_px,
        "paper_width_px": page_width_px,
        "paper_height_px": page_height_px,
        "x_pos": x_pos,
        "y_pos": y_pos,
        "template": template,
    }
