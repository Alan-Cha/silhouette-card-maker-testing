import os
import re

import click
from utilities import Registration, FitMode, generate_pdf, load_layout_config, get_all_card_size_names, get_all_paper_size_names, get_all_specialty_layout_names

front_directory = os.path.join('game', 'front')
back_directory = os.path.join('game', 'back')
double_sided_directory = os.path.join('game', 'double_sided')
output_directory = os.path.join('game', 'output')

default_output_path = os.path.join(output_directory, 'game.pdf')

layout_config = load_layout_config()
card_size_choices = get_all_card_size_names(layout_config)
paper_size_choices = get_all_paper_size_names(layout_config)
specialty_choices = get_all_specialty_layout_names(layout_config)

@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card fronts.")
@click.option("--back_dir_path", default=back_directory, show_default=True, help="The path to the directory containing one or more card backs.")
@click.option("--double_sided_dir_path", default=double_sided_directory, show_default=True, help="The path to the directory containing card backs for double-sided cards.")
@click.option("--output_path", default=default_output_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--output_images", default=False, is_flag=True, help="Create images instead of a PDF.")

@click.option("--card_size", default="standard", type=click.Choice(card_size_choices, case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--paper_size", default="letter", type=click.Choice(paper_size_choices, case_sensitive=False), show_default=True, help="The desired paper size.")
@click.option("--registration", default=Registration.THREE.value, type=click.Choice([t.value for t in Registration], case_sensitive=False), show_default=True, help="The desired registration.")
@click.option("--specialty", default=None, type=click.Choice(specialty_choices, case_sensitive=False), help="Use a specialty layout. Overrides card_size, paper_size, and registration settings.")

@click.option("--only_fronts", default=False, is_flag=True, help="Only use the card fronts, exclude the card backs.")
@click.option("--fit", default=FitMode.STRETCH.value, type=click.Choice([t.value for t in FitMode], case_sensitive=False), show_default=True, help="How to fit front and double-sided images to card size. 'stretch' allows distortion, 'crop' preserves aspect ratio by center-cropping.")
@click.option("--fit_backs", type=click.Choice([t.value for t in FitMode], case_sensitive=False), help="How to fit back images to card size. If not specified, uses the value from --fit.")

@click.option("--crop", help="Crop the outer portion of front and double-sided images (removes edges). Examples: 3mm, 0.125in, 6.5.")
@click.option("--crop_backs", help="Crop the outer portion of back images (removes edges). Examples: 3mm, 0.125in, 6.5.")
@click.option("--extend_edges", help="Crop card edges and extend them uniformly to generate bleed for front and double-sided images. Like --crop but generates bleed from cropped edges. Examples: 3mm, 0.125in.")
@click.option("--extend_edges_backs", help="Crop card edges and extend them uniformly to generate bleed for back images only. Like --crop but generates bleed from cropped edges. Examples: 3mm, 0.125in.")
@click.option("--extend_corners", help="Fill rounded corner regions to reduce corner artifacts for front and double-sided images. Fills cut zones beyond corner radius arc. Examples: 3mm, 0.125in.")
@click.option("--extend_corners_backs", help="Fill rounded corner regions to reduce corner artifacts for back images only. Fills cut zones beyond corner radius arc. Examples: 3mm, 0.125in.")
@click.option("--extend_bleed", help="Extend the outer bleed of outer cards on front pages (odd-numbered pages). Only affects edges facing outward from the layout. Examples: 3mm, 0.125in.")
@click.option("--extend_bleed_backs", help="Extend the outer bleed of outer cards on back pages (even-numbered pages). Only affects edges facing outward from the layout. Examples: 3mm, 0.125in.")

@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")
@click.option("--quality", default=100, type=click.IntRange(min=0, max=100), show_default=True, help="File compression. A higher value corresponds to better quality and larger file size.")
@click.option("--load_offset", default=False, is_flag=True, help="Apply saved offsets. See `offset_pdf.py` for more information.")
@click.option("--skip", type=click.IntRange(min=0), multiple=True, help="Skip a card based on its index. Useful for registration issues. Examples: 0, 4.")

@click.option("--label", help="Apply a custom label to each page.")
@click.option("--show_outline", default=False, is_flag=True, help="Overlay a white outline of the cutting path on each page.")
@click.option("--borderless", default=False, is_flag=True, help="Use tighter margins to fit more cards per page.")

@click.version_option("2.2.0")

def cli(
    front_dir_path,
    back_dir_path,
    double_sided_dir_path,
    output_path,
    output_images,
    card_size,
    paper_size,
    registration,
    specialty,
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
    borderless
):
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
    )

if __name__ == '__main__':
    cli()
