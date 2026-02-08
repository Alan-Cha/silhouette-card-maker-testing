#!/usr/bin/env python3
"""
Generate DXF files for all paper/card size combinations.

This script reads layouts.json and generates a DXF cutting template
for each paper/card size combination.

Usage:
    python generate_all_dxf.py [output_folder]

Output files are named: {paper_size}_{card_size}.dxf
"""

import os
import sys
import json
from pathlib import Path

# Import from the main generator
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from generate_studio3 import (
    load_layouts,
    get_card_positions,
    generate_dxf,
    CORNER_RADIUS_MM
)


def main():
    # Output folder
    if len(sys.argv) > 1:
        output_folder = Path(sys.argv[1])
    else:
        output_folder = SCRIPT_DIR / "generated_dxf"

    output_folder.mkdir(parents=True, exist_ok=True)

    # Load layouts
    layouts = load_layouts()

    generated = 0
    errors = 0

    print(f"Generating DXF files to: {output_folder}")
    print()

    for paper_size, paper_data in layouts['paper_layouts'].items():
        for card_size in paper_data['card_layouts'].keys():
            output_name = f"{paper_size}_{card_size}.dxf"
            output_path = output_folder / output_name

            try:
                positions, paper_w, paper_h = get_card_positions(
                    paper_size, card_size, layouts
                )

                generate_dxf(
                    positions,
                    paper_w,
                    paper_h,
                    output_path,
                    CORNER_RADIUS_MM
                )

                generated += 1
            except Exception as e:
                print(f"Error generating {output_name}: {e}")
                errors += 1

    print()
    print(f"Generated {generated} DXF files ({errors} errors)")


if __name__ == "__main__":
    main()
