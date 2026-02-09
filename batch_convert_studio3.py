#!/usr/bin/env python3
"""
Batch convert DXF files to .studio3 using Silhouette Studio GUI automation.

Iterates over all DXF files in cutting_templates/dxf/ and converts each
to a .studio3 file in cutting_templates/ using SilhouetteAutomation from
dxf_to_studio3.py.

Opens Silhouette Studio once, converts all files, then closes it.
Always uses registration marks with thickness=100.

Usage:
    python batch_convert_studio3.py
    python batch_convert_studio3.py --dxf_dir cutting_templates/dxf --output_dir cutting_templates
"""

import re
from pathlib import Path

import click

from enums import Orientation
from utilities import LayoutConfig, load_layout_config
from dxf_to_studio3 import (
    SilhouetteAutomation,
    RegistrationSettings,
    DEFAULT_STUDIO_PATH,
    ACTION_DELAY,
)

DEFAULT_DXF_DIR = Path(__file__).parent / "cutting_templates" / "dxf"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "cutting_templates"


def parse_dxf_filename(filename: str, config: LayoutConfig) -> tuple[str, str] | None:
    """Extract paper_size and card_size from a DXF filename.

    Expected format: {paper_size}_{card_size}_v{N}.dxf
    Card sizes may contain underscores (e.g. poker_half, bridge_square).
    Matches against known paper sizes in layouts.json, then strips
    the version suffix and checks if the remainder is a known card size.
    """
    stem = Path(filename).stem

    for paper_size in config.paper_sizes:
        if stem.startswith(paper_size + "_"):
            remainder = stem[len(paper_size) + 1:]
            # Strip version suffix (_v1, _v2, etc.)
            card_size = re.sub(r"_v\d+$", "", remainder)
            if paper_size in config.layouts and card_size in config.layouts[paper_size]:
                return paper_size, card_size

    return None


def get_paper_dimensions(filename: str, config: LayoutConfig) -> tuple[str, str]:
    """Get paper width and height unit strings for a DXF file.

    Parses paper_size from the filename and looks up dimensions
    in layouts.json. Falls back to letter size.
    """
    parts = parse_dxf_filename(filename, config)
    if parts is not None:
        paper_size, _ = parts
        paper_def = config.paper_sizes[paper_size]
        return paper_def.width, paper_def.height

    # Fall back to letter
    paper_def = config.paper_sizes["letter"]
    return paper_def.width, paper_def.height


def get_orientation_for_dxf(filename: str, config: LayoutConfig) -> Orientation:
    """Look up the paper orientation for a DXF file from layouts.json.

    Falls back to landscape if the filename can't be parsed.
    """
    parts = parse_dxf_filename(filename, config)
    if parts is not None:
        paper_size, card_size = parts
        return config.layouts[paper_size][card_size].orientation

    return Orientation.LANDSCAPE


@click.command()
@click.option("--dxf_dir", type=click.Path(exists=True), default=str(DEFAULT_DXF_DIR), show_default=True, help="Directory containing DXF files.")
@click.option("--output_dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR), show_default=True, help="Output directory for .studio3 files.")
@click.option("--studio_path", default=DEFAULT_STUDIO_PATH, show_default=True, help="Path to Silhouette Studio executable.")
@click.option("--action_delay", type=float, default=ACTION_DELAY, show_default=True, help="Delay between UI actions (seconds).")
@click.option("--calibration_file", type=click.Path(), default=None, help="Path to calibration JSON.")
@click.option("--dry_run", is_flag=True, help="List files that would be converted without running Silhouette Studio.")
def cli(dxf_dir, output_dir, studio_path, action_delay, calibration_file, dry_run):
    """Batch convert DXF files to .studio3 with registration marks."""
    dxf_path = Path(dxf_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    config = load_layout_config()

    dxf_files = sorted(dxf_path.glob("*.dxf"))
    if not dxf_files:
        click.echo(f"No DXF files found in {dxf_path}")
        return

    click.echo(f"Found {len(dxf_files)} DXF files in {dxf_path}")
    click.echo()

    # Registration marks: always enabled, thickness=100
    reg_settings = RegistrationSettings(
        enabled=True,
        thickness=100,
    )

    if dry_run:
        for dxf_file in dxf_files:
            output_file = out_path / dxf_file.with_suffix(".studio3").name
            orientation = get_orientation_for_dxf(dxf_file.name, config)
            paper_w, paper_h = get_paper_dimensions(dxf_file.name, config)
            click.echo(f"  {dxf_file.name} -> {output_file.name} ({orientation.value}, {paper_w} x {paper_h})")
        click.echo()
        click.echo("Dry run complete. No files were converted.")
        return

    click.echo("=" * 60)
    click.echo("Batch DXF to Studio3 Converter")
    click.echo("=" * 60)
    click.echo()
    click.echo("WARNING: Do not use mouse/keyboard during conversion!")
    click.echo("Move mouse to top-left corner to abort.")
    click.echo()

    if not click.confirm("Proceed?"):
        click.echo("Aborted.")
        return

    cal_path = Path(calibration_file) if calibration_file else None
    automation = SilhouetteAutomation(studio_path, cal_path, action_delay)

    try:
        automation.start()

        converted = 0
        errors = 0

        for dxf_file in dxf_files:
            output_file = out_path / dxf_file.with_suffix(".studio3").name
            orientation = get_orientation_for_dxf(dxf_file.name, config)
            paper_w, paper_h = get_paper_dimensions(dxf_file.name, config)

            try:
                automation.convert(
                    input_dxf=str(dxf_file),
                    output_studio3=str(output_file),
                    paper_width=paper_w,
                    paper_height=paper_h,
                    orientation=orientation,
                    center=True,
                    registration=reg_settings,
                )
                converted += 1
            except Exception as e:
                click.echo(f"  Error converting {dxf_file.name}: {e}")
                errors += 1

        click.echo()
        click.echo(f"Converted {converted} files ({errors} errors)")

    except KeyboardInterrupt:
        click.echo("\nAborted by user.")
    except Exception as e:
        click.echo(f"\nFail-safe triggered: {e}")
    finally:
        try:
            automation.close()
        except Exception:
            pass


if __name__ == "__main__":
    cli()
