import os
import click

from pdf_generation.offset_pdf import offset_pdf

output_directory = os.path.join('game', 'output')
default_output_pdf_path = os.path.join(output_directory, 'game.pdf')

@click.command(name="offset_pdf")
@click.option("--pdf_path", default=default_output_pdf_path, help="The path of the input PDF.")
@click.option("--output_pdf_path", help="The desired path of the offset PDF.")
@click.option("-x", "--x_offset", type=int, help="The desired offset in the x-axis.")
@click.option("-y", "--y_offset", type=int, help="The desired offset in the y-axis.")
@click.option("-s", "--save", default=False, is_flag=True, help="Save the x and y offset values.")
@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")

def offset_pdf_cli(pdf_path, output_pdf_path, x_offset, y_offset, save, ppi):
    """Add an offset to your PDF"""
    offset_pdf(pdf_path, output_pdf_path, x_offset, y_offset, save, ppi)