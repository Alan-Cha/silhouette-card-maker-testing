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

import size_convert

from enums import Orientation
from utilities import LayoutConfig, load_layout_config, template_name
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

    Expected format: {paper_size}-{card_size}-v{N}.dxf
    Card sizes may contain underscores (e.g. poker_half, bridge_square).
    Splits on the first hyphen to separate paper_size from the rest,
    then strips the version suffix and checks if the remainder is a
    known card size.
    """
    stem = Path(filename).stem

    for paper_size in config.paper_sizes:
        if stem.startswith(paper_size + "-"):
            remainder = stem[len(paper_size) + 1:]
            # Strip version suffix (-v1, -v2, etc.)
            card_size = re.sub(r"-v\d+$", "", remainder)
            if paper_size in config.layouts and card_size in config.layouts[paper_size]:
                return paper_size, card_size

    return None


def get_paper_dimensions(paper_size: str | None, config: LayoutConfig) -> tuple[str, str]:
    """Get paper width and height unit strings for a paper size.

    Falls back to letter size if paper_size is None or unknown.
    """
    if paper_size is not None and paper_size in config.paper_sizes:
        paper_def = config.paper_sizes[paper_size]
        return paper_def.width, paper_def.height

    paper_def = config.paper_sizes["letter"]
    return paper_def.width, paper_def.height


def get_orientation_for_dxf(paper_size: str | None, card_size: str | None, config: LayoutConfig) -> Orientation:
    """Look up the paper orientation for a paper/card size pair from layouts.json.

    Falls back to landscape if either size is None.
    """
    if paper_size is not None and card_size is not None:
        return config.layouts[paper_size][card_size].orientation

    return Orientation.LANDSCAPE


def get_max_length_for_dxf(paper_size: str | None, card_size: str | None, config: LayoutConfig, unit: str) -> float | None:
    """Look up the max registration mark length for a paper/card size pair.

    Args:
        paper_size: Paper size key (e.g. "letter"), or None.
        card_size: Card size key (e.g. "poker"), or None.
        config: Loaded layout config.
        unit: "mm" or "in".

    Returns:
        Max length in the requested unit, or None if not available.
    """
    if paper_size is not None and card_size is not None:
        layout_reg = config.layouts[paper_size][card_size].registration
        mm = size_convert.size_to_mm(layout_reg.length) if layout_reg is not None and layout_reg.length is not None else None
        if mm is None:
            return None
        if unit == "in":
            return round(mm / 25.4, 4)
        return mm

    return None


@click.command()
@click.option("--dxf_dir", type=click.Path(exists=True), default=str(DEFAULT_DXF_DIR), show_default=True, help="Directory containing DXF files.")
@click.option("--output_dir", type=click.Path(), default=str(DEFAULT_OUTPUT_DIR), show_default=True, help="Output directory for .studio3 files.")
@click.option("--unit", type=click.Choice(["mm", "in"], case_sensitive=False), required=True, help="Unit for registration mark values (must match Silhouette Studio's setting).")
@click.option("--studio_path", default=DEFAULT_STUDIO_PATH, show_default=True, help="Path to Silhouette Studio executable.")
@click.option("--action_delay", type=float, default=ACTION_DELAY, show_default=True, help="Delay between UI actions (seconds).")
@click.option("--calibration_file", type=click.Path(), default=None, help="Path to calibration JSON.")
@click.option("--new", "generate_new", is_flag=True, help="Only convert layouts whose .studio3 file is missing (based on layouts.json versions).")
@click.option("--dry_run", is_flag=True, help="List files that would be converted without running Silhouette Studio.")
def cli(dxf_dir, output_dir, unit, studio_path, action_delay, calibration_file, generate_new, dry_run):
    """Batch convert DXF files to .studio3 with registration marks."""
    dxf_path = Path(dxf_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    config = load_layout_config()

    if generate_new:
        # Derive expected DXF/studio3 filenames from layouts.json
        dxf_files = []
        for ps, cards in config.layouts.items():
            for cs, layout_def in cards.items():
                name = template_name(ps, cs, layout_def.version)
                studio3_file = out_path / f"{name}.studio3"
                if not studio3_file.exists():
                    dxf_file = dxf_path / f"{name}.dxf"
                    if dxf_file.exists():
                        dxf_files.append(dxf_file)
                    else:
                        click.echo(f"  Warning: missing DXF {dxf_file.name} for {ps} + {cs}")
        dxf_files.sort()
    else:
        dxf_files = sorted(dxf_path.glob("*.dxf"))

    if not dxf_files:
        if generate_new:
            click.echo("All .studio3 files are up to date.")
        else:
            click.echo(f"No DXF files found in {dxf_path}")
        return

    click.echo(f"Found {len(dxf_files)} DXF files to convert")
    click.echo(f"Registration mark unit: {unit}")
    click.echo()

    if dry_run:
        for dxf_file in dxf_files:
            output_file = out_path / dxf_file.with_suffix(".studio3").name
            paper_size, card_size = parse_dxf_filename(dxf_file.name, config) or (None, None)
            orientation = get_orientation_for_dxf(paper_size, card_size, config)
            paper_w, paper_h = get_paper_dimensions(paper_size, config)
            max_len = get_max_length_for_dxf(paper_size, card_size, config, unit)
            len_str = f", max_length={max_len}{unit}" if max_len is not None else ""
            click.echo(f"  {dxf_file.name} -> {output_file.name} ({orientation.value}, {paper_w} x {paper_h}{len_str})")
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
            paper_size, card_size = parse_dxf_filename(dxf_file.name, config) or (None, None)
            orientation = get_orientation_for_dxf(paper_size, card_size, config)
            paper_w, paper_h = get_paper_dimensions(paper_size, config)
            max_len = get_max_length_for_dxf(paper_size, card_size, config, unit)

            # Registration marks: always enabled, thickness=100,
            # length set to the computed max for this layout.
            reg_settings = RegistrationSettings(
                enabled=True,
                length=max_len if max_len is not None else 0,
                thickness=100,
            )

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
