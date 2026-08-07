# ==============================================================================
# pdf.py
#     PDF generation
# ==============================================================================
import itertools
import math
import os

from natsort import natsorted

from src import page_manager

from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

from src import measurements
from src.draw import draw_card_layouts, draw_outlines
from src.enums import FitMode, Orientation, OrientationMode, Registration, Variant
from src.images import (
    MINIMUM_BLEED,
    calculate_max_print_bleed,
    load_card_image,
    parse_crop_string,
    parse_dimension_string,
)
from src.layouts import (
    PaperSizeDef,
    RegistrationSettings,
    load_layout_config,
    CardSizeDef,
    resolve_card_size_alias,
    resolve_paper_size_alias,
)
from src.offset import load_saved_offset
from src.paths import (
    Paths,
    check_paths_subset,
    ensure_output_directory_exists,
    get_back_card_image_path,
    get_directory,
    get_image_file_paths,
    resolve_image_with_any_extension,
)


def create_template_name(
    paper_size: str, card_size: str, variant: Variant, version: int
) -> str:
    var_string = f"{variant.value}-" if variant != Variant.DEFAULT else ""
    return f"{paper_size}-{card_size}-{var_string}v{version}"


def add_front_back_pages(
    front_page: Image.Image,
    back_page: Image.Image,
    pages: list[Image.Image],
    page_width: int,
    page_height: int,
    ppi_ratio: float,
    template: str,
    only_fronts: bool,
    label: str | None,
    orientation: Orientation,
    label_margin_px: int,
) -> None:
    font = ImageFont.truetype(Paths.assets / "arial.ttf", 40 * ppi_ratio)
    num_sheet = len(pages) + 1
    if not only_fronts:
        num_sheet = int(len(pages) / 2) + 1

    label_text = f"sheet: {num_sheet}, template: {template}"
    if label is not None:
        label_text = f"label: {label}, {label_text}"

    # Label goes on short side of paper opposite top-left black square
    if orientation == Orientation.LANDSCAPE:
        front_page = front_page.rotate(-90, expand=True)
        draw = ImageDraw.Draw(front_page)
        label_x = math.floor((page_height / 2) * ppi_ratio)
        label_y = math.floor(page_width * ppi_ratio) - label_margin_px
        draw.text(
            (label_x, label_y), label_text, fill=(0, 0, 0), anchor="mm", font=font
        )
        front_page = front_page.rotate(90, expand=True)
    else:
        draw = ImageDraw.Draw(front_page)
        label_x = math.floor((page_width / 2) * ppi_ratio)
        label_y = math.floor(page_height * ppi_ratio) - label_margin_px
        draw.text(
            (label_x, label_y), label_text, fill=(0, 0, 0), anchor="mm", font=font
        )

    if orientation == Orientation.PORTRAIT:
        front_page = front_page.rotate(90, expand=True)
        back_page = back_page.rotate(90, expand=True)

    pages.append(front_page)
    if not only_fronts:
        pages.append(back_page)


def find_best_orientation(
    orientation_mode: OrientationMode,
    card_width: str,
    card_height: str,
    paper_width: str,
    paper_height: str,
    inset: str,
    length: str,
    ppi: int,
    preferred: Orientation = Orientation.LANDSCAPE,
) -> tuple[Orientation, page_manager.CardLayout]:
    kwargs = dict(
        card_width=card_width,
        card_height=card_height,
        paper_width=paper_width,
        paper_height=paper_height,
        inset=inset,
        length=length,
        ppi=ppi,
    )

    if orientation_mode != OrientationMode.OPTIMIZE:
        orientation = Orientation(orientation_mode.value)
        return orientation, page_manager.generate_layout(
            orientation=orientation, **kwargs
        )

    # try both orientations and pick the one that fits more cards
    best_count = 0
    best_orientation = preferred
    best_computed = None

    for orient in Orientation:
        try:
            computed = page_manager.generate_layout(orientation=orient, **kwargs)
        except ValueError:
            continue

        count = len(computed.x_pos) * len(computed.y_pos)
        if count > best_count or (count == best_count and orient == preferred):
            best_count = count
            best_orientation = orient
            best_computed = computed

    if best_computed is None:
        raise ValueError("No valid layout in either card orientation.")

    return best_orientation, best_computed


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
    fit_backs: FitMode | None,
    crop_string: str | None,
    crop_backs_string: str | None,
    extend_edges: str | None,
    extend_edges_backs: str | None,
    extend_corners: str | None,
    extend_corners_backs: str | None,
    extend_bleed: str | None,
    extend_bleed_backs: str | None,
    ppi: int,
    quality: int,
    skip_indices: list[int],
    load_offset: bool,
    label: str,
    show_outline: bool = False,
    specialty: str | None = None,
    borderless: bool = False,
    registration_orientation_override: str | None = None,
) -> None:

    # ==============================
    # File ops
    # ==============================
    f_path = Path(front_dir_path)
    if not f_path.is_dir():
        raise FileNotFoundError(f"Invalid front image directory: {f_path}")
    b_path = Path(back_dir_path)
    if not b_path.is_dir():
        raise FileNotFoundError(f"Invalid back image directory: {b_path}")
    ds_path = Path(ds_dir_path)
    if not ds_path.is_dir():
        raise FileNotFoundError(f"Invalid double-sided image directory: {ds_path}")

    o_path = Path(output_path)
    if output_images:
        o_path = get_directory(o_path)
    else:
        if not o_path.name.lower().endswith(".pdf"):
            raise FileNotFoundError(f"Invalid PDF output path: {o_path}")
        ensure_output_directory_exists(o_path)
    output_path = str(o_path)

    back_card_image_path = None
    use_default_back_page = True
    if not only_fronts:
        back_card_image_path = get_back_card_image_path(back_dir_path)
        use_default_back_page = back_card_image_path is None
        if use_default_back_page:
            print(f"No back image provided in back image directory: {back_dir_path}")

    front_image_filenames = get_image_file_paths(front_dir_path)
    ds_image_filenames = get_image_file_paths(ds_dir_path)

    front_set = set(front_image_filenames)
    ds_set = set(ds_image_filenames)
    diff = check_paths_subset(ds_set, front_set)
    if len(diff) > 0:
        raise Exception(
            f'Double-sided backs "{ds_set - front_set}" do not have matching fronts. Add the missing fronts to front image directory: {front_dir_path}'
        )

    if only_fronts:
        if len(ds_set) > 0:
            raise Exception(
                f'Cannot use "--only_fronts" with double-sided cards. Remove cards from double_side image directory: {ds_dir_path}'
            )

    # ==============================
    # Layout
    # ==============================
    layout_config = load_layout_config()
    default_reg = layout_config.defaults.registration.default
    registration_orientation_override = (
        Orientation(registration_orientation_override)
        if registration_orientation_override is not None
        else None
    )

    if borderless and specialty:
        raise Exception(
            "Cannot use --borderless with --specialty. Specialty layouts define their own geometry."
        )

    if specialty:
        if (
            not layout_config.specialty_layouts
            or specialty not in layout_config.specialty_layouts
        ):
            raise Exception(f'Specialty layout "{specialty}" not found.')
        spec = layout_config.specialty_layouts[specialty]

        if spec.card_size.name:
            if spec.card_size.name not in layout_config.card_sizes:
                raise Exception(f"Card size not found: {spec.card_size.name}")
            base = layout_config.card_sizes[spec.card_size.name]
            card_size_def = CardSizeDef(
                width=base.width,
                height=base.height,
                radius=spec.card_size.radius or base.radius,
            )
        else:
            card_size_def = CardSizeDef(
                width=spec.card_size.width or "",
                height=spec.card_size.height or "",
                radius=spec.card_size.radius,
            )

        if spec.paper_size.name:
            if spec.paper_size.name not in layout_config.paper_sizes:
                raise Exception(f"Paper size not found: {spec.paper_size.name}")
            paper_size_def = layout_config.paper_sizes[spec.paper_size.name]
        else:
            paper_size_def = PaperSizeDef(
                width=spec.paper_size.width or "",
                height=spec.paper_size.height or "",
            )

        orientation = spec.orientation
        registration_orientation = spec.registration_orientation or orientation

        if registration_orientation_override is not None:
            registration_orientation = registration_orientation_override
        template = f"{specialty}-v{spec.version}"

        lr = spec.registration or RegistrationSettings()
        effective_inset = lr.inset or default_reg.inset

    else:
        card_size = resolve_card_size_alias(layout_config, card_size)
        paper_size = resolve_paper_size_alias(layout_config, paper_size)

        if card_size not in layout_config.card_sizes:
            raise Exception(
                f'Unsupported card size "{card_size}". Try card sizes: {list(layout_config.card_sizes.keys())}'
            )
        card_size_def = layout_config.card_sizes[card_size]

        if paper_size not in layout_config.paper_sizes:
            raise Exception(
                f'Unsupported paper size "{paper_size}". Try paper sizes: {list(layout_config.paper_sizes.keys())}'
            )
        paper_size_def = layout_config.paper_sizes[paper_size]

        variant = Variant.BORDERLESS if borderless else Variant.DEFAULT

        if (
            paper_size not in layout_config.layouts
            or card_size not in layout_config.layouts[paper_size]
        ):
            raise Exception(
                f'No layout defined for paper "{paper_size}" with card "{card_size}". Add it to layouts.json.'
            )

        card_layouts = layout_config.layouts[paper_size][card_size]
        if variant.value not in card_layouts:
            raise Exception(
                f'No {variant.value} layout defined for paper "{paper_size}" with card "{card_size}". Add it to layouts.json.'
            )

        layout_def = card_layouts[variant.value]
        orientation = layout_def.orientation
        registration_orientation = layout_def.registration_orientation or orientation
        if registration_orientation_override is not None:
            registration_orientation = registration_orientation_override
        version = layout_def.version

        layout_reg = layout_def.registration
        lr = layout_reg or RegistrationSettings()

        if borderless:
            effective_inset = (
                lr.inset or layout_config.defaults.registration.borderless.inset
            )
        else:
            effective_inset = (
                lr.inset or layout_config.defaults.registration.default.inset
            )

        template = create_template_name(paper_size, card_size, variant, version)

    # ==============================
    # Image modification
    # ==============================
    effective_thickness = lr.thickness or default_reg.thickness
    effective_length = lr.length or default_reg.length

    total_exclusion_mm = (
        measurements.size_to_mm(default_reg.length) + page_manager.REG_PADDING_MM
    )
    computed = page_manager.generate_layout(
        orientation=orientation,
        card_width=card_size_def.width,
        card_height=card_size_def.height,
        paper_width=paper_size_def.width,
        paper_height=paper_size_def.height,
        inset=effective_inset or "",
        length=f"{total_exclusion_mm}mm",
        ppi=layout_config.ppi,
    )

    card_width_px = computed.card_width_px
    card_height_px = computed.card_height_px
    page_width_px = computed.paper_width_px
    page_height_px = computed.paper_height_px
    x_pos = computed.x_pos
    y_pos = computed.y_pos

    crop = parse_crop_string(crop_string, card_width_px, card_height_px)
    crop_backs = parse_crop_string(crop_backs_string, card_width_px, card_height_px)

    extend_edges_px = parse_dimension_string(extend_edges, layout_config.ppi)
    extend_edges_backs_px = parse_dimension_string(
        extend_edges_backs, layout_config.ppi
    )

    extend_corners_px = parse_dimension_string(extend_corners, layout_config.ppi)
    extend_corners_backs_px = parse_dimension_string(
        extend_corners_backs, layout_config.ppi
    )

    extend_bleed_px = parse_dimension_string(extend_bleed, layout_config.ppi)
    extend_bleed_backs_px = parse_dimension_string(
        extend_bleed_backs, layout_config.ppi
    )

    fit_backs_mode = FitMode(fit_backs) if fit_backs is not None else fit

    effective_card_radius = card_size_def.radius or layout_config.defaults.card_radius
    radius_px = measurements.size_to_pixel(effective_card_radius, layout_config.ppi)

    # ==============================
    # PDF
    # ==============================
    num_rows = len(y_pos)
    num_cols = len(x_pos)
    num_cards = num_rows * num_cols

    if num_cards == 0:
        raise Exception(
            f'Card size "{card_size}" does not fit on paper size "{paper_size}".'
        )

    clean_skip_indices = [n for n in skip_indices if n < num_cards]
    ignore_skip_indices = [n for n in skip_indices if n >= num_cards]

    if len(ignore_skip_indices) > 0:
        print(
            f"Ignoring skip indices that are outside range 0-{num_cards - 1}: {ignore_skip_indices}"
        )

    if len(clean_skip_indices) == num_cards:
        raise Exception("You cannot skip all cards per page!")

    ppi_ratio = ppi / 300
    inset_px = measurements.size_to_pixel(effective_inset, layout_config.ppi)
    thickness_px = measurements.size_to_pixel(effective_thickness, layout_config.ppi)
    if borderless:
        label_margin_px = math.floor(inset_px * ppi_ratio)
    else:
        label_margin_px = math.floor((inset_px - thickness_px * 2) * ppi_ratio)

    reg_is_portrait = registration_orientation == Orientation.PORTRAIT
    reg_width = paper_size_def.height if reg_is_portrait else paper_size_def.width
    reg_height = paper_size_def.width if reg_is_portrait else paper_size_def.height

    # ==============================
    # Page Manager
    # ==============================
    with page_manager.generate_reg_mark(
        reg_width,
        reg_height,
        effective_inset or "",
        effective_thickness or "",
        effective_length or "",
        layout_config.ppi,
        registration,
    ) as reg_im:
        reg_im = reg_im.resize(
            [
                math.floor(reg_im.width * ppi_ratio),
                math.floor(reg_im.height * ppi_ratio),
            ]
        )

        if registration_orientation != orientation:
            reg_im = reg_im.rotate(90 if reg_is_portrait else -90, expand=True)

        pages: list[Image.Image] = []

        max_print_bleed = calculate_max_print_bleed(
            x_pos, y_pos, card_width_px, card_height_px, MINIMUM_BLEED
        )

        # Cache back
        single_back_image = None
        if not only_fronts and not use_default_back_page:
            if back_card_image_path is not None:
                single_back_image = load_card_image(back_card_image_path, "back")

        # Create card layout
        num_image = 1
        it = iter(
            natsorted(list(check_paths_subset(front_set, ds_set)))
            + natsorted(list(ds_set))
        )
        while True:
            file_group = list(itertools.islice(it, num_cards - len(clean_skip_indices)))
            if not file_group:
                break

            # Get cards in batches
            front_card_images: list[Image.Image | None] = []
            back_card_images: list[Image.Image | None] = []
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

                print(f"Image {num_image}: {file}")
                num_image += 1

                front_card_image_path = os.path.join(front_dir_path, file)
                front_card_image_path = resolve_image_with_any_extension(
                    front_card_image_path
                )

                front_card_image = load_card_image(front_card_image_path, "front")
                front_card_images.append(front_card_image)

                if only_fronts:
                    back_card_images.append(None)
                    continue

                if file in ds_set:
                    ds_card_image_path = os.path.join(ds_dir_path, file)

                    # Backside image might have different extension
                    ds_card_image_path = resolve_image_with_any_extension(
                        ds_card_image_path
                    )
                    ds_card_image = load_card_image(ds_card_image_path, "double-sided")
                    back_card_images.append(ds_card_image)
                    continue

                back_card_images.append(single_back_image)

            front_page = reg_im.copy()
            back_page = reg_im.copy()

            draw_card_layouts(
                front_card_images,
                back_card_images,
                single_back_image,
                front_page,
                back_page,
                num_rows,
                num_cols,
                x_pos,
                y_pos,
                card_width_px,
                card_height_px,
                max_print_bleed,
                crop,
                crop_backs,
                ppi_ratio,
                extend_edges_px,
                extend_edges_backs_px,
                extend_corners_px,
                extend_corners_backs_px,
                extend_bleed_px,
                extend_bleed_backs_px,
                fit=fit,
                fit_backs=fit_backs_mode,
                orientation=orientation,
            )

            if show_outline:
                draw_outlines(
                    [front_page, back_page],
                    x_pos,
                    y_pos,
                    card_width_px,
                    card_height_px,
                    radius_px,
                    ppi_ratio,
                )

            add_front_back_pages(
                front_page,
                back_page,
                pages,
                page_width_px,
                page_height_px,
                ppi_ratio,
                template,
                only_fronts,
                label,
                orientation,
                label_margin_px,
            )

        if len(pages) == 0:
            print("No pages were generated.")
            return

        if load_offset:
            saved_offset = load_saved_offset()

            if saved_offset is None:
                print("Offset cannot be applied")
            else:
                print(
                    "Loaded offsets:"
                    + f"x={saved_offset.x_offset},"
                    + f"y={saved_offset.y_offset},"
                    + f"angle={saved_offset.angle_offset}"
                )

        if output_images:
            for index, page in enumerate(pages):
                page.save(
                    os.path.join(output_path, f"page{index + 1}.png"),
                    resolution=math.floor(300 * ppi_ratio),
                    speed=0,
                    subsampling=0,
                    quality=quality,
                )
            print(f"Generated images: {output_path}")
        else:
            pages[0].save(
                output_path,
                format="PDF",
                save_all=True,
                append_images=pages[1:],
                resolution=math.floor(300 * ppi_ratio),
                speed=0,
                subsampling=0,
                quality=quality,
            )
            print(f"Generated PDF: {output_path}")
