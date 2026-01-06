import click

from commands.fetch import fetch_cli
from commands.create_pdf import create_pdf_cli
from commands.offset_pdf import offset_pdf_cli
from commands.utility import utility_cli

@click.group()
def cli() -> None:
    """Silhouette Card Maker - A suite of tools for making custom cards and proxies with Silhouette cutting machines."""
    pass

# Attach external commands/groups
cli.add_command(create_pdf_cli)
cli.add_command(offset_pdf_cli)
cli.add_command(fetch_cli)
cli.add_command(utility_cli)

if __name__ == "__main__":
    cli()
