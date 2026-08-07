import click

from pathlib import Path

from src.enums import Orientation, Registration, FitMode
from src.paths import Paths
from src.pdf import generate_pdf
from src.layouts import (
    load_layout_config,
    get_all_card_size_names,
    get_all_paper_size_names,
    get_all_specialty_layout_names,
)

#============================
# Initialize Defaults
#============================
front_directory = Paths.fronts
back_directory = Paths.backs
double_sided_directory = Paths.doubles
output_directory = Paths.output
default_output_path = output_directory / "game.pdf"

layout_config = load_layout_config()
card_size_choices = get_all_card_size_names(layout_config)
paper_size_choices = get_all_paper_size_names(layout_config)
specialty_choices = get_all_specialty_layout_names(layout_config)

# ============================
# CLI Args
# ============================
@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card fronts.")
@click.option("--back_dir_path", default=back_directory, show_default=True, help="The path to the directory containing one or more card backs.")
@click.option("--double_sided_dir_path", default=double_sided_directory, show_default=True, help="The path to the directory containing card backs for double-sided cards.")
@click.option("--output_path", default=default_output_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--output_images", default=False, is_flag=True, help="Create images instead of a PDF.")
@click.option("--card_size", default="standard", type=click.Choice(card_size_choices, case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--paper_size", default="letter", type=click.Choice(paper_size_choices, case_sensitive=False), show_default=True, help="The desired paper size.")
@click.option("--registration", default=Registration.THREE.value, type=click.Choice([t.value for t in Registration], case_sensitive=False), show_default=True, help="The desired registration pattern.")
@click.option("--registration_orientation", default=None, type=click.Choice([t.value for t in Orientation], case_sensitive=False), help="Override the registration mark orientation without changing the card layout.")
@click.option("--specialty", default=None, type=click.Choice(specialty_choices, case_sensitive=False), help="Use a specialty layout. Overrides card_size, paper_size, and registration settings.")
@click.option("--only_fronts", default=False, is_flag=True, help="Only generate front pages.")
@click.option("--fit", default=FitMode.STRETCH.value, type=click.Choice([t.value for t in FitMode], case_sensitive=False), show_default=True, help="How to fit front and double-sided images to card size. 'stretch' allows distortion, 'crop' preserves aspect ratio by center-cropping.")
@click.option("--fit_backs", type=click.Choice([t.value for t in FitMode], case_sensitive=False), help="How to fit back images to card size. 'stretch' allows distortion, 'crop' preserves aspect ratio by center-cropping.")
@click.option("--crop", help="Crop card edges of front and double-sided images (removes edges). Examples: 3mm, 0.125in, 6.5.")
@click.option("--crop_backs", help="Crop card edges of back images (removes edges). Examples: 3mm, 0.125in, 6.5.")
@click.option("--extend_edges", help="Crop card edges and extend them for front and double-sided images. Examples: 3mm, 0.125in.")
@click.option("--extend_edges_backs", help="Crop card edges and extend them for back images only. Examples: 3mm, 0.125in.")
@click.option("--extend_corners", help="Extend rounded corner regions to reduce corner artifacts for front and double-sided images. Examples: 3mm, 0.125in.")
@click.option("--extend_corners_backs", help="Extend rounded corner regions to reduce corner artifacts for back images only. Examples: 3mm, 0.125in.")
@click.option("--extend_bleed", help="Extend the outer bleed of outer cards on front pages (odd-numbered pages). Examples: 3mm, 0.125in.")
@click.option("--extend_bleed_backs", help="Extend the outer bleed of outer cards on back pages (even-numbered pages). Examples: 3mm, 0.125in.")
@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")
@click.option("--quality", default=100, type=click.IntRange(min=0, max=100), show_default=True, help="File compression quality.")
@click.option("--load_offset", default=False, is_flag=True, help="Apply saved offsets. See `offset_pdf.py` for more information.")
@click.option("--skip", type=click.IntRange(min=0), multiple=True, help="Skip a card based on its index. Useful for registration issues. Examples: 0, 4.")
@click.option("--label", help="Apply a custom label to each page.")
@click.option("--show_outline", default=False, is_flag=True, help="Show a white outline for cutting paths.")
@click.option("--borderless", default=False, is_flag=True, help="Use tighter inset to fit more cards per page.")
@click.version_option("2.2.0")
# ============================

def cli(
    front_dir_path: str | Path,
    back_dir_path: str | Path,
    double_sided_dir_path: str | Path,
    output_path: str | Path,
    output_images: bool,
    card_size: str,
    paper_size: str,
    registration: Registration,
    registration_orientation: str | None,
    specialty: str | None,
    only_fronts: bool,
    fit: FitMode,
    fit_backs: FitMode,
    crop: str | None,
    crop_backs: str | None,
    extend_edges: str | None,
    extend_edges_backs: str | None,
    extend_corners: str | None,
    extend_corners_backs: str | None,
    extend_bleed: str | None,
    extend_bleed_backs: str | None,
    ppi: int,
    quality: int,
    skip: list[int] | None,
    load_offset: bool,
    label: str | None,
    show_outline: bool,
    borderless: bool,
):
    front_dir_path = str(front_dir_path)
    back_dir_path = str(back_dir_path)
    double_sided_dir_path = str(double_sided_dir_path)
    output_path = str(output_path)

    skip = skip or []
    label = label or ""

    generate_pdf(
        front_dir_path,
        back_dir_path,
        double_sided_dir_path,
        output_path,
        output_images,
        card_size,
        paper_size,
        registration,
        only_fronts,
        fit,
        fit_backs,
        crop,
        crop_backs,
        extend_edges,
        extend_edges_backs,
        extend_corners,
        extend_corners_backs,
        extend_bleed,
        extend_bleed_backs,
        ppi,
        quality,
        skip,
        load_offset,
        label,
        show_outline,
        specialty=specialty,
        borderless=borderless,
        registration_orientation_override=registration_orientation,
    )


if __name__ == "__main__":
    cli()
