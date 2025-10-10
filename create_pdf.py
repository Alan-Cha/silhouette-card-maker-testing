import os
import re

import click
from utilities import Registration, CardSize, PaperSize, generate_pdf

# Try to import upscale functionality (optional dependency)
try:
    from upscale import upscale_for_create_pdf
    UPSCALE_AVAILABLE = True
except ImportError:
    UPSCALE_AVAILABLE = False

front_directory = os.path.join('game', 'front')
back_directory = os.path.join('game', 'back')
double_sided_directory = os.path.join('game', 'double_sided')
output_directory = os.path.join('game', 'output')

default_output_path = os.path.join(output_directory, 'game.pdf')

@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card fronts.")
@click.option("--back_dir_path", default=back_directory, show_default=True, help="The path to the directory containing one or more card backs.")
@click.option("--double_sided_dir_path", default=double_sided_directory, show_default=True, help="The path to the directory containing card backs for double-sided cards.")
@click.option("--output_path", default=default_output_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--output_images", default=False, is_flag=True, help="Create images instead of a PDF.")
@click.option("--card_size", default=CardSize.STANDARD.value, type=click.Choice([t.value for t in CardSize], case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--paper_size", default=PaperSize.LETTER.value, type=click.Choice([t.value for t in PaperSize], case_sensitive=False), show_default=True, help="The desired paper size.")
@click.option("--registration", default=Registration.THREE.value, type=click.Choice([t.value for t in Registration], case_sensitive=False), show_default=True, help="The desired registration.")
@click.option("--only_fronts", default=False, is_flag=True, help="Only use the card fronts, exclude the card backs.")
@click.option("--crop", help="Crop the outer portion of front and double-sided images. Examples: 3mm, 0.125in, 6.5.")
@click.option("--extend_corners", default=0, type=click.IntRange(min=0), show_default=True, help="Reduce artifacts produced by rounded corners in card images.")
@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")
@click.option("--quality", default=75, type=click.IntRange(min=0, max=100), show_default=True, help="File compression. A higher value corresponds to better quality and larger file size.")
@click.option("--load_offset", default=False, is_flag=True, help="Apply saved offsets. See `offset_pdf.py` for more information.")
@click.option("--skip", type=click.IntRange(min=0), multiple=True, help="Skip a card based on its index. Useful for registration issues. Examples: 0, 4.")
@click.option("--name", help="Label each page of the PDF with a name.")
@click.option("--upscale", default=False, is_flag=True, help="Upscale images to 1200 DPI before creating PDF using Real-ESRGAN.")
@click.version_option("1.5.1")

def cli(
    front_dir_path,
    back_dir_path,
    double_sided_dir_path,
    output_path,
    output_images,
    card_size,
    paper_size,
    registration,
    only_fronts,
    crop,
    extend_corners,
    ppi,
    quality,
    skip,
    load_offset,
    name,
    upscale
):
    # Upscale images if requested
    if upscale:
        if not UPSCALE_AVAILABLE:
            print("Warning: Upscaling dependencies not installed. Skipping upscaling.")
            print("Install with: pip install torch torchvision basicsr facexlib gfpgan realesrgan opencv-python")
            print()
        else:
            upscale_for_create_pdf(
                front_dir_path,
                back_dir_path,
                double_sided_dir_path,
                card_size,
                target_dpi=1200
            )
    
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
        crop,
        extend_corners,
        ppi,
        quality,
        skip,
        load_offset,
        name
    )

if __name__ == '__main__':
    cli()