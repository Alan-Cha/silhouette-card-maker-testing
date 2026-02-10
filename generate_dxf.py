#!/usr/bin/env python3
"""
Generate DXF cutting templates for all or specific paper/card size combinations.

Reads card and paper sizes from assets/layouts.json and computes card
positions dynamically using page_manager. Outputs DXF files to
cutting_templates/dxf/.

Usage:
    python generate_dxf.py --all
    python generate_dxf.py --paper_size letter --card_size poker
    python generate_dxf.py --list
"""

import json
from pathlib import Path

import click

import page_manager
import dxf_manager
from enums import CardSize, PaperSize, Orientation
from utilities import LayoutConfig, load_layout_config, template_name

OUTPUT_DIR = Path("cutting_templates") / "dxf"
LAYOUTS_PATH = Path("assets") / "layouts.json"


def generate_single_dxf(
    card_size: str,
    paper_size: str,
    config: LayoutConfig,
    output_dir: Path,
) -> tuple[int, int, float]:
    """Generate a single DXF file for a paper/card combination.

    Returns:
        (num_cols, num_rows, max_length_mm) tuple.
    """
    card_def = config.card_sizes[card_size]
    paper_def = config.paper_sizes[paper_size]
    layout_def = config.layouts[paper_size][card_size]
    silhouette = config.silhouette
    ppi = config.ppi

    orientation = layout_def.orientation
    version = layout_def.version

    computed = page_manager.generate_layout(
        orientation=orientation,
        card_width=card_def.width,
        card_height=card_def.height,
        paper_width=paper_def.width,
        paper_height=paper_def.height,
        inset=silhouette.inset,
        length=silhouette.length,
        ppi=ppi,
    )

    x_pos = computed.x_pos
    y_pos = computed.y_pos
    num_cols = len(x_pos)
    num_rows = len(y_pos)

    name = template_name(paper_size, card_size, version)
    output_file = output_dir / f"{name}.dxf"

    dxf_manager.generate_dxf(
        card_def.width,
        card_def.height,
        card_def.radius,
        x_pos,
        y_pos,
        ppi,
        output_path=str(output_file),
    )

    num_cards = num_cols * num_rows
    print(f"  {paper_size} + {card_size}: {num_cols}x{num_rows} ({num_cards} cards), max_length={computed.max_length_mm}mm -> {output_file}")
    return num_cols, num_rows, computed.max_length_mm


@click.command()
@click.option("--paper_size", type=click.Choice([p.value for p in PaperSize], case_sensitive=False), help="Paper size.")
@click.option("--card_size", type=click.Choice([c.value for c in CardSize], case_sensitive=False), help="Card size.")
@click.option("--all", "generate_all", is_flag=True, help="Generate DXF files for all paper/card combinations defined in layouts.json.")
@click.option("--all_optimize", "optimize_all", is_flag=True, help="Generate DXF files for all combinations, optimizing orientation for maximum cards. Updates layouts.json if a better orientation is found.")
@click.option("--list", "list_sizes", is_flag=True, help="List available paper/card size combinations and exit.")
@click.option("--output_dir", type=click.Path(), default=str(OUTPUT_DIR), show_default=True, help="Output directory for DXF files.")
def cli(paper_size, card_size, generate_all, optimize_all, list_sizes, output_dir):
    """Generate DXF cutting templates from layouts.json."""
    config = load_layout_config()

    if list_sizes:
        print("Available card sizes:")
        for cs, cs_def in config.card_sizes.items():
            print(f"  {cs}: {cs_def.width} x {cs_def.height}")
        print()
        print("Available paper sizes:")
        for ps, ps_def in config.paper_sizes.items():
            print(f"  {ps}: {ps_def.width} x {ps_def.height}")
        print()
        print("Defined layouts (paper + card -> orientation, version, grid):")
        for ps, cards in config.layouts.items():
            for cs, layout in cards.items():
                grid = ""
                if layout.num_cols is not None and layout.num_rows is not None:
                    grid = f", {layout.num_cols}x{layout.num_rows}"
                print(f"  {ps} + {cs}: {layout.orientation.value}, v{layout.version}{grid}")
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if optimize_all:
        _generate_all_optimized(config, out)
        return

    if generate_all:
        with open(LAYOUTS_PATH, 'r') as f:
            raw_config = json.load(f)

        generated = 0
        errors = 0
        print(f"Generating DXF files to: {out}")
        print()

        for ps, cards in config.layouts.items():
            for cs in cards:
                try:
                    num_cols, num_rows, ml_mm = generate_single_dxf(cs, ps, config, out)
                    raw_config["layouts"][ps][cs]["num_rows"] = num_rows
                    raw_config["layouts"][ps][cs]["num_cols"] = num_cols
                    raw_config["layouts"][ps][cs]["max_length_mm"] = ml_mm
                    generated += 1
                except Exception as e:
                    print(f"  Error: {ps} + {cs}: {e}")
                    errors += 1

        with open(LAYOUTS_PATH, 'w') as f:
            json.dump(raw_config, f, indent=4)
            f.write('\n')

        print()
        print(f"Generated {generated} DXF files ({errors} errors)")
        return

    if not paper_size or not card_size:
        raise click.UsageError("Provide --paper_size and --card_size, or use --all.")

    if paper_size not in config.layouts or card_size not in config.layouts.get(paper_size, {}):
        raise click.UsageError(f"No layout defined for {paper_size} + {card_size}. Check layouts.json or use --list.")

    generate_single_dxf(card_size, paper_size, config, out)
    print("Done!")


def _generate_all_optimized(config: LayoutConfig, out: Path):
    """Generate DXF files for all combinations, optimizing orientation.

    Tries both landscape and portrait for each paper/card combo and picks
    the orientation that maximizes card count. If the optimal orientation
    differs from layouts.json, updates the file with the new orientation
    and a bumped version number.
    """
    with open(LAYOUTS_PATH, 'r') as f:
        raw_config = json.load(f)

    generated = 0
    errors = 0
    updated = 0
    print(f"Optimizing orientations and generating DXF files to: {out}")
    print()

    for ps in list(config.layouts.keys()):
        for cs in list(config.layouts[ps].keys()):
            try:
                card_def = config.card_sizes[cs]
                paper_def = config.paper_sizes[ps]
                silhouette = config.silhouette
                ppi = config.ppi
                layout_def = config.layouts[ps][cs]

                # Try both orientations, prefer the existing one on ties
                best_count = 0
                best_orientation = layout_def.orientation
                best_computed = None

                for orient in Orientation:
                    computed = page_manager.generate_layout(
                        orientation=orient,
                        card_width=card_def.width,
                        card_height=card_def.height,
                        paper_width=paper_def.width,
                        paper_height=paper_def.height,
                        inset=silhouette.inset,
                        length=silhouette.length,
                        ppi=ppi,
                    )
                    count = len(computed.x_pos) * len(computed.y_pos)
                    if count > best_count or (count == best_count and orient == layout_def.orientation):
                        best_count = count
                        best_orientation = orient
                        best_computed = computed

                version = layout_def.version
                orientation_changed = best_orientation != layout_def.orientation

                if orientation_changed:
                    version += 1
                    raw_config["layouts"][ps][cs]["orientation"] = best_orientation.value
                    raw_config["layouts"][ps][cs]["version"] = version
                    updated += 1

                num_cols = len(best_computed.x_pos)
                num_rows = len(best_computed.y_pos)
                raw_config["layouts"][ps][cs]["num_rows"] = num_rows
                raw_config["layouts"][ps][cs]["num_cols"] = num_cols
                raw_config["layouts"][ps][cs]["max_length_mm"] = best_computed.max_length_mm

                name = template_name(ps, cs, version)
                output_file = out / f"{name}.dxf"

                dxf_manager.generate_dxf(
                    card_def.width, card_def.height, card_def.radius,
                    best_computed.x_pos, best_computed.y_pos, ppi,
                    output_path=str(output_file),
                )

                change_note = ""
                if orientation_changed:
                    change_note = f" (was {layout_def.orientation.value})"
                print(f"  {ps} + {cs}: {num_cols}x{num_rows} ({best_count} cards), max_length={best_computed.max_length_mm}mm -> {output_file}{change_note}")
                generated += 1

            except Exception as e:
                print(f"  Error: {ps} + {cs}: {e}")
                errors += 1

    with open(LAYOUTS_PATH, 'w') as f:
        json.dump(raw_config, f, indent=4)
        f.write('\n')

    print()
    summary = f"Generated {generated} DXF files ({errors} errors)"
    if updated > 0:
        summary += f", updated {updated} orientations in layouts.json"
    print(summary)


if __name__ == "__main__":
    cli()
