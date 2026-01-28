from enum import Enum
import itertools
import json
import math
import filetype
import os
import re
from glob import glob
from pathlib import Path
from typing import Dict, List
from xml.dom import ValidationErr

from natsort import natsorted
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
from pydantic import BaseModel

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

class CardSize(str, Enum):
    STANDARD = "standard"
    STANDARD_DOUBLE = "standard_double"
    JAPANESE = "japanese"
    POKER = "poker"
    POKER_HALF = "poker_half"
    BRIDGE = "bridge"
    BRIDGE_SQUARE = "bridge_square"
    TAROT = "tarot"
    DOMINO = "domino"
    DOMINO_SQUARE = "domino_square"

class PaperSize(str, Enum):
    LETTER = "letter"
    TABLOID = "tabloid"
    A4 = "a4"
    A3 = "a3"
    ARCHB = "archb"

class Registration(str, Enum):
    THREE = "3"
    FOUR = "4"

class CardLayoutSize(BaseModel):
    width: int
    height: int

class CardLayout(BaseModel):
    x_pos: List[int]
    y_pos: List[int]
    template: str

class PaperLayout(BaseModel):
    width: int
    height: int
    card_layouts: Dict[CardSize, CardLayout]

class Layouts(BaseModel):
    card_sizes: Dict[CardSize, CardLayoutSize]
    paper_layouts: Dict[PaperSize, PaperLayout]

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

def draw_card_with_bleed(card_image: Image.Image, base_image: Image.Image, x: int, y: int, print_bleed: tuple[int, int]):
    bleed_width, bleed_height = print_bleed

    width, height = card_image.size
    base_image.paste(card_image, (x, y))

    class Axis(int, Enum):
        X = 0
        Y = 1

    def extend_edge(crop_box: tuple[int, int, int, int], start: tuple[int, int], bleed: int, axis: Axis):
        for bleed_i in range(bleed):
            pos = (
                start[0] + (bleed_i if axis == Axis.X else 0),
                start[1] + (bleed_i if axis == Axis.Y else 0)
            )

            base_image.paste(card_image.crop(crop_box), pos)

    # Extend the edges of the cards to create print bleed
    # Top and bottom
    extend_edge((0, 0, width, 1), (x, y - bleed_height), bleed_height, Axis.Y)
    extend_edge((0, height - 1, width, height), (x, y + height), bleed_height, Axis.Y)

    # Left and right
    extend_edge((0, 0, 1, height), (x - bleed_width, y), bleed_width, Axis.X)
    extend_edge((width - 1, 0, width, height), (x + width, y), bleed_width, Axis.X)

    # Corners
    for bleed_width, crop_x, pos_x in [(bleed_width, 0, x - bleed_width), (bleed_width, width - 1, x + width)]:
        for bleed_height, crop_y, pos_y in [(bleed_height, 0, y - bleed_height), (bleed_height, height - 1, y + height)]:
            for x_bleed_i in range(bleed_width):
                for y_bleed_i in range(bleed_height):
                    base_image.paste(card_image.crop((crop_x, crop_y, crop_x + 1, crop_y + 1)), (pos_x + x_bleed_i, pos_y + y_bleed_i))

    return base_image

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
    ppi_ratio: float,
    extend_corners: int,
    flip: bool
):
    num_cards = num_rows * num_cols
    crop_percent_x, crop_percent_y = crop

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
        if flip:
            row = num_rows - row - 1

        base_x = math.floor(x_pos[col] * ppi_ratio)
        base_y = math.floor(y_pos[row] * ppi_ratio)

        # Default: use synthetic bleed, no position offset needed
        bleed_offset_x = 0
        bleed_offset_y = 0
        synthetic_bleed = (scaled_bleed_width, scaled_bleed_height)

        if card_image is single_back_image:
            card_image = card_image.resize((scaled_width, scaled_height))

        # Apply cropping and scaling if required
        elif crop_percent_x > 0 or crop_percent_y > 0:
            card_width, card_height = card_image.size

            # Calculate the original size minus the desired crop: "cropped size"
            cropped_width = math.floor(card_width * (1 - (crop_percent_x / 100)))
            cropped_height = math.floor(card_height * (1 - (crop_percent_y / 100)))

            # Calculate the ratio between the cropped size and the scaled size: "scale ratio"
            cropped_scaled_ratio_x = cropped_width / scaled_width
            cropped_scaled_ratio_y = cropped_height / scaled_height

            # Calculate the size of the card after adding bleed: "bleed size"
            scaled_width_with_bleed = scaled_width + 2 * scaled_bleed_width
            scaled_height_with_bleed = scaled_height + 2 * scaled_bleed_height

            # Calculate the size of the card after adding bleed, but before scaling: "unscaled bleed size"
            unscaled_width_with_bleed = math.floor(scaled_width_with_bleed * cropped_scaled_ratio_x)
            unscaled_height_with_bleed = math.floor(scaled_height_with_bleed * cropped_scaled_ratio_y)

            # Check if the unscaled bleed size is smaller than the original card size
            # If so, we can use real bleed from the card's edge pixels
            if unscaled_width_with_bleed < card_width and unscaled_height_with_bleed < card_height:
                crop_x = (card_width - unscaled_width_with_bleed) // 2
                crop_y = (card_height - unscaled_height_with_bleed) // 2
                card_image = card_image.crop((
                    crop_x,
                    crop_y,
                    card_width - crop_x,
                    card_height - crop_y,
                ))
                card_image = card_image.resize((scaled_width_with_bleed, scaled_height_with_bleed))

                # Offset position to account for bleed included in image
                bleed_offset_x = -scaled_bleed_width
                bleed_offset_y = -scaled_bleed_height
                synthetic_bleed = (0, 0)

            # Otherwise, crop the card to the cropped size, then resize it to the scaled size
            else:
                crop_x = card_width * (crop_percent_x / 100) // 2
                crop_y = card_height * (crop_percent_y / 100) // 2
                card_image = card_image.crop((
                    crop_x,
                    crop_y,
                    card_width - crop_x,
                    card_height - crop_y,
                ))
                card_image = card_image.resize((scaled_width, scaled_height))

        # If the card is not cropped, just resize it to the desired size
        else:
            card_image = card_image.resize((scaled_width, scaled_height))

        # Extend the corners if required
        card_image = card_image.crop((
            extend_corners_thickness,
            extend_corners_thickness,
            card_image.width - extend_corners_thickness,
            card_image.height - extend_corners_thickness
        ))

        if flip:
            card_image = card_image.rotate(180)

        # Calculate final position
        x = base_x + bleed_offset_x + extend_corners_thickness
        y = base_y + bleed_offset_y + extend_corners_thickness

        draw_card_with_bleed(card_image, base_image, x, y, (synthetic_bleed[0] + extend_corners_thickness, synthetic_bleed[1] + extend_corners_thickness))

def add_front_back_pages(front_page: Image.Image, back_page: Image.Image, pages: List[Image.Image], page_width: int, page_height: int, ppi_ratio: float, template: str, only_fronts: bool, name: str):
    # Add template version number to the back
    draw = ImageDraw.Draw(front_page)
    font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40 * ppi_ratio)

    # "Raw" specified location
    num_sheet = len(pages) + 1
    if not only_fronts:
        num_sheet = int(len(pages) / 2) + 1

    label = f'sheet: {num_sheet}, template: {template}'
    if name is not None:
        label = f'name: {name}, {label}'

    draw.text((math.floor((page_width / 2) * ppi_ratio), math.floor((page_height - 140) * ppi_ratio)), label, fill = (0, 0, 0), anchor="ma", font=font)

    # Add a back page for every front page template
    pages.append(front_page)
    if not only_fronts:
        pages.append(back_page)

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
    card_size: CardSize,
    paper_size: PaperSize,
    registration: Registration,
    only_fronts: bool,
    crop_string: str | None,
    extend_corners: int,
    ppi: int,
    quality: int,
    skip_indices: List[int],
    load_offset: bool,
    name: str
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

    with open(layouts_path, 'r') as layouts_file:
        try:
            layouts_data = json.load(layouts_file)
            layouts = Layouts(**layouts_data)

        except ValidationErr as e:
            raise Exception(f'Cannot parse layouts.json: {e}.')

        # paper_layout represents the size of a paper and all possible card layouts
        if paper_size not in layouts.paper_layouts:
            raise Exception(f'Unsupported paper size "{paper_size}".')
        paper_layout = layouts.paper_layouts[paper_size]

        # card_layout_size represents the size of a card
        if card_size not in layouts.card_sizes:
            raise Exception(f'Unsupported card size "{card_size}". Try card sizes: {paper_layout.card_layouts.keys()}.')
        card_layout_size = layouts.card_sizes[card_size]

        # card_layout represents the position of cards
        if card_size not in paper_layout.card_layouts:
            raise Exception(f'Unsupported card size "{card_size}" with paper size "{paper_size}". Try card sizes: {paper_layout.card_layouts.keys()}.')
        card_layout = paper_layout.card_layouts[card_size]

        # Determine the amount of x and y crop
        crop = parse_crop_string(crop_string, card_layout_size.width, card_layout_size.height)

        num_rows = len(card_layout.y_pos)
        num_cols = len(card_layout.x_pos)
        num_cards = num_rows * num_cols

        # Check skip indices
        # You can only skip valid indices (within the max card count per page)
        clean_skip_indices = [n for n in skip_indices if n < num_cards]
        ignore_skip_indices = [n for n in skip_indices if n >= num_cards]

        if len(ignore_skip_indices) > 0:
            print(f'Ignoring skip indices that are outside range 0-{num_cards - 1}: {ignore_skip_indices}')

        # If all possible cards are skipped, this may result in an infinite loop
        if len(clean_skip_indices) == num_cards:
            raise Exception(f'You cannot skip all cards per page')

        registration_filename =  f'{paper_size}_registration_{registration}.jpg'
        registration_path = os.path.join(asset_directory, registration_filename)

        # The baseline PPI is 300
        ppi_ratio = ppi / 300

        # Load an image with the registration marks
        with Image.open(registration_path) as reg_im:
            reg_im = reg_im.resize([math.floor(reg_im.width * ppi_ratio), math.floor(reg_im.height * ppi_ratio)])

            # Create the array that will store the filled templates
            pages: List[Image.Image] = []

            max_print_bleed = calculate_max_print_bleed(card_layout.x_pos, card_layout.y_pos, card_layout_size.width, card_layout_size.height)

            # Load and cache the single back image for reuse
            # Do this if we expect both front and back pages and if we have a back image
            # use_default_back_page indicates no back image was found
            single_back_image = None
            if not only_fronts and not use_default_back_page:
                try:
                    # We know the exact image path so we do not need resolve_image_with_any_extension()
                    single_back_image = Image.open(back_card_image_path)
                    single_back_image = ImageOps.exif_transpose(single_back_image)
                except FileNotFoundError:
                    print(f'Cannot get back image "{back_card_image_path}". Using default instead.')
                    single_back_image = None

            # Create card layout
            num_image = 1
            # First iterate on single-sided cards, then iterate on double-sided cards
            it = iter(natsorted(list(check_paths_subset(front_set, ds_set))) + natsorted(list(ds_set)))
            while True:
                file_group = list(itertools.islice(it, num_cards - len(clean_skip_indices)))
                if not file_group:
                    break

                # Fetch card art in batches
                # Batch size is based on cards per page
                front_card_images = []
                back_card_images = []
                file_group_iterator = iter(file_group)
                for i in range(num_cards):
                    if i in clean_skip_indices:
                        front_card_images.append(None)
                        back_card_images.append(None)
                        continue

                    try:
                        file = next(file_group_iterator)
                    except StopIteration:
                        break

                    print(f'Image {num_image}: {file}')
                    num_image += 1

                    front_card_image_path = os.path.join(front_dir_path, file)
                    # Allow differing extensions for double-sided images
                    # Iteration is a combination of front and double-sided image paths
                    front_card_image_path = resolve_image_with_any_extension(front_card_image_path)
                    front_card_image = Image.open(front_card_image_path)
                    front_card_image = ImageOps.exif_transpose(front_card_image)
                    front_card_images.append(front_card_image)

                    if only_fronts:
                        back_card_images.append(None)
                        continue

                    # Add double-sided back image
                    if file in ds_set:
                        ds_card_image_path = os.path.join(ds_dir_path, file)
                        # Allow differing extensions for double-sided images
                        # Iteration is a combination of front and double-sided image paths
                        ds_card_image_path = resolve_image_with_any_extension(ds_card_image_path)
                        ds_card_image = Image.open(ds_card_image_path)
                        ds_card_image = ImageOps.exif_transpose(ds_card_image)
                        back_card_images.append(ds_card_image)
                        continue

                    back_card_images.append(single_back_image)

                front_page = reg_im.copy()
                back_page = reg_im.copy()

                # Create front layout
                draw_card_layout(
                    front_card_images,
                    single_back_image,
                    front_page,
                    num_rows,
                    num_cols,
                    card_layout.x_pos,
                    card_layout.y_pos,
                    card_layout_size.width,
                    card_layout_size.height,
                    max_print_bleed,
                    crop,
                    ppi_ratio,
                    extend_corners,
                    flip=False
                )

                # Create back layout
                draw_card_layout(
                    back_card_images,
                    single_back_image,
                    back_page,
                    num_rows,
                    num_cols,
                    card_layout.x_pos,
                    card_layout.y_pos,
                    card_layout_size.width,
                    card_layout_size.height,
                    max_print_bleed,
                    crop,
                    ppi_ratio,
                    extend_corners,
                    flip=True # Flip the back sides
                )

                # Add the front and back layouts
                add_front_back_pages(
                    front_page,
                    back_page,
                    pages,
                    paper_layout.width,
                    paper_layout.height,
                    ppi_ratio,
                    card_layout.template,
                    only_fronts,
                    name
                )

            if len(pages) == 0:
                print('No pages were generated')
                return

            # Load saved offset if available
            if load_offset:
                saved_offset = load_saved_offset()

                if saved_offset is None:
                    print('Offset cannot be applied')
                else:
                    print(f'Loaded x offset: {saved_offset.x_offset}, y offset: {saved_offset.y_offset}, angle offset: {saved_offset.angle_offset}')
                    pages = offset_images(pages, saved_offset.x_offset, saved_offset.y_offset, ppi, saved_offset.angle_offset)

            # Save the pages array as a PDF
            if output_images:
                for index, page in enumerate(pages):
                    page.save(os.path.join(output_path, f'page{index + 1}.png'), resolution=math.floor(300 * ppi_ratio), speed=0, subsampling=0, quality=quality)

                print(f'Generated images: {output_path}')

            else:
                pages[0].save(output_path, format='PDF', save_all=True, append_images=pages[1:], resolution=math.floor(300 * ppi_ratio), speed=0, subsampling=0, quality=quality)
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
            result = ImageChops.offset(image, math.floor(x_offset * ppi / 300), math.floor(y_offset * ppi / 300))
            # Apply angle rotation if specified
            # Negative angle because PIL rotates counter-clockwise, but we want positive = clockwise
            if angle_offset != 0.0:
                result = result.rotate(-angle_offset, center=(image.width / 2, image.height / 2), fillcolor='white')
            result_images.append(result)
        else:
            result_images.append(image)

        add_offset = not add_offset

    return result_images

def calculate_max_print_bleed(x_pos: List[int], y_pos: List[int], width: int, height: int) -> tuple[int, int]:
    if len(x_pos) == 1 & len(y_pos) == 1:
        return (0, 0)

    x_border_max = 100000
    if len(x_pos) >= 2:
        x_pos.sort()

        x_pos_0 = x_pos[0]
        x_pos_1 = x_pos[1]

        x_border_max = math.ceil((x_pos_1 - x_pos_0 - width) / 2)

        if x_border_max < 0:
            x_border_max = 100000

    y_border_max = 100000
    if len(y_pos) >= 2:
        y_pos.sort()

        y_pos_0 = y_pos[0]
        y_pos_1 = y_pos[1]

        y_border_max = math.ceil((y_pos_1 - y_pos_0 - height) / 2)

        if y_border_max < 0:
            y_border_max = 100000

    return (x_border_max, y_border_max)