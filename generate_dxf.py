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
import size_convert
from enums import Orientation
from utilities import LayoutConfig, load_layout_config, template_name, resolve_card_size_alias, resolve_paper_size_alias, get_all_card_size_names, get_all_paper_size_names

OUTPUT_DIR = Path("cutting_templates") / "dxf"
LAYOUTS_PATH = Path("assets") / "layouts.json"

layout_config = load_layout_config()
card_size_choices = get_all_card_size_names(layout_config)
paper_size_choices = get_all_paper_size_names(layout_config)


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

# Predefined paper/card sizes from layouts.json
@click.option("--card_size", type=click.Choice(card_size_choices, case_sensitive=False), help="Card size. Cannot be combined with --card_length/--card_width.")
@click.option("--paper_size", type=click.Choice(paper_size_choices, case_sensitive=False), help="Paper size. Cannot be combined with --paper_length/--paper_width.")

# For defining paper/card sizes directly instead of using predefined ones from layouts.json
@click.option("--card_length", type=str, default=None, help="Card length (height) as a size string (e.g. '88mm', '3.5in'). Requires --card_width. Cannot be combined with --card_size.")
@click.option("--card_width", type=str, default=None, help="Card width as a size string (e.g. '63mm', '2.5in'). Requires --card_length. Cannot be combined with --card_size.")
@click.option("--card_radius", type=str, default="3mm", show_default=True, help="Card corner radius as a size string (e.g. '3mm'). Used only with --card_length/--card_width.")
@click.option("--card_name", type=str, default=None, help="Override the card label used for the output filename and --save.")
@click.option("--paper_length", type=str, default=None, help="Paper length (longer dimension) as a size string (e.g. '11in', '297mm'). Requires --paper_width. Cannot be combined with --paper_size.")
@click.option("--paper_width", type=str, default=None, help="Paper width (shorter dimension) as a size string (e.g. '8.5in', '210mm'). Requires --paper_length. Cannot be combined with --paper_size.")
@click.option("--paper_name", type=str, default=None, help="Override the paper label used for the output filename and --save.")
@click.option("--save", "save", is_flag=True, help="Save new card/paper sizes and layout combination to assets/layouts.json.")

# Batch generation options
@click.option("--all", "generate_all", is_flag=True, help="Generate DXF files for all paper/card combinations defined in layouts.json.")
@click.option("--all_optimize", "optimize_all", is_flag=True, help="Generate DXF files for all combinations, optimizing orientation for maximum cards. Updates layouts.json if a better orientation is found.")
@click.option("--new", "generate_new", is_flag=True, help="Generate DXF files only for new paper and card combinations.")

@click.option("--output_dir", type=click.Path(), default=str(OUTPUT_DIR), show_default=True, help="Output directory for DXF files.")
def cli(paper_size, card_size, card_length, card_width, card_radius, paper_length, paper_width, card_name, paper_name, save, generate_all, generate_new, optimize_all, output_dir):
    """Generate DXF cutting templates from layouts.json."""
    config = load_layout_config()

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if optimize_all:
        _generate_all_optimized(config, out)
        return

    if generate_all or generate_new:
        with open(LAYOUTS_PATH, 'r') as f:
            raw_config = json.load(f)

        generated = 0
        skipped = 0
        errors = 0
        error_list = []
        print(f"Generating DXF files to: {out}")
        print()

        for ps, cards in config.layouts.items():
            for cs in cards:
                layout_def = config.layouts[ps][cs]
                name = template_name(ps, cs, layout_def.version)
                output_file = out / f"{name}.dxf"

                if generate_new and output_file.exists():
                    skipped += 1
                    continue

                try:
                    num_cols, num_rows, ml_mm = generate_single_dxf(cs, ps, config, out)
                    raw_config["layouts"][ps][cs]["num_rows"] = num_rows
                    raw_config["layouts"][ps][cs]["num_cols"] = num_cols
                    raw_config["layouts"][ps][cs]["max_length_mm"] = ml_mm
                    generated += 1
                except Exception as e:
                    print(f"  Error: {ps} + {cs}: {e}")
                    error_list.append((f"{ps} + {cs}", e))
                    errors += 1

        if error_list:
            print(f'Errors: {error_list}')

        with open(LAYOUTS_PATH, 'w') as f:
            json.dump(raw_config, f, indent=4)
            f.write('\n')

        print()
        summary = f"Generated {generated} DXF files ({errors} errors)"
        if generate_new:
            summary += f", skipped {skipped} existing"
        print(summary)
        return

    # Validate card dimension options
    has_card_size = card_size is not None
    has_card_dims = card_length is not None or card_width is not None

    if has_card_size and has_card_dims:
        raise click.UsageError("Cannot use --card_size together with --card_length or --card_width.")
    if card_length is not None and card_width is None:
        raise click.UsageError("--card_length requires --card_width.")
    if card_width is not None and card_length is None:
        raise click.UsageError("--card_width requires --card_length.")

    # Validate paper dimension options
    has_paper_size = paper_size is not None
    has_paper_dims = paper_length is not None or paper_width is not None

    if has_paper_size and has_paper_dims:
        raise click.UsageError("Cannot use --paper_size together with --paper_length or --paper_width.")
    if paper_length is not None and paper_width is None:
        raise click.UsageError("--paper_length requires --paper_width.")
    if paper_width is not None and paper_length is None:
        raise click.UsageError("--paper_width requires --paper_length.")

    if not has_card_size and not has_card_dims:
        raise click.UsageError("Provide --card_size or (--card_length and --card_width), or use --all.")
    if not has_paper_size and not has_paper_dims:
        raise click.UsageError("Provide --paper_size or (--paper_length and --paper_width), or use --all.")

    # Resolve aliases
    if has_card_size:
        card_size = resolve_card_size_alias(config, card_size)
    if has_paper_size:
        paper_size = resolve_paper_size_alias(config, paper_size)

    # Resolve card parameters
    if has_card_size:
        card_def = config.card_sizes[card_size]
        resolved_card_width = card_def.width
        resolved_card_height = card_def.height
        resolved_card_radius = card_def.radius
        card_label = card_size
    else:
        resolved_card_width = card_width
        resolved_card_height = card_length
        resolved_card_radius = card_radius
        card_label = f"{card_width}x{card_length}"

    # Resolve paper parameters (stored as landscape: longer dim = width)
    if has_paper_size:
        paper_def = config.paper_sizes[paper_size]
        resolved_paper_width = paper_def.width
        resolved_paper_height = paper_def.height
        paper_label = paper_size
    else:
        pl_mm = size_convert.size_to_mm(paper_length)
        pw_mm = size_convert.size_to_mm(paper_width)
        if pl_mm >= pw_mm:
            resolved_paper_width = paper_length
            resolved_paper_height = paper_width
        else:
            resolved_paper_width = paper_width
            resolved_paper_height = paper_length
        paper_label = f"{paper_width}x{paper_length}"

    # Apply name overrides
    if card_name is not None:
        card_label = card_name
    if paper_name is not None:
        paper_label = paper_name

    # Determine orientation and output name
    if has_card_size and has_paper_size:
        if paper_size not in config.layouts or card_size not in config.layouts.get(paper_size, {}):
            raise click.UsageError(f"No layout defined for {paper_size} + {card_size}. Check layouts.json or use --list.")
        layout_def = config.layouts[paper_size][card_size]
        orientation = layout_def.orientation
        version = layout_def.version
    else:
        orientation = Orientation.LANDSCAPE
        version = 1

    name = template_name(paper_label, card_label, version)
    output_file = out / f"{name}.dxf"

    silhouette = config.silhouette
    ppi = config.ppi

    computed = page_manager.generate_layout(
        orientation=orientation,
        card_width=resolved_card_width,
        card_height=resolved_card_height,
        paper_width=resolved_paper_width,
        paper_height=resolved_paper_height,
        inset=silhouette.inset,
        length=silhouette.length,
        ppi=ppi,
    )

    x_pos = computed.x_pos
    y_pos = computed.y_pos
    num_cols = len(x_pos)
    num_rows = len(y_pos)

    dxf_manager.generate_dxf(
        resolved_card_width,
        resolved_card_height,
        resolved_card_radius,
        x_pos,
        y_pos,
        ppi,
        output_path=str(output_file),
    )

    num_cards = num_cols * num_rows
    print(f"  {paper_label} + {card_label}: {num_cols}x{num_rows} ({num_cards} cards), max_length={computed.max_length_mm}mm -> {output_file}")

    if save:
        with open(LAYOUTS_PATH, 'r') as f:
            raw_config = json.load(f)

        changed = False

        if card_label not in raw_config["card_sizes"]:
            raw_config["card_sizes"][card_label] = {
                "width": resolved_card_width,
                "height": resolved_card_height,
                "radius": resolved_card_radius,
            }
            print(f"  Saved new card size '{card_label}': {resolved_card_width} x {resolved_card_height}, radius {resolved_card_radius}")
            changed = True

        if paper_label not in raw_config["paper_sizes"]:
            raw_config["paper_sizes"][paper_label] = {
                "width": resolved_paper_width,
                "height": resolved_paper_height,
            }
            print(f"  Saved new paper size '{paper_label}': {resolved_paper_width} x {resolved_paper_height}")
            changed = True

        if paper_label not in raw_config["layouts"] or card_label not in raw_config["layouts"].get(paper_label, {}):
            if paper_label not in raw_config["layouts"]:
                raw_config["layouts"][paper_label] = {}
            raw_config["layouts"][paper_label][card_label] = {
                "orientation": orientation.value,
                "version": version,
                "num_rows": num_rows,
                "num_cols": num_cols,
                "max_length_mm": computed.max_length_mm,
            }
            print(f"  Saved new layout '{paper_label}' + '{card_label}'")
            changed = True

        if changed:
            with open(LAYOUTS_PATH, 'w') as f:
                json.dump(raw_config, f, indent=4)
                f.write('\n')
        else:
            print("  No new entries to save.")

    print("Done!")


def _generate_all_optimized(config: LayoutConfig, out: Path):
    """Generate DXF files for all paper/card combinations, optimizing orientation.

    Iterates over every paper_size × card_size combination from layouts.json.
    For existing layouts, re-optimizes orientation and bumps the version if
    it changes. For missing combinations, creates a new layout entry at v1.
    """
    with open(LAYOUTS_PATH, 'r') as f:
        raw_config = json.load(f)

    generated = 0
    added = 0
    errors = 0
    updated = 0
    error_list = []
    print(f"Optimizing orientations and generating DXF files to: {out}")
    print()

    for ps, paper_def in config.paper_sizes.items():
        for cs, card_def in config.card_sizes.items():
            try:
                silhouette = config.silhouette
                ppi = config.ppi

                # Check if a layout already exists for this combination
                existing = (
                    ps in config.layouts
                    and cs in config.layouts[ps]
                )
                if existing:
                    layout_def = config.layouts[ps][cs]
                    existing_orientation = layout_def.orientation
                    version = layout_def.version
                else:
                    existing_orientation = Orientation.LANDSCAPE
                    version = 1

                # Try both orientations, prefer the existing one on ties
                best_count = 0
                best_orientation = existing_orientation
                best_computed = None

                for orient in Orientation:
                    try:
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
                    except ValueError:
                        continue
                    count = len(computed.x_pos) * len(computed.y_pos)
                    if count > best_count or (count == best_count and orient == existing_orientation):
                        best_count = count
                        best_orientation = orient
                        best_computed = computed

                if best_computed is None:
                    print(f"  {ps} + {cs}: no valid layout in either orientation, skipping")
                    continue

                num_cols = len(best_computed.x_pos)
                num_rows = len(best_computed.y_pos)

                if existing:
                    orientation_changed = best_orientation != existing_orientation
                    if orientation_changed:
                        version += 1
                        updated += 1
                    raw_config["layouts"][ps][cs]["orientation"] = best_orientation.value
                    raw_config["layouts"][ps][cs]["version"] = version
                else:
                    # Add new layout entry
                    if ps not in raw_config["layouts"]:
                        raw_config["layouts"][ps] = {}
                    raw_config["layouts"][ps][cs] = {
                        "orientation": best_orientation.value,
                        "version": version,
                    }
                    added += 1

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
                if existing and best_orientation != existing_orientation:
                    change_note = f" (was {existing_orientation.value})"
                elif not existing:
                    change_note = " (new)"
                print(f"  {ps} + {cs}: {num_cols}x{num_rows} ({best_count} cards), max_length={best_computed.max_length_mm}mm -> {output_file}{change_note}")
                generated += 1

            except Exception as e:
                print(f"  Error: {ps} + {cs}: {e}")
                error_list.append((f"{ps} + {cs}", e))
                errors += 1

    if error_list:
        print(f'Errors: {error_list}')

    with open(LAYOUTS_PATH, 'w') as f:
        json.dump(raw_config, f, indent=4)
        f.write('\n')

    print()
    summary = f"Generated {generated} DXF files ({errors} errors)"
    if added > 0:
        summary += f", added {added} new layouts"
    if updated > 0:
        summary += f", updated {updated} orientations"
    print(summary)


if __name__ == "__main__":
    cli()
