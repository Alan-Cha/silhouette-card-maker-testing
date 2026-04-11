import os

import click
from utilities import PaperSize, generate_md_pdf

# Use environment variables if available, otherwise fall back to local game directory
input_directory = os.environ.get('CARD_MAKER_DECKLIST_DIR', os.path.join('game', 'decklist'))
output_directory = os.environ.get('CARD_MAKER_OUTPUT_DIR', os.path.join('game', 'output'))

default_input_path = os.path.join(input_directory, 'entries.md')
default_output_path = os.path.join(output_directory, 'translatedTextBoxes.pdf')


@click.command()
@click.option('--input_path', default=default_input_path, show_default=True, help='The path to the markdown file containing entries separated by ---.')
@click.option('--output_path', default=default_output_path, show_default=True, help='The desired path to the output PDF.')
@click.option('--paper_size', default=PaperSize.LETTER.value, type=click.Choice([t.value for t in PaperSize], case_sensitive=False), show_default=True, help='The desired paper size.')
@click.option('--ppi', default=300, type=click.IntRange(min=1), show_default=True, help='Pixels per inch (PPI) when creating PDF.')
@click.option('--quality', default=75, type=click.IntRange(min=0, max=100), show_default=True, help='File compression. A higher value corresponds to better quality and larger file size.')
@click.version_option('1.0.0')
def cli(input_path, output_path, paper_size, ppi, quality):
    generate_md_pdf(
        input_path=input_path,
        output_path=output_path,
        paper_size=paper_size,
        ppi=ppi,
        quality=quality,
    )


if __name__ == '__main__':
    cli()
