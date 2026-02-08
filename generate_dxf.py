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
import size_convert
import dxf_manager
from enums import CardSize, PaperSize, Orientation

ASSETS_DIR = Path("assets")
LAYOUTS_FILE = ASSETS_DIR / "layouts.json"
OUTPUT_DIR = Path("cutting_templates") / "dxf"


def load_layout_config() -> dict:
    with open(LAYOUTS_FILE, "r") as f:
        return json.load(f)


def generate_single_dxf(
    card_size: str,
    paper_size: str,
    config: dict,
    output_dir: Path,
):
    """Generate a single DXF file for a paper/card combination."""
    card_def = config["card_sizes"][card_size]
    paper_def = config["paper_sizes"][paper_size]
    layout_def = config["layouts"][paper_size][card_size]
    silhouette = config["silhouette"]
    ppi = config["ppi"]

    orientation = Orientation(layout_def["orientation"])

    computed = page_manager.generate_layout(
        card_size=card_size,
        paper_size=paper_size,
        orientation=orientation,
        card_width=card_def["width"],
        card_height=card_def["height"],
        card_radius=card_def["radius"],
        paper_width=paper_def["width"],
        paper_height=paper_def["height"],
        inset=silhouette["inset"],
        thickness=silhouette["thickness"],
        length=silhouette["length"],
        ppi=ppi,
    )

    x_pos = computed["x_pos"]
    y_pos = computed["y_pos"]

    # Determine card dimensions for DXF (swap if horizontal)
    if orientation == Orientation.HORIZONTAL:
        dxf_width = card_def["height"]
        dxf_height = card_def["width"]
    else:
        dxf_width = card_def["width"]
        dxf_height = card_def["height"]

    output_file = output_dir / f"{paper_size}_{card_size}.dxf"

    dxf_manager.generate_dxf(
        dxf_width,
        dxf_height,
        card_def["radius"],
        x_pos,
        y_pos,
        ppi,
        f"{paper_size}_{card_size}",
        output_path=str(output_file),
    )

    num_cards = len(x_pos) * len(y_pos)
    paper_w_mm = size_convert.size_to_mm(paper_def["width"])
    paper_h_mm = size_convert.size_to_mm(paper_def["height"])
    print(f"  {paper_size} + {card_size}: {num_cards} cards ({paper_w_mm:.0f}x{paper_h_mm:.0f}mm, {orientation.value}) -> {output_file}")


@click.command()
@click.option("--paper_size", type=click.Choice([p.value for p in PaperSize], case_sensitive=False), help="Paper size.")
@click.option("--card_size", type=click.Choice([c.value for c in CardSize], case_sensitive=False), help="Card size.")
@click.option("--all", "generate_all", is_flag=True, help="Generate DXF files for all paper/card combinations defined in layouts.json.")
@click.option("--list", "list_sizes", is_flag=True, help="List available paper/card size combinations and exit.")
@click.option("--output_dir", type=click.Path(), default=str(OUTPUT_DIR), show_default=True, help="Output directory for DXF files.")
def cli(paper_size, card_size, generate_all, list_sizes, output_dir):
    """Generate DXF cutting templates from layouts.json."""
    config = load_layout_config()

    if list_sizes:
        print("Available card sizes:")
        for cs, cs_def in config["card_sizes"].items():
            print(f"  {cs}: {cs_def['width']} x {cs_def['height']}")
        print()
        print("Available paper sizes:")
        for ps, ps_def in config["paper_sizes"].items():
            print(f"  {ps}: {ps_def['width']} x {ps_def['height']}")
        print()
        print("Defined layouts (paper + card -> orientation):")
        for ps, cards in config["layouts"].items():
            for cs, layout in cards.items():
                print(f"  {ps} + {cs}: {layout['orientation']}")
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if generate_all:
        generated = 0
        errors = 0
        print(f"Generating DXF files to: {out}")
        print()

        for ps, cards in config["layouts"].items():
            for cs in cards:
                try:
                    generate_single_dxf(cs, ps, config, out)
                    generated += 1
                except Exception as e:
                    print(f"  Error: {ps} + {cs}: {e}")
                    errors += 1

        print()
        print(f"Generated {generated} DXF files ({errors} errors)")
        return

    if not paper_size or not card_size:
        raise click.UsageError("Provide --paper_size and --card_size, or use --all.")

    if paper_size not in config["layouts"] or card_size not in config["layouts"].get(paper_size, {}):
        raise click.UsageError(f"No layout defined for {paper_size} + {card_size}. Check layouts.json or use --list.")

    generate_single_dxf(card_size, paper_size, config, out)
    print("Done!")


if __name__ == "__main__":
    cli()
