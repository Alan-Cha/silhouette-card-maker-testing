# ==============================================================================
# images.py
#     Place images on the page and perform non-crop manipulations
# ==============================================================================
import math

from pathlib import Path
from PIL import Image, ImageOps

from src import measurements
from src.enums import FitMode

# Approximately 1.25mm of bleed in px assuming 300ppi: ceil(1.25mm * 1in/25.4mm * 300px/1in)
MINIMUM_BLEED = 15


def calculate_max_print_bleed(
    x_pos: list[int],
    y_pos: list[int],
    width: int,
    height: int,
    min_bleed: int = 0
) -> tuple[int, int]:

    def max_bleed(positions: list[int], size: int) -> int:
        if len(positions) < 2:
            return min_bleed

        positions = sorted(positions)
        return max(0, math.ceil((positions[1] - positions[0] - size) / 2))

    return max_bleed(x_pos, width), max_bleed(y_pos, height)


def fill_rounded_corners(card_image: Image.Image, corner_radius: int) -> Image.Image:
    result = card_image.copy()
    width, height = result.size

    # [top-left, top-right, bottom-left, bottom-right]
    corners = [
        ((0, 0), (corner_radius, corner_radius)),
        ((width, 0), (width - corner_radius, corner_radius)),
        ((0, height), (corner_radius, height - corner_radius)),
        ((width, height), (width - corner_radius, height - corner_radius)),
    ]

    for (corner_x, corner_y), (arc_cx, arc_cy) in corners:
        # Each rounded corner has a square region of size (corner_radius x corner_radius)
        # that contains both the rounded arc and the "cut zone" beyond it
        square_x_start = 0 if corner_x == 0 else width - corner_radius
        square_y_start = 0 if corner_y == 0 else height - corner_radius
        square_x_end = corner_radius if corner_x == 0 else width
        square_y_end = corner_radius if corner_y == 0 else height

        # Process each pixel in this corner's square
        for local_x in range(square_x_start, square_x_end):
            for local_y in range(square_y_start, square_y_end):
                dist = math.sqrt((local_x - arc_cx) ** 2 + (local_y - arc_cy) ** 2)

                if dist > corner_radius:
                    # Angle from arc center to this pixel
                    angle = math.atan2(local_y - arc_cy, local_x - arc_cx)

                    # Project angle onto arc
                    src_x = int(arc_cx + corner_radius * math.cos(angle))
                    src_y = int(arc_cy + corner_radius * math.sin(angle))

                    # Copy the arc pixel outward
                    try:
                        pixel = result.getpixel((src_x, src_y))
                        result.putpixel((local_x, local_y), pixel)
                    except (IndexError, ValueError):
                        pass
    return result


def load_card_image(image_path: str | Path, path_label: str = "") -> Image.Image | None:

    path_label = f"{path_label.strip()} " if path_label else ""

    try:
        image = Image.open(image_path)
        return ImageOps.exif_transpose(image)
    except FileNotFoundError:
        print(f'Cannot get {path_label} image "{image_path}".')
    except OSError as e:
        raise OSError(f'Failed to load {path_label} image "{image_path}": {e}') from e

    return None


def convert_inch_to_crop(
    crop_in: float, card_width_px: int, card_height_px: int
) -> tuple[float, float]:
    # Card dimensions are based on 300 ppi
    card_width_in = card_width_px / 300
    card_height_in = card_height_px / 300

    crop_x_percent = 2 * crop_in / card_width_in * 100
    crop_y_percent = 2 * crop_in / card_height_in * 100

    return (crop_x_percent, crop_y_percent)


def parse_dimension_string(dimension_string: str | None, ppi: int) -> int:
    if dimension_string is None:
        return 0

    valid_units = ["", "mm", "in", "px"]
    amount, unit = measurements.parse_unit_string(dimension_string, valid_units)

    if unit == "mm":
        return math.floor(amount / 25.4 * ppi)
    if unit == "in":
        return math.floor(amount * ppi)
    return int(amount)


def parse_crop_string(
    crop_string: str | None, card_width: int, card_height: int
) -> tuple[float, float]:
    if crop_string is None:
        return 0, 0

    valid_units = ["", "mm", "in", "%"]
    try: 
        amount, unit = measurements.parse_unit_string(crop_string, valid_units)
    except ValueError as e:
        raise ValueError(f"Invalid Crop Format: {crop_string}") from e

    if unit == "mm":
        return convert_inch_to_crop(amount / 25.4, card_width, card_height)
    if unit == "in":
        return convert_inch_to_crop(amount, card_width, card_height)
    # Default unit is %
    return amount, amount


def crop_and_scale_image(
    card_image: Image.Image,
    crop_percent_x: float,
    crop_percent_y: float,
    scaled_width: int,
    scaled_height: int,
    scaled_bleed_width: int,
    scaled_bleed_height: int,
    fit: FitMode = FitMode.STRETCH,
) -> tuple[Image.Image, int, int, tuple[int, int]]:
    # Returns processed image, bleed_offset_x, bleed_offset_y, synthetic_bleed (w,h)

    card_width, card_height = card_image.size

    cropped_width = math.floor(card_width * (1 - (crop_percent_x / 100)))
    cropped_height = math.floor(card_height * (1 - (crop_percent_y / 100)))

    if fit == FitMode.CROP:
        uniform_ratio = min(
            cropped_width / scaled_width, cropped_height / scaled_height
        )
        cropped_scaled_ratio_x = uniform_ratio
        cropped_scaled_ratio_y = uniform_ratio
    else:
        cropped_scaled_ratio_x = cropped_width / scaled_width
        cropped_scaled_ratio_y = cropped_height / scaled_height

    scaled_width_with_bleed = scaled_width + (2 * scaled_bleed_width)
    scaled_height_with_bleed = scaled_height + (2 * scaled_bleed_height)

    unscaled_width_with_bleed = math.floor(
        scaled_width_with_bleed * cropped_scaled_ratio_x
    )
    unscaled_height_with_bleed = math.floor(
        scaled_height_with_bleed * cropped_scaled_ratio_y
    )

    can_bleed_x = unscaled_width_with_bleed <= card_width
    can_bleed_y = unscaled_height_with_bleed <= card_height

    if can_bleed_x and can_bleed_y:
        crop_x = (card_width - unscaled_width_with_bleed) // 2
        crop_y = (card_height - unscaled_height_with_bleed) // 2
        card_image = card_image.crop(
            (crop_x, crop_y, card_width - crop_x, card_height - crop_y)
        )
        card_image = card_image.resize(
            (scaled_width_with_bleed, scaled_height_with_bleed)
        )

        return card_image, -scaled_bleed_width, -scaled_bleed_height, (0, 0)

    if fit == FitMode.CROP:
        if can_bleed_x:
            content_height = min(
                math.floor(scaled_height * cropped_scaled_ratio_y), card_height
            )
            crop_x = (card_width - unscaled_width_with_bleed) // 2
            crop_y = (card_height - content_height) // 2
            card_image = card_image.crop(
                (crop_x, crop_y, card_width - crop_x, card_height - crop_y)
            )
            card_image = card_image.resize((scaled_width_with_bleed, scaled_height))
            return card_image, -scaled_bleed_width, 0, (0, scaled_bleed_height)
        if can_bleed_y:
            content_width = min(
                math.floor(scaled_width * cropped_scaled_ratio_x), card_width
            )
            crop_x = (card_width - content_width) // 2
            crop_y = (card_height - unscaled_height_with_bleed) // 2
            card_image = card_image.crop(
                (crop_x, crop_y, card_width - crop_x, card_height - crop_y)
            )
            card_image = card_image.resize((scaled_width, scaled_height_with_bleed))
            return card_image, 0, -scaled_bleed_height, (scaled_bleed_width, 0)

        content_width = min(
            math.floor(scaled_width * cropped_scaled_ratio_x), card_width
        )
        content_height = min(
            math.floor(scaled_height * cropped_scaled_ratio_y), card_height
        )
        crop_x = (card_width - content_width) // 2
        crop_y = (card_height - content_height) // 2
        card_image = card_image.crop(
            (crop_x, crop_y, card_width - crop_x, card_height - crop_y)
        )
        card_image = card_image.resize((scaled_width, scaled_height))
        return card_image, 0, 0, (scaled_bleed_width, scaled_bleed_height)

    # STRETCH fallback
    crop_x = card_width * (crop_percent_x / 100) // 2
    crop_y = card_height * (crop_percent_y / 100) // 2
    card_image = card_image.crop(
        (crop_x, crop_y, card_width - crop_x, card_height - crop_y)
    )
    card_image = card_image.resize((scaled_width, scaled_height))
    return card_image, 0, 0, (scaled_bleed_width, scaled_bleed_height)
