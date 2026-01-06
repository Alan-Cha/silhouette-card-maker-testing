import click

from utilities.clean_up import delete_files

@click.group(name="utility")
def utility_cli() -> None:
    """Utilities to ease use of Silhouette Card Maker"""
    pass

@utility_cli.command(name="cleanup")
@click.version_option("1.6.0")

def cleanup_cli():
    """Clear files retrieved by plugins"""
    delete_files()