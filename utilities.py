from enum import Enum
import itertools
import json
import math
import filetype
import os
import re
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional
from xml.dom import ValidationErr

from concurrent.futures import ThreadPoolExecutor

from natsort import natsorted
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
# Allow very large images for high-DPI PDF generation without spurious warnings
Image.MAX_IMAGE_PIXELS = None
from pydantic import BaseModel, model_validator

import page_manager
import size_convert
from enums import Registration, Orientation

# Specify directory locations
asset_directory = 'assets'

layouts_filename = 'layouts.json'
layouts_path = os.path.join(asset_directory, layouts_filename)

# Specify valid mimetypes for images
# List can be found here: https://github.com/h2non/filetype.py?tab=readme-ov-file#image
# Pillow suported formats: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
valid_mimetypes = (
    # "image/vnd.dwg",
    # "image/x-xcf",
    "image/jpeg",
    "image/jpx",
    # "image/jxl",
    "image/png",
    "image/apng",
    "image/gif",
    "image/webp",
    # "image/x-canon-cr2",
    "image/tiff",
    "image/bmp",
    # "image/vnd.ms-photo",
    # "image/vnd.adobe.photoshop",
    # "image/x-icon",
    # "image/heic",
    "image/avif",
    "image/qoi",
    "image/dds"
)

# Approximately 1.25mm of bleed assuming 300 PPI: ceil(1.25mm * 1in/25.4mm * 300ppi)
MINIMUM_BLEED = 15


class CardSizeDef(BaseModel):
    width: str
    height: str
    radius: Optional[str] = None
    aliases: Optional[List[str]] = None



class RegistrationSettings(BaseModel):
    inset: Optional[str] = None
    thickness: Optional[str] = None
    length: Optional[str] = None


class DefaultSettings(BaseModel):
    card_radius: str
    registration: RegistrationSettings


class SpecialtyCardSizeDef(BaseModel):
    name: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    radius: Optional[str] = None


class SpecialtyPaperSizeDef(BaseModel):
    name: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None


class SpecialtyLayoutDef(BaseModel):
    card_size: SpecialtyCardSizeDef
    paper_size: SpecialtyPaperSizeDef
    orientation: Orientation = Orientation.LANDSCAPE
    version: int = 1
    num_rows: Optional[int] = None
    num_cols: Optional[int] = None
    registration: Optional[RegistrationSettings] = None


class FitMode(str, Enum):
    STRETCH = "stretch"
    CROP = "crop"

class PaperSizeDef(BaseModel):
    width: str
    height: str
    aliases: Optional[List[str]] = None

    @model_validator(mode='after')
    def width_gte_height(self) -> 'PaperSizeDef':
        w = size_convert.size_to_mm(self.width)
        h = size_convert.size_to_mm(self.height)
        if w < h:
            raise ValueError(f'Paper width ({self.width}) must be >= height ({self.height}). Paper sizes are stored as landscape.')
        return self

class CardLayout(BaseModel):
    orientation: Orientation
    version: int
    num_rows: Optional[int] = None
    num_cols: Optional[int] = None
    registration: Optional[RegistrationSettings] = None

class LayoutConfig(BaseModel):
    ppi: int
    defaults: DefaultSettings
    card_sizes: Dict[str, CardSizeDef]
    paper_sizes: Dict[str, PaperSizeDef]
    layouts: Dict[str, Dict[str, CardLayout]]
    specialty_layouts: Optional[Dict[str, SpecialtyLayoutDef]] = None


def load_layout_config() -> LayoutConfig:
    """Load and validate layouts.json from the assets directory."""
    with open(layouts_path, 'r') as f:
        return LayoutConfig(**json.load(f))


def resolve_card_size_alias(layout_config: LayoutConfig, card_size: str) -> str:
    """Resolve a card size alias to its canonical name. Returns the original if not an alias."""
    for name, card_def in layout_config.card_sizes.items():
        if card_def.aliases and card_size in card_def.aliases:
            print(f'Card size "{card_size}" is an alias of "{name}". Using "{name}" card size and cutting template.')
            return name
    return card_size


def resolve_paper_size_alias(layout_config: LayoutConfig, paper_size: str) -> str:
    """Resolve a paper size alias to its canonical name. Returns the original if not an alias."""
    for name, paper_def in layout_config.paper_sizes.items():
        if paper_def.aliases and paper_size in paper_def.aliases:
            print(f'Paper size "{paper_size}" is an alias of "{name}". Using "{name}" paper size and cutting template.')
            return name
    return paper_size


def get_all_card_size_names(layout_config: LayoutConfig) -> List[str]:
    """Return all valid card size names: canonical names and their aliases.
    standard, poker, bridge first; then alphabetical; then names starting with a digit."""
    names = list(layout_config.card_sizes.keys())
    for card_def in layout_config.card_sizes.values():
        if card_def.aliases:
            names.extend(card_def.aliases)
    priority = ["standard", "poker", "bridge"]
    priority_names = [n for n in priority if n in names]
    rest = sorted((n for n in names if n not in priority), key=lambda n: (n[0].isdigit(), n))
    return priority_names + rest


def get_all_paper_size_names(layout_config: LayoutConfig) -> List[str]:
    """Return all valid paper size names: canonical names and their aliases.
    letter, tabloid, a4, a3, arch_b first; then alphabetical; then names starting with a digit."""
    names = list(layout_config.paper_sizes.keys())
    for paper_def in layout_config.paper_sizes.values():
        if paper_def.aliases:
            names.extend(paper_def.aliases)
    priority = ["letter", "tabloid", "a4", "a3", "arch_b"]
    priority_names = [n for n in priority if n in names]
    rest = sorted((n for n in names if n not in priority), key=lambda n: (n[0].isdigit(), n))
    return priority_names + rest


def get_all_specialty_layout_names(layout_config: LayoutConfig) -> List[str]:
    """Return all specialty layout names, sorted alphabetically."""
    if not layout_config.specialty_layouts:
        return []
    return sorted(layout_config.specialty_layouts.keys())


def template_name(paper_size: str, card_size: str, version: int) -> str:
    """Compose the standard template name: {paper_size}-{card_size}-v{version}."""
    return f"{paper_size}-{card_size}-v{version}"


# Known junk files across OSes
EXTRANEOUS_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "Icon\r",  # macOS oddball
}

def parse_crop_string(crop_string: str | None, card_width: int, card_height: int) -> tuple[float, float]:
    """
    Calculates crop based on various formats.

    "9" -> (9, 9)
    "3mm" -> calls function to determine mm crop
    "3in" -> calls function to determine in crop
    """
    if crop_string is None:
        return 0, 0

    crop_string = crop_string.strip().lower()

    float_pattern = r"(?:\d+\.\d*|\.\d+|\d+)"  # matches 1.0, .5, or 2

    # Match "3mm" or "3.5mm"
    mm_match = re.fullmatch(rf"({float_pattern})mm", crop_string)
    if mm_match:
        crop_mm = float(mm_match.group(1))
        return convertInToCrop(crop_mm / 25.4, card_width, card_height)

    # Match "0.1in" or "0.125in"
    in_match = re.fullmatch(rf"({float_pattern})in", crop_string)
    if in_match:
        crop_in = float(in_match.group(1))
        return convertInToCrop(crop_in, card_width, card_height)

    # Match single float like "6.5" or "4.5"
    single_match = re.fullmatch(float_pattern, crop_string)
    if single_match:
        num = float(crop_string)
        return num, num

    raise ValueError(f"Invalid crop format: '{crop_string}'")

def convertInToCrop(crop_in: float, card_width_px: int, card_height_px: int) -> tuple[float, float]:
    # Convert from pixels to physical mm using DPI
    # Card dimensions are based on 300 ppi
    card_width_mm = card_width_px / 300
    card_height_mm = card_height_px / 300

    crop_x_percent = 2 * crop_in / card_width_mm * 100
    crop_y_percent = 2 * crop_in / card_height_mm * 100

    return (crop_x_percent, crop_y_percent)

def delete_hidden_files_in_directory(path: str):
    if len(path) > 0:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path) and (file in EXTRANEOUS_FILES or file.startswith("._")):
                try:
                    os.remove(full_path)
                    print(f"Removed hidden file: {full_path}")
                except OSError as e:
                    print(f"Could not remove {full_path}: {e}")

def get_directory(path):
    if os.path.isdir(path):
        return os.path.abspath(path)
    else:
        return os.path.abspath(os.path.dirname(path))

def ensure_directory(path: str) -> str:
    """Create directory and any missing parent directories. Returns the path."""
    os.makedirs(path, exist_ok=True)
    return path

def ensure_output_directory(output_path: str) -> None:
    """Create the parent directory of output_path if it doesn't exist."""
    parent = os.path.dirname(os.path.abspath(output_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

def get_image_file_paths(dir_path: str) -> List[str]:
    result = []

    for current_folder, _, files in os.walk(dir_path):
        for filename in files:
            full_path = os.path.join(current_folder, filename)

            # Skip invalid files
            if filetype.guess_mime(full_path) not in valid_mimetypes:
                continue

            relative_path = os.path.relpath(full_path, dir_path)
            result.append(relative_path)

    return result

def get_back_card_image_path(back_dir_path) -> str | None:
    # List all files in the directory that are pngs and jpegs
    # The directory may contain markdown and/or other files
    files = [f for f in Path(back_dir_path).glob("*") if f.is_file() and filetype.guess_mime(f) in valid_mimetypes]

    if len(files) == 0:
        return None

    if len(files) == 1:
        return files[0]

    # Multiple back files detected, provide a selection menu
    for i, f in enumerate(files):
        print(f'[{i + 1}] {f}')

    while True:
        choice = input("Select a back image (enter the number): ")

        if not choice.isdigit():
            continue

        index = int(choice) - 1
        if index >= 0 and index < len(files):
            break

    return files[index]

def crop_and_scale_image(
    card_image: Image.Image,
    crop_percent_x: float,
    crop_percent_y: float,
    scaled_width: int,
    scaled_height: int,
    scaled_bleed_width: int,
    scaled_bleed_height: int,
    fit: FitMode = FitMode.STRETCH
) -> tuple[Image.Image, int, int, tuple[int, int]]:
    cw, ch = card_image.size

    cropped_w = math.floor(cw * (1 - crop_percent_x / 100))
    cropped_h = math.floor(ch * (1 - crop_percent_y / 100))

    if fit == FitMode.CROP:
        ratio = min(cropped_w / scaled_width, cropped_h / scaled_height)
        ratio_x = ratio_y = ratio
    else:
        ratio_x = cropped_w / scaled_width
        ratio_y = cropped_h / scaled_height

    scaled_w_bleed = scaled_width + 2 * scaled_bleed_width
    scaled_h_bleed = scaled_height + 2 * scaled_bleed_height

    unscaled_w_bleed = math.floor(scaled_w_bleed * ratio_x)
    unscaled_h_bleed = math.floor(scaled_h_bleed * ratio_y)

    can_x = unscaled_w_bleed <= cw
    can_y = unscaled_h_bleed <= ch

    if can_x and can_y:
        cx = (cw - unscaled_w_bleed) // 2
        cy = (ch - unscaled_h_bleed) // 2
        img = card_image.resize(
            (scaled_w_bleed, scaled_h_bleed),
            resample=Image.Resampling.BILINEAR,
            box=(cx, cy, cw - cx, ch - cy)
        )
        return img, -scaled_bleed_width, -scaled_bleed_height, (0, 0)

    if fit == FitMode.CROP:
        if can_x:
            content_h = min(math.floor(scaled_height * ratio_y), ch)
            cx = (cw - unscaled_w_bleed) // 2
            cy = (ch - content_h) // 2
            img = card_image.resize(
                (scaled_w_bleed, scaled_height),
                resample=Image.Resampling.BILINEAR,
                box=(cx, cy, cw - cx, ch - cy)
            )
            return img, -scaled_bleed_width, 0, (0, scaled_bleed_height)

        if can_y:
            content_w = min(math.floor(scaled_width * ratio_x), cw)
            cx = (cw - content_w) // 2
            cy = (ch - unscaled_h_bleed) // 2
            img = card_image.resize(
                (scaled_width, scaled_h_bleed),
                resample=Image.Resampling.BILINEAR,
                box=(cx, cy, cw - cx, ch - cy)
            )
            return img, 0, -scaled_bleed_height, (scaled_bleed_width, 0)

        content_w = min(math.floor(scaled_width * ratio_x), cw)
        content_h = min(math.floor(scaled_height * ratio_y), ch)
        cx = (cw - content_w) // 2
        cy = (ch - content_h) // 2
        img = card_image.resize(
            (scaled_width, scaled_height),
            resample=Image.Resampling.BILINEAR,
            box=(cx, cy, cw - cx, ch - cy)
        )
        return img, 0, 0, (scaled_bleed_width, scaled_bleed_height)

    cx = cw * (crop_percent_x / 100) // 2
    cy = ch * (crop_percent_y / 100) // 2
    img = card_image.resize(
        (scaled_width, scaled_height),
        resample=Image.Resampling.BILINEAR,
        box=(cx, cy, cw - cx, ch - cy)
    )
    return img, 0, 0, (scaled_bleed_width, scaled_bleed_height)


def draw_card_with_bleed(card_image: Image.Image, base_image: Image.Image, x: int, y: int, print_bleed: tuple[int, int]):
    bleed_w, bleed_h = print_bleed
    w, h = card_image.size
    base_image.paste(card_image, (x, y))

    if bleed_h > 0:
        top = card_image.resize((w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, 0, w, 1))
        base_image.paste(top, (x, y - bleed_h))
        bottom = card_image.resize((w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, h - 1, w, h))
        base_image.paste(bottom, (x, y + h))

    if bleed_w > 0:
        left = card_image.resize((bleed_w, h), resample=Image.Resampling.NEAREST, box=(0, 0, 1, h))
        base_image.paste(left, (x - bleed_w, y))
        right = card_image.resize((bleed_w, h), resample=Image.Resampling.NEAREST, box=(w - 1, 0, w, h))
        base_image.paste(right, (x + w, y))

    if bleed_w > 0 and bleed_h > 0:
        tl = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, 0, 1, 1))
        base_image.paste(tl, (x - bleed_w, y - bleed_h))
        tr = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(w - 1, 0, w, 1))
        base_image.paste(tr, (x + w, y - bleed_h))
        bl = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, h - 1, 1, h))
        base_image.paste(bl, (x - bleed_w, y + h))
        br = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(w - 1, h - 1, w, h))
        base_image.paste(br, (x + w, y + h))

    return base_image


def compose_card_with_bleed(card_image: Image.Image, print_bleed: tuple[int, int]) -> Image.Image:
    bleed_w, bleed_h = print_bleed
    w, h = card_image.size
    total_w = w + 2 * bleed_w
    total_h = h + 2 * bleed_h
    result = Image.new('RGB', (total_w, total_h), 'white')
    result.paste(card_image, (bleed_w, bleed_h))

    if bleed_h > 0:
        top = card_image.resize((w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, 0, w, 1))
        result.paste(top, (bleed_w, 0))
        bottom = card_image.resize((w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, h - 1, w, h))
        result.paste(bottom, (bleed_w, h + bleed_h))

    if bleed_w > 0:
        left = card_image.resize((bleed_w, h), resample=Image.Resampling.NEAREST, box=(0, 0, 1, h))
        result.paste(left, (0, bleed_h))
        right = card_image.resize((bleed_w, h), resample=Image.Resampling.NEAREST, box=(w - 1, 0, w, h))
        result.paste(right, (w + bleed_w, bleed_h))

    if bleed_w > 0 and bleed_h > 0:
        tl = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, 0, 1, 1))
        result.paste(tl, (0, 0))
        tr = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(w - 1, 0, w, 1))
        result.paste(tr, (w + bleed_w, 0))
        bl = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(0, h - 1, 1, h))
        result.paste(bl, (0, h + bleed_h))
        br = card_image.resize((bleed_w, bleed_h), resample=Image.Resampling.NEAREST, box=(w - 1, h - 1, w, h))
        result.paste(br, (w + bleed_w, h + bleed_h))

    return result


def _preprocess_card_image(
    card_image: Image.Image,
    is_back: bool,
    single_back_image: Image.Image,
    scaled_width: int,
    scaled_height: int,
    scaled_bleed_width: int,
    scaled_bleed_height: int,
    extend_corners_thickness: int,
    crop: tuple[float, float],
    crop_backs: tuple[float, float],
    fit: FitMode,
    flip: bool,
    orientation: Orientation,
) -> Image.Image:
    if card_image is None:
        return None

    active_crop = crop_backs if (is_back and card_image is single_back_image) else crop

    if active_crop[0] > 0 or active_crop[1] > 0 or fit == FitMode.CROP:
        card_image, off_x, off_y, syn_bleed = crop_and_scale_image(
            card_image, *active_crop, scaled_width, scaled_height,
            scaled_bleed_width, scaled_bleed_height, fit
        )
    else:
        card_image = card_image.resize((scaled_width, scaled_height), resample=Image.Resampling.BILINEAR)
        syn_bleed = (scaled_bleed_width, scaled_bleed_height)
        off_x = off_y = 0

    if extend_corners_thickness > 0:
        t = extend_corners_thickness
        card_image = card_image.crop((t, t, card_image.width - t, card_image.height - t))

    if flip and orientation == Orientation.LANDSCAPE:
        card_image = card_image.transpose(Image.Transpose.ROTATE_180)

    total_bleed_x = syn_bleed[0] + extend_corners_thickness
    total_bleed_y = syn_bleed[1] + extend_corners_thickness
    if total_bleed_x > 0 or total_bleed_y > 0:
        card_image = compose_card_with_bleed(card_image, (total_bleed_x, total_bleed_y))

    card_image._paste_offset_x = off_x - syn_bleed[0]
    card_image._paste_offset_y = off_y - syn_bleed[1]
    return card_image


def _paste_preprocessed_cards(
    card_images: List[Image.Image | None],
    base_image: Image.Image,
    num_rows: int,
    num_cols: int,
    x_pos: List[int],
    y_pos: List[int],
    ppi_ratio: float,
    flip: bool,
    orientation: Orientation,
):
    for i, card_image in enumerate(card_images):
        if card_image is None:
            continue
        col, row = i % num_cols, i // num_cols
        if flip:
            col, row = (num_cols - col - 1, row) if orientation == Orientation.PORTRAIT else (col, num_rows - row - 1)
        base_x = math.floor(x_pos[col] * ppi_ratio)
        base_y = math.floor(y_pos[row] * ppi_ratio)
        base_image.paste(
            card_image,
            (base_x + card_image._paste_offset_x, base_y + card_image._paste_offset_y),
        )


def draw_card_layout(
    card_images: List[Image.Image | None],
    single_back_image: Image.Image,
    base_image: Image.Image,
    num_rows: int,
    num_cols: int,
    x_pos: List[int],
    y_pos: List[int],
    width: int,
    height: int,
    print_bleed: tuple[int, int],
    crop: tuple[float, float],
    crop_backs: tuple[float, float],
    ppi_ratio: float,
    extend_corners: int,
    flip: bool,
    fit: FitMode,
    orientation: Orientation
):
    num_cards = num_rows * num_cols
    crop_percent_x, crop_percent_y = crop
    crop_backs_percent_x, crop_backs_percent_y = crop_backs

    extend_corners_thickness = math.floor(extend_corners * ppi_ratio)

    # Calculate the size of the card after scaling: "scaled size"
    scaled_width = math.floor(width * ppi_ratio)
    scaled_height = math.floor(height * ppi_ratio)

    scaled_bleed_width = math.ceil(print_bleed[0] * ppi_ratio)
    scaled_bleed_height = math.ceil(print_bleed[1] * ppi_ratio)

    # Fill all the spaces with the card back
    for i, card_image in enumerate(card_images):
        if card_image is None:
            continue

        # Calculate base position from layout
        col = i % num_cards % num_cols
        row = (i % num_cards) // num_cols
        # Long-side flip: landscape flips rows, portrait flips columns
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

        # Determine which crop percentages to use
        if card_image is single_back_image:
            active_crop_x, active_crop_y = crop_backs_percent_x, crop_backs_percent_y
        else:
            active_crop_x, active_crop_y = crop_percent_x, crop_percent_y

        # Apply cropping, scaling, and fit mode
        if active_crop_x > 0 or active_crop_y > 0 or fit == FitMode.CROP:
            card_image, bleed_offset_x, bleed_offset_y, synthetic_bleed = crop_and_scale_image(
                card_image,
                active_crop_x,
                active_crop_y,
                scaled_width,
                scaled_height,
                scaled_bleed_width,
                scaled_bleed_height,
                fit
            )
        else:
            # No percentage crop and STRETCH mode: just scale to target size
            card_image = card_image.resize((scaled_width, scaled_height), resample=Image.Resampling.BILINEAR)

        # Extend the corners if required
        card_image = card_image.crop((
            extend_corners_thickness,
            extend_corners_thickness,
            card_image.width - extend_corners_thickness,
            card_image.height - extend_corners_thickness
        ))

        if flip and orientation == Orientation.LANDSCAPE:
            card_image = card_image.rotate(180)

        # Calculate final position
        x = base_x + bleed_offset_x + extend_corners_thickness
        y = base_y + bleed_offset_y + extend_corners_thickness

        draw_card_with_bleed(card_image, base_image, x, y, (synthetic_bleed[0] + extend_corners_thickness, synthetic_bleed[1] + extend_corners_thickness))

def draw_outline(
    page: Image.Image,
    x_pos: List[int],
    y_pos: List[int],
    card_width_px: int,
    card_height_px: int,
    radius_px: int,
    ppi_ratio: float,
):
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
                outline='white',
                width=1,
            )

def add_front_back_pages(front_page: Image.Image, back_page: Image.Image | None, pages: List[Image.Image], page_width: int, page_height: int, ppi_ratio: float, template: str, only_fronts: bool, label: str, orientation: Orientation, label_margin_px: int):
    font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40 * ppi_ratio)

    num_sheet = len(pages) + 1
    if not only_fronts:
        num_sheet = int(len(pages) / 2) + 1

    label_text = f'sheet: {num_sheet}, template: {template}'
    if label is not None:
        label_text = f'label: {label}, {label_text}'

    if orientation == Orientation.LANDSCAPE:
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1), (0, 0, 0, 0)))
        bbox = temp_draw.textbbox((0, 0), label_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        text_img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
        ImageDraw.Draw(text_img).text((0, 0), label_text, fill=(0, 0, 0), font=font)

        rot = text_img.rotate(-90, expand=True, resample=Image.Resampling.NEAREST)
        paste_x = front_page.width - label_margin_px - rot.width // 2
        paste_y = front_page.height // 2 - rot.height // 2
        front_page.paste(rot, (paste_x, paste_y), rot)
    else:
        draw = ImageDraw.Draw(front_page)
        label_x = math.floor((page_width / 2) * ppi_ratio)
        label_y = math.floor(page_height * ppi_ratio) - label_margin_px
        draw.text((label_x, label_y), label_text, fill=(0, 0, 0), anchor="mm", font=font)

    if orientation == Orientation.PORTRAIT:
        front_page = front_page.rotate(-90, expand=True, resample=Image.Resampling.NEAREST)
        if back_page is not None:
            back_page = back_page.rotate(-90, expand=True, resample=Image.Resampling.NEAREST)

    pages.append(front_page)
    if not only_fronts:
        pages.append(back_page)

def _draw_label(page: Image.Image, text: str, orientation: Orientation,
                page_w: int, page_h: int, ppi_ratio: float, margin: int):
    font = ImageFont.truetype(
        os.path.join(asset_directory, 'arial.ttf'),
        int(40 * ppi_ratio)
    )

    if orientation == Orientation.LANDSCAPE:
        scratch = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        x0, y0, x1, y1 = scratch.textbbox((0, 0), text, font=font)
        tw, th = x1 - x0, y1 - y0

        label = Image.new('RGBA', (tw, th), (255, 255, 255, 0))
        ImageDraw.Draw(label).text((0, 0), text, fill=(0, 0, 0), font=font)
        rot = label.rotate(-90, expand=True, resample=Image.Resampling.NEAREST)

        page.paste(
            rot,
            (page.width - margin - rot.width // 2,
             page.height // 2 - rot.height // 2),
            rot
        )
        return

    draw = ImageDraw.Draw(page)
    draw.text(
        (int(page_w * ppi_ratio / 2), int(page_h * ppi_ratio) - margin),
        text, fill=(0, 0, 0), anchor='mm', font=font
    )

def check_paths_subset(subset: set[str], mainset: set[str]) -> set[str]:
    """Return the items in `subset` whose basenames do NOT appear in `mainset`,
    ignoring extensions."""
    subset_stems = {Path(p).stem: p for p in subset}
    mainset_stems = {Path(p).stem for p in mainset}

    return {orig for stem, orig in subset_stems.items() if stem not in mainset_stems}

def resolve_image_with_any_extension(path: str) -> str:
    """
    If the exact path exists, return it.
    Otherwise search for files with the same stem (basename)
    but any extension. Returns the resolved path or raises.
    """
    p = Path(path)

    # Case 1: exact file exists
    if p.exists():
        return str(p)

    # Case 2: try to find any file with the same stem
    pattern = str(p.with_suffix('')) + ".*"   # e.g. "card1.*"
    matches = glob(pattern)

    if len(matches) == 0:
        raise FileNotFoundError(f"Missing image: {pattern}")

    if len(matches) > 1:
        raise ValueError(f"Ambiguous image match: {matches}")

    return matches[0]

def generate_pdf(
    front_dir_path: str,
    back_dir_path: str,
    ds_dir_path: str,
    output_path: str,
    output_images: bool,
    card_size: str,
    paper_size: str,
    registration: Registration,
    only_fronts: bool,
    fit: FitMode,
    crop_string: str | None,
    crop_backs_string: str | None,
    extend_corners: int,
    ppi: int,
    quality: int,
    skip_indices: List[int],
    load_offset: bool,
    label: str,
    show_outline: bool = False,
    specialty: Optional[str] = None,
    output_format: str = "jpg",
):
    # Sanity checks for the different directories
    f_path = Path(front_dir_path)
    if not f_path.exists() or not f_path.is_dir():
        raise Exception(f'Front image directory path "{f_path}" is invalid.')

    b_path = Path(back_dir_path)
    if not b_path.exists() or not b_path.is_dir():
        raise Exception(f'Back image directory path "{b_path}" is invalid.')

    ds_path = Path(ds_dir_path)
    if not ds_path.exists() or not ds_path.is_dir():
        raise Exception(f'Double-sided image directory path "{ds_path}" is invalid.')

    # Delete hidden files that may affect image fetching
    delete_hidden_files_in_directory(front_dir_path)
    delete_hidden_files_in_directory(back_dir_path)
    delete_hidden_files_in_directory(ds_dir_path)

    # Sanity check for output images
    if output_images:
        output_path = get_directory(output_path)
    else:
        if not output_path.lower().endswith(".pdf"):
            raise Exception(f'Cannot save PDF to output path "{output_path}" because it is not a valid PDF file path.')
        ensure_output_directory(output_path)

    # Get the back image, if it exists
    back_card_image_path = None
    use_default_back_page = True
    if not only_fronts:
        back_card_image_path = get_back_card_image_path(back_dir_path)
        use_default_back_page = back_card_image_path is None
        if use_default_back_page:
            print(f'No back image provided in back image directory \"{back_dir_path}\". Using default instead.')

    front_image_filenames = get_image_file_paths(front_dir_path)
    ds_image_filenames = get_image_file_paths(ds_dir_path)

    # Check if double-sided back images has matching front images
    front_set = set(front_image_filenames)
    ds_set = set(ds_image_filenames)
    diff = check_paths_subset(ds_set, front_set)
    if len(diff) > 0:
        raise Exception(f'Double-sided backs "{ds_set - front_set}" do not have matching fronts. Add the missing fronts to front image directory "{front_dir_path}".')

    if only_fronts:
        if len(ds_set) > 0:
            raise Exception(f'Cannot use "--only_fronts" with double-sided cards. Remove cards from double-side image directory "{ds_dir_path}".')

    layout_config = load_layout_config()
    default_reg = layout_config.defaults.registration

    if specialty:
        if not layout_config.specialty_layouts or specialty not in layout_config.specialty_layouts:
            raise Exception(f'Specialty layout "{specialty}" not found.')
        spec = layout_config.specialty_layouts[specialty]

        # Resolve card size
        if spec.card_size.name:
            if spec.card_size.name not in layout_config.card_sizes:
                raise Exception(f'Card size "{spec.card_size.name}" not found in card_sizes.')
            base = layout_config.card_sizes[spec.card_size.name]
            card_size_def = CardSizeDef(
                width=base.width,
                height=base.height,
                radius=spec.card_size.radius or base.radius,
            )
        else:
            card_size_def = CardSizeDef(
                width=spec.card_size.width,
                height=spec.card_size.height,
                radius=spec.card_size.radius,
            )

        # Resolve paper size
        if spec.paper_size.name:
            if spec.paper_size.name not in layout_config.paper_sizes:
                raise Exception(f'Paper size "{spec.paper_size.name}" not found in paper_sizes.')
            paper_size_def = layout_config.paper_sizes[spec.paper_size.name]
        else:
            paper_size_def = PaperSizeDef(
                width=spec.paper_size.width,
                height=spec.paper_size.height,
            )

        orientation = spec.orientation
        template = f"{specialty}-v{spec.version}"

        lr = spec.registration or RegistrationSettings()
        effective_inset = lr.inset or default_reg.inset
        effective_thickness = lr.thickness or default_reg.thickness
        effective_length = lr.length or default_reg.length

    else:
        # Resolve aliases
        card_size = resolve_card_size_alias(layout_config, card_size)
        paper_size = resolve_paper_size_alias(layout_config, paper_size)

        # Validate card size
        if card_size not in layout_config.card_sizes:
            raise Exception(f'Unsupported card size "{card_size}". Try card sizes: {list(layout_config.card_sizes.keys())}.')
        card_size_def = layout_config.card_sizes[card_size]

        # Validate paper size
        if paper_size not in layout_config.paper_sizes:
            raise Exception(f'Unsupported paper size "{paper_size}". Try paper sizes: {list(layout_config.paper_sizes.keys())}.')
        paper_size_def = layout_config.paper_sizes[paper_size]

        # Look up orientation and version from the layouts field (per paper+card combination)
        if paper_size not in layout_config.layouts or card_size not in layout_config.layouts[paper_size]:
            raise Exception(f'No layout defined for paper "{paper_size}" with card "{card_size}". Add it to layouts.json.')
        layout_def = layout_config.layouts[paper_size][card_size]
        orientation = layout_def.orientation
        version = layout_def.version

        # Effective registration: merge per-layout overrides on top of defaults
        layout_reg = layout_def.registration
        lr = layout_reg or RegistrationSettings()
        effective_inset = lr.inset or default_reg.inset
        effective_thickness = lr.thickness or default_reg.thickness
        effective_length = lr.length or default_reg.length

        template = template_name(paper_size, card_size, version)

    # Corner exclusion zone = configured mark length + padding constant
    total_exclusion_mm = size_convert.size_to_mm(default_reg.length) + page_manager.REG_PADDING_MM
    computed = page_manager.generate_layout(
        orientation=orientation,
        card_width=card_size_def.width,
        card_height=card_size_def.height,
        paper_width=paper_size_def.width,
        paper_height=paper_size_def.height,
        inset=effective_inset,
        length=f"{total_exclusion_mm}mm",
        ppi=layout_config.ppi,
    )

    card_width_px = computed.card_width_px
    card_height_px = computed.card_height_px
    page_width_px = computed.paper_width_px
    page_height_px = computed.paper_height_px
    x_pos = computed.x_pos
    y_pos = computed.y_pos

    # Determine the amount of x and y crop
    crop = parse_crop_string(crop_string, card_width_px, card_height_px)
    crop_backs = parse_crop_string(crop_backs_string, card_width_px, card_height_px)

    # Convert corner radius to pixels for outline drawing
    effective_card_radius = card_size_def.radius or layout_config.defaults.card_radius
    radius_px = size_convert.size_to_pixel(effective_card_radius, layout_config.ppi)

    num_rows = len(y_pos)
    num_cols = len(x_pos)
    num_cards = num_rows * num_cols

    if num_cards == 0:
        raise Exception(f'Card size "{card_size}" does not fit on paper size "{paper_size}".')

    # Check skip indices
    # You can only skip valid indices (within the max card count per page)
    clean_skip_indices = [n for n in skip_indices if n < num_cards]
    ignore_skip_indices = [n for n in skip_indices if n >= num_cards]

    if len(ignore_skip_indices) > 0:
        print(f'Ignoring skip indices that are outside range 0-{num_cards - 1}: {ignore_skip_indices}')

    # If all possible cards are skipped, this may result in an infinite loop
    if len(clean_skip_indices) == num_cards:
        raise Exception(f'You cannot skip all cards per page')

    ppi_ratio = ppi / 300

    inset_px = size_convert.size_to_pixel(effective_inset, layout_config.ppi)
    label_margin_px = math.floor((inset_px - 2 * MINIMUM_BLEED) * ppi_ratio)

    max_print_bleed = calculate_max_print_bleed(x_pos, y_pos, card_width_px, card_height_px, MINIMUM_BLEED)

    scaled_width = math.floor(card_width_px * ppi_ratio)
    scaled_height = math.floor(card_height_px * ppi_ratio)
    scaled_bleed_width = math.ceil(max_print_bleed[0] * ppi_ratio)
    scaled_bleed_height = math.ceil(max_print_bleed[1] * ppi_ratio)
    extend_corners_thickness = math.floor(extend_corners * ppi_ratio)

    pw_mm = size_convert.size_to_mm(paper_size_def.width)
    ph_mm = size_convert.size_to_mm(paper_size_def.height)
    if orientation == Orientation.PORTRAIT:
        pw_mm, ph_mm = ph_mm, pw_mm
    page_w = int(pw_mm / 25.4 * ppi)
    page_h = int(ph_mm / 25.4 * ppi)

    inset_mm, thick_mm, len_mm = page_manager._constrain_reg_params(
        size_convert.size_to_mm(effective_inset),
        size_convert.size_to_mm(effective_thickness),
        size_convert.size_to_mm(effective_length),
    )
    len_mm = min(len_mm, computed.max_length_mm)
    mm_to_px = ppi / 25.4
    inset_px = int(inset_mm * mm_to_px)
    thick_px = max(1, int(thick_mm * mm_to_px))
    length_px = int(len_mm * mm_to_px)
    sq_px = int(round((5 + thick_mm) * mm_to_px))

    pages: List[Image.Image] = []
    sheet_num = 0

    if output_images:
        os.makedirs(output_path, exist_ok=True)

    # Load and cache the single back image for reuse
    single_back_image = None
    single_back_image_preprocessed = None
    if not only_fronts and not use_default_back_page:
        try:
            single_back_image = Image.open(back_card_image_path)
            ImageOps.exif_transpose(single_back_image, in_place=True)
        except FileNotFoundError:
            print(f'Cannot get back image "{back_card_image_path}". Using default instead.')
            single_back_image = None
        except OSError as e:
            raise OSError(f'Failed to load back image "{back_card_image_path}": {e}') from e

        if single_back_image is not None:
            single_back_image_preprocessed = _preprocess_card_image(
                single_back_image,
                is_back=True,
                single_back_image=single_back_image,
                scaled_width=scaled_width,
                scaled_height=scaled_height,
                scaled_bleed_width=scaled_bleed_width,
                scaled_bleed_height=scaled_bleed_height,
                extend_corners_thickness=extend_corners_thickness,
                crop=crop,
                crop_backs=crop_backs,
                fit=fit,
                flip=True,
                orientation=orientation,
            )

    images_to_close: list[Image.Image] = []

    def _process_one(file: str):
        front_path = os.path.join(front_dir_path, file)
        front_path = resolve_image_with_any_extension(front_path)
        raw_front = Image.open(front_path)
        ImageOps.exif_transpose(raw_front, in_place=True)
        front_img = _preprocess_card_image(
            raw_front,
            is_back=False,
            single_back_image=single_back_image,
            scaled_width=scaled_width,
            scaled_height=scaled_height,
            scaled_bleed_width=scaled_bleed_width,
            scaled_bleed_height=scaled_bleed_height,
            extend_corners_thickness=extend_corners_thickness,
            crop=crop,
            crop_backs=crop_backs,
            fit=fit,
            flip=False,
            orientation=orientation,
        )
        raw_front.close()

        if only_fronts:
            back_img = None
        elif file in ds_set:
            ds_path = os.path.join(ds_dir_path, file)
            ds_path = resolve_image_with_any_extension(ds_path)
            raw_back = Image.open(ds_path)
            ImageOps.exif_transpose(raw_back, in_place=True)
            back_img = _preprocess_card_image(
                raw_back,
                is_back=True,
                single_back_image=single_back_image,
                scaled_width=scaled_width,
                scaled_height=scaled_height,
                scaled_bleed_width=scaled_bleed_width,
                scaled_bleed_height=scaled_bleed_height,
                extend_corners_thickness=extend_corners_thickness,
                crop=crop,
                crop_backs=crop_backs,
                fit=fit,
                flip=True,
                orientation=orientation,
            )
            raw_back.close()
        else:
            back_img = single_back_image_preprocessed

        return front_img, back_img

    all_files = natsorted(list(check_paths_subset(front_set, ds_set))) + natsorted(list(ds_set))
    it = iter(all_files)
    n = 0
    total = len(all_files)
    while True:
        file_group = list(itertools.islice(it, num_cards - len(clean_skip_indices)))
        if not file_group:
            break

        sheet_num += 1

        front_cards: List[Image.Image | None] = [None] * num_cards
        back_cards: List[Image.Image | None] = [None] * num_cards

        slots = []
        fg_it = iter(file_group)
        for i in range(num_cards):
            if i in clean_skip_indices:
                continue
            try:
                f = next(fg_it)
            except StopIteration:
                break
            slots.append((i, f))

        # Preprocess cards in parallel; PIL releases the GIL during C ops
        if len(slots) > 1:
            workers = min(len(slots), os.cpu_count() or 1)
            with ThreadPoolExecutor(max_workers=workers) as ex:
                results = list(ex.map(_process_one, (f for _, f in slots)))
        else:
            results = [_process_one(f) for _, f in slots]

        for (i, f), (front, back) in zip(slots, results):
            n += 1
            print(f'\r{n}/{total} {f}', end='', flush=True)

            images_to_close.append(front)
            front_cards[i] = front

            if back is not None and back is not single_back_image_preprocessed:
                images_to_close.append(back)
            back_cards[i] = back

        front = Image.new('RGB', (page_w, page_h), 'white')
        page_manager.draw_reg_mark_pil(front, inset_px, thick_px, length_px, sq_px, registration)
        _paste_preprocessed_cards(front_cards, front, num_rows, num_cols, x_pos, y_pos,
                                  ppi_ratio, flip=False, orientation=orientation)
        if show_outline:
            draw_outline(front, x_pos, y_pos, card_width_px, card_height_px, radius_px, ppi_ratio)
        text = f'sheet: {sheet_num}, template: {template}'
        if label is not None:
            text = f'label: {label}, {text}'
        _draw_label(front, text, orientation, page_width_px, page_height_px, ppi_ratio, label_margin_px)

        if not output_images and orientation == Orientation.PORTRAIT:
            front = front.rotate(-90, expand=True, resample=Image.Resampling.NEAREST)

        if not only_fronts:
            back = Image.new('RGB', (page_w, page_h), 'white')
            page_manager.draw_reg_mark_pil(back, inset_px, thick_px, length_px, sq_px, registration)
            _paste_preprocessed_cards(back_cards, back, num_rows, num_cols, x_pos, y_pos,
                                      ppi_ratio, flip=True, orientation=orientation)
            if show_outline:
                draw_outline(back, x_pos, y_pos, card_width_px, card_height_px, radius_px, ppi_ratio)
            if not output_images and orientation == Orientation.PORTRAIT:
                back = back.rotate(-90, expand=True, resample=Image.Resampling.NEAREST)
        else:
            back = None

        if output_images:
            ext = 'png' if output_format == 'png' else 'jpg'
            kwargs = dict(format='PNG') if output_format == 'png' else dict(
                format='JPEG', quality=(quality if quality is not None else 95)
            )
            front.save(os.path.join(output_path, f'page{2 * sheet_num - 1}.{ext}'),
                       dpi=(ppi, ppi), **kwargs)
            front.close()
            if back is not None:
                back.save(os.path.join(output_path, f'page{2 * sheet_num}.{ext}'),
                          dpi=(ppi, ppi), **kwargs)
                back.close()
        else:
            pages.append(front)
            if back is not None:
                pages.append(back)

    print()
    for img in images_to_close:
        img.close()
    if single_back_image_preprocessed is not None:
        single_back_image_preprocessed.close()
    if single_back_image is not None:
        single_back_image.close()

    if output_images:
        if sheet_num == 0:
            print('No pages were generated')
            return
        print(f'Generated images: {output_path}')
        return

    if len(pages) == 0:
        print('No pages were generated')
        return

    if load_offset:
        saved_offset = load_saved_offset()
        if saved_offset is None:
            print('Offset cannot be applied')
        else:
            print(f'Loaded x offset: {saved_offset.x_offset}, y offset: {saved_offset.y_offset}, angle offset: {saved_offset.angle_offset}')
            pages = offset_images(pages, saved_offset.x_offset, saved_offset.y_offset, ppi, saved_offset.angle_offset)

    print(f'\nSaving PDF ({len(pages)} pages at {ppi} PPI)...')
    save_kwargs = dict(resolution=math.floor(300 * ppi_ratio))
    if quality is not None:
        save_kwargs['quality'] = quality
    pages[0].save(output_path, format='PDF', save_all=True, append_images=pages[1:], **save_kwargs)
    print(f'Generated PDF: {output_path}')

class OffsetData(BaseModel):
    x_offset: int
    y_offset: int
    angle_offset: float = 0.0

def save_offset(x_offset: int, y_offset: int, angle_offset: float = 0.0) -> None:
    # Create the directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save the offset data to a JSON file
    with open('data/offset_data.json', 'w') as offset_file:
        offset_file.write(OffsetData(x_offset=x_offset, y_offset=y_offset, angle_offset=angle_offset).model_dump_json(indent=4))

    print('Offset data saved!')

def load_saved_offset() -> OffsetData:
    if os.path.exists('data/offset_data.json'):
        with open('data/offset_data.json', 'r') as offset_file:
            try:
                data = json.load(offset_file)
                return OffsetData(**data)

            except json.JSONDecodeError as e:
                print(f'Cannot decode offset JSON: {e}')

            except ValidationErr as e:
                print(f'Cannot validate offset data: {e}.')

    return None

def offset_images(images: List[Image.Image], x_offset: int, y_offset: int, ppi: int, angle_offset: float = 0.0) -> List[Image.Image]:
    result_images = []

    add_offset = False
    for image in images:
        if add_offset:
            # The back page is rotated 180° in the PDF (long-side flip).
            # In orientation-relative terms: +X = right, -X = left, +Y = up, -Y = down.
            # Negating x_offset compensates for the 180° x-axis flip.
            result = ImageChops.offset(image, math.floor(-x_offset * ppi / 300), math.floor(y_offset * ppi / 300))
            # Apply angle rotation if specified
            # Negative angle because PIL rotates counter-clockwise, but we want positive = clockwise
            if angle_offset != 0.0:
                result = result.rotate(-angle_offset, center=(image.width / 2, image.height / 2), fillcolor='white', resample=Image.Resampling.NEAREST)
            result_images.append(result)
        else:
            result_images.append(image)

        add_offset = not add_offset

    return result_images

def calculate_max_print_bleed(x_pos: List[int], y_pos: List[int], width: int, height: int, min_bleed: int = 0) -> tuple[int, int]:
    if len(x_pos) == 1 and len(y_pos) == 1:
        return (min_bleed, min_bleed)

    x_border_max = min_bleed
    if len(x_pos) >= 2:
        sx = sorted(x_pos)
        x_border_max = max(0, math.ceil((sx[1] - sx[0] - width) / 2))

    y_border_max = min_bleed
    if len(y_pos) >= 2:
        sy = sorted(y_pos)
        y_border_max = max(0, math.ceil((sy[1] - sy[0] - height) / 2))

    return (x_border_max, y_border_max)
