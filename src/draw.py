# ==============================================================================
# draw.py
#     Drawing onto the page.
# ==============================================================================
import math

from PIL import Image, ImageDraw
from enum import Enum

from src.enums import FitMode, Orientation
from src.images import fill_rounded_corners, crop_and_scale_image


def draw_card_with_bleed(
    card_image: Image.Image,
    base_image: Image.Image,
    x: int,
    y: int,
    print_bleed: tuple[int, int],
    extra_bleed: tuple[int, int, int, int] = (0, 0, 0, 0),  # top, right, bottom, left
) -> None:
    bleed_width, bleed_height = print_bleed
    extra_top, extra_right, extra_bottom, extra_left = extra_bleed

    bleed_top = bleed_height + extra_top
    bleed_bottom = bleed_height + extra_bottom
    bleed_left = bleed_width + extra_left
    bleed_right = bleed_width + extra_right

    width, height = card_image.size
    base_image.paste(card_image, (x, y))

    class Axis(int, Enum):
        X = 0
        Y = 1

    def extend_edge(
        crop_box: tuple[int, int, int, int],
        start: tuple[int, int],
        bleed: int,
        axis: Axis,
    ) -> None:
        for bleed_i in range(bleed):
            pos = (
                start[0] + (bleed_i if axis == Axis.X else 0),
                start[1] + (bleed_i if axis == Axis.Y else 0),
            )
            base_image.paste(card_image.crop(crop_box), pos)

    def fill_corner(
        corner_pixel_x: int,
        corner_pixel_y: int,
        corner_x: int,
        corner_y: int,
        width: int,
        height: int,
    ) -> None:
        pixel = card_image.crop(
            (corner_pixel_x, corner_pixel_y, corner_pixel_x + 1, corner_pixel_y + 1)
        )
        for dx in range(width):
            for dy in range(height):
                base_image.paste(pixel, (corner_x + dx, corner_y + dy))

    extend_edge((0, 0, width, 1), (x, y - bleed_top), bleed_top, Axis.Y)
    extend_edge((0, height - 1, width, height), (x, y + height), bleed_bottom, Axis.Y)
    extend_edge((0, 0, 1, height), (x - bleed_left, y), bleed_left, Axis.X)
    extend_edge((width - 1, 0, width, height), (x + width, y), bleed_right, Axis.X)

    fill_corner(0, 0, x - bleed_left, y - bleed_top, bleed_left, bleed_top)
    fill_corner(width - 1, 0, x + width, y - bleed_top, bleed_right, bleed_top)
    fill_corner(0, height - 1, x - bleed_left, y + height, bleed_left, bleed_bottom)
    fill_corner(width - 1, height - 1, x + width, y + height, bleed_right, bleed_bottom)



def draw_card_layout(
    card_images: list[Image.Image | None],
    single_back_image: Image.Image | None,
    base_image: Image.Image,
    num_rows: int,
    num_cols: int,
    x_pos: list[int],
    y_pos: list[int],
    width: int,
    height: int,
    print_bleed: tuple[int, int],
    crop: tuple[float, float],
    crop_backs: tuple[float, float],
    ppi_ratio: float,
    extend_edges: int,
    extend_edges_backs: int,
    extend_corners_radius: int,
    extend_corners_backs_radius: int,
    extend_bleed: int,
    flip: bool,
    fit: FitMode,
    fit_backs: FitMode,
    orientation: Orientation,
) -> None:
    num_cards = num_rows * num_cols
    crop_percent_x, crop_percent_y = crop
    crop_backs_percent_x, crop_backs_percent_y = crop_backs
    print_bleed_x, print_bleed_y = print_bleed

    extend_edges_thickness = math.floor(extend_edges * ppi_ratio)
    extend_edges_backs_thickness = math.floor(extend_edges_backs * ppi_ratio)
    extend_corners_thickness = math.floor(extend_corners_radius * ppi_ratio)
    extend_corners_backs_thickness = math.floor(extend_corners_backs_radius * ppi_ratio)
    extend_bleed_thickness = math.floor(extend_bleed * ppi_ratio)

    scaled_width = math.floor(width * ppi_ratio)
    scaled_height = math.floor(height * ppi_ratio)

    scaled_bleed_width = math.ceil(print_bleed_x * ppi_ratio)
    scaled_bleed_height = math.ceil(print_bleed_y * ppi_ratio)

    # Fill spaces with card back
    for i, card_image in enumerate(card_images):
        if card_image is None:
            continue

        col = i % num_cards % num_cols
        row = (i % num_cards) // num_cols

        if flip:
            if orientation == Orientation.PORTRAIT:
                col = num_cols - col - 1
            else:
                row = num_rows - row - 1

        base_x = math.floor(x_pos[col] * ppi_ratio)
        base_y = math.floor(y_pos[row] * ppi_ratio)

        # Default: use synthetic bleed, no position offset needed
        bleed_offset_x = 0
        bleed_offset_y = 0
        synthetic_bleed = (scaled_bleed_width, scaled_bleed_height)

        if card_image is single_back_image:
            active_crop_x, active_crop_y = crop_backs_percent_x, crop_backs_percent_y
            active_fit = fit_backs
            active_extend_edges_thickness = extend_edges_backs_thickness
            active_extend_corners_thickness = extend_corners_backs_thickness
        else:
            active_crop_x, active_crop_y = crop_percent_x, crop_percent_y
            active_fit = fit
            active_extend_edges_thickness = extend_edges_thickness
            active_extend_corners_thickness = extend_corners_thickness

        if active_crop_x > 0 or active_crop_y > 0 or active_fit == FitMode.CROP:
            card_image, bleed_offset_x, bleed_offset_y, synthetic_bleed = (
                crop_and_scale_image(
                    card_image,
                    active_crop_x,
                    active_crop_y,
                    scaled_width,
                    scaled_height,
                    scaled_bleed_width,
                    scaled_bleed_height,
                    active_fit,
                )
            )
        else:
            card_image = card_image.resize((scaled_width, scaled_height))

        if active_extend_edges_thickness > 0:
            card_image = card_image.crop(
                (
                    active_extend_edges_thickness,
                    active_extend_edges_thickness,
                    card_image.width - active_extend_edges_thickness,
                    card_image.height - active_extend_edges_thickness,
                )
            )

        if active_extend_corners_thickness > 0:
            card_image = fill_rounded_corners(
                card_image, active_extend_corners_thickness
            )

        if flip and orientation == Orientation.LANDSCAPE:
            card_image = card_image.rotate(180)

        # Calculate final position
        x = base_x + bleed_offset_x + active_extend_edges_thickness
        y = base_y + bleed_offset_y + active_extend_edges_thickness

        # Calculate total bleed
        edge_bleed_width = synthetic_bleed[0] + active_extend_edges_thickness
        edge_bleed_height = synthetic_bleed[1] + active_extend_edges_thickness

        # Handle edges
        extra_bleed_top = extend_bleed_thickness * (row == 0)
        extra_bleed_bottom = extend_bleed_thickness * (row == num_rows - 1)
        extra_bleed_left = extend_bleed_thickness * (col == 0)
        extra_bleed_right = extend_bleed_thickness * (col == num_cols - 1)

        draw_card_with_bleed(
            card_image,
            base_image,
            x,
            y,
            (edge_bleed_width, edge_bleed_height),
            (extra_bleed_top, extra_bleed_right, extra_bleed_bottom, extra_bleed_left),
        )


# Doesn't save any lines of code but cleans up the call
def draw_card_layouts(
    front_card_images: list[Image.Image | None],
    back_card_images: list[Image.Image | None],
    single_back_image: Image.Image | None,
    base_front_image: Image.Image,
    base_back_image: Image.Image,
    num_rows: int,
    num_cols: int,
    x_pos: list[int],
    y_pos: list[int],
    width: int,
    height: int,
    print_bleed: tuple[int, int],
    crop: tuple[float, float],
    crop_backs: tuple[float, float],
    ppi_ratio: float,
    extend_edges: int,
    extend_edges_backs: int,
    extend_corners_radius: int,
    extend_corners_backs_radius: int,
    extend_bleed: int,
    extend_bleed_backs: int,
    fit: FitMode,
    fit_backs: FitMode,
    orientation: Orientation,
) -> None:
    draw_card_layout(
        front_card_images,
        single_back_image,
        base_front_image,
        num_rows,
        num_cols,
        x_pos,
        y_pos,
        width,
        height,
        print_bleed,
        crop,
        crop_backs,
        ppi_ratio,
        extend_edges,
        extend_edges_backs,
        extend_corners_radius,
        extend_corners_backs_radius,
        extend_bleed,
        flip=False,
        fit=fit,
        fit_backs=fit_backs,
        orientation=orientation,
    )

    draw_card_layout(
        back_card_images,
        single_back_image,
        base_back_image,
        num_rows,
        num_cols,
        x_pos,
        y_pos,
        width,
        height,
        print_bleed,
        crop,
        crop_backs,
        ppi_ratio,
        extend_edges,
        extend_edges_backs,
        extend_corners_radius,
        extend_corners_backs_radius,
        extend_bleed_backs,
        flip=True,
        fit=fit,
        fit_backs=fit_backs,
        orientation=orientation,
    )


def draw_outline(
    page: Image.Image,
    x_pos: list[int],
    y_pos: list[int],
    card_width_px: int,
    card_height_px: int,
    radius_px: int,
    ppi_ratio: float,
) -> None:
    draw = ImageDraw.Draw(page)
    scaled_w = math.floor(card_width_px * ppi_ratio)
    scaled_h = math.floor(card_height_px * ppi_ratio)
    scaled_r = math.floor(radius_px * ppi_ratio)

    for x in x_pos:
        for y in y_pos:
            sx = math.floor(x * ppi_ratio)
            sy = math.floor(y * ppi_ratio)
            draw.rounded_rectangle(
                [sx, sy, sx + scaled_w, sy + scaled_h],
                radius=scaled_r,
                outline="white",
                width=1,
            )


def draw_outlines(
    pages: list[Image.Image],
    x_pos: list[int],
    y_pos: list[int],
    card_width_px: int,
    card_height_px: int,
    radius_px: int,
    ppi_ratio: float,
) -> None:
    for page in pages:
        draw_outline(
            page,
            x_pos,
            y_pos,
            card_width_px,
            card_height_px,
            radius_px,
            ppi_ratio,
        )
