"""
Card PDF Generator with Image Enhancement

This script lays out card images into printable PDFs with registration marks for
use with Silhouette cutting machines. Includes optional AI-powered upscaling and
image enhancement features for professional-quality output.

Features:
    - Automatic card layout with registration marks
    - Support for single and double-sided cards
    - AI-powered upscaling to 1200 DPI (optional)
    - Saturation, contrast, and brightness adjustments for vibrant colors
    - Blank page exclusion to reduce PDF size (optional)
    - Multiple card and paper size support
    - Offset calibration for precise alignment

Usage:
    Basic usage:
        python create_pdf.py
    
    With upscaling and enhancements:
        python create_pdf.py --upscale --saturation 1.1 --contrast 1.1 --brightness 1.1
    
    Custom sizes:
        python create_pdf.py --card_size poker --paper_size a4

For detailed documentation, see README.md

Author: Silhouette Card Maker Contributors
Version: 1.5.1
"""

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
@click.option("--upscale", default=False, is_flag=True, help="Upscale images before creating PDF using Real-ESRGAN.")
@click.option("--upscale_target_dpi", default=1200, type=click.IntRange(min=300), show_default=True, help="Target DPI when upscaling (used with --upscale).")
@click.option("--saturation", default=1.0, type=click.FloatRange(min=0.0, max=2.0), show_default=True, help="Saturation multiplier (1.0=no change, >1.0=boost, <1.0=reduce).")
@click.option("--contrast", default=1.0, type=click.FloatRange(min=0.0, max=2.0), show_default=True, help="Contrast multiplier (1.0=no change, >1.0=boost, <1.0=reduce).")
@click.option("--brightness", default=1.0, type=click.FloatRange(min=0.0, max=2.0), show_default=True, help="Brightness multiplier (1.0=no change, >1.0=brighter, <1.0=darker).")
@click.option("--skip_blank_pages", default=False, is_flag=True, help="Skip pages that contain no card images to reduce PDF size.")
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
    upscale,
    upscale_target_dpi,
    saturation,
    contrast,
    brightness,
    skip_blank_pages
):
    """
    Generate a PDF with card images laid out for cutting with Silhouette machines.
    
    This command-line interface provides comprehensive control over PDF generation,
    including optional AI upscaling and image enhancements for professional results.
    
    The tool will:
    1. Optionally upscale images to target DPI using Real-ESRGAN (if --upscale is set)
    2. Apply saturation, contrast, and brightness adjustments (if specified)
    3. Layout cards with registration marks for precise cutting
    4. Optionally skip blank pages to reduce PDF size (if --skip_blank_pages is set)
    5. Generate a print-ready PDF (or individual images if --output_images is set)
    
    Examples:
        Basic usage:
            python create_pdf.py
        
        With AI upscaling and color enhancement:
            python create_pdf.py --upscale --saturation 1.1 --contrast 1.1 --brightness 1.1
        
        Optimized PDF with blank page skipping:
            python create_pdf.py --skip_blank_pages
        
        Custom card/paper sizes with offset:
            python create_pdf.py --card_size poker --paper_size a4 --load_offset
    """
    
    # Step 1: Upscale images if requested (before PDF generation)
    if upscale:
        if not UPSCALE_AVAILABLE:
            print("\n" + "=" * 60)
            print("⚠️  WARNING: Upscaling dependencies not installed")
            print("=" * 60)
            print("\nThe --upscale flag requires additional dependencies.")
            print("Skipping upscaling and proceeding with PDF generation...")
            print("\nTo enable upscaling, install dependencies:")
            print("  pip install -r requirements.txt")
            print("\n" + "=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print("🎨 Upscaling images to " + str(upscale_target_dpi) + " DPI...")
            print("=" * 60 + "\n")
            
            upscale_for_create_pdf(
                front_dir_path,
                back_dir_path,
                double_sided_dir_path,
                card_size,
                target_dpi=upscale_target_dpi
            )
            
            print("=" * 60)
            print("✓ Upscaling complete!")
            print("=" * 60 + "\n")
    
    # Step 2: Generate PDF with layout, registration marks, and optional enhancements
    # The saturation, contrast, and brightness parameters are applied during image processing
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
        name,
        saturation,       # Color saturation multiplier (1.0 = no change)
        contrast,         # Contrast multiplier (1.0 = no change)
        brightness,       # Brightness multiplier (1.0 = no change)
        skip_blank_pages  # Skip pages with no card content
    )

if __name__ == '__main__':
    cli()