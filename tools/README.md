# Cutting Template Tools

This folder contains tools for generating and converting Silhouette Studio cutting templates.

## Overview

There are three approaches to creating .studio3 cutting templates:

| Approach | Reliability | Requirements | Best For |
|----------|-------------|--------------|----------|
| **DXF Generation** | High | None | CI/CD, automation |
| **GUI Automation** | Medium | Silhouette Studio | Batch conversion |
| **Direct .studio3 Generation** | Medium | Template file | Similar layouts |

## Tool 1: DXF Generation (Recommended)

`generate_studio3.py` can generate DXF files directly from your layout configuration.

### Generate a DXF file:

```bash
python tools/generate_studio3.py --paper_size letter --card_size poker --output template.dxf
```

### List available combinations:

```bash
python tools/generate_studio3.py --list
```

### Import DXF into Silhouette Studio:

1. Open Silhouette Studio
2. File → Open → Select the .dxf file
3. File → Save As → Save as .studio3

### Options:

- `--paper_size`: letter, tabloid, a4, a3, archb
- `--card_size`: standard, poker, bridge, tarot, etc.
- `--output`: Output file path (.dxf or .studio3)
- `--corner_radius`: Corner radius in mm (default: 3.0)

---

## Tool 2: GUI Automation (DXF to Studio3)

`dxf_to_studio3_advanced.py` automates Silhouette Studio to convert DXF files to .studio3,
including page orientation, centering, and registration mark settings.

### First-time setup:

```bash
# Install requirements
pip install pyautogui pywinauto pillow click

# Calibrate UI element positions (run once per screen size/DPI)
python tools/dxf_to_studio3_advanced.py calibrate
```

The calibrate command starts Silhouette Studio at a fixed window size and prompts you
to hover over each UI element. Coordinates are saved to `silhouette_ui_coordinates.json`
(commit this to the repo so others can use it).

### Convert a DXF file:

```bash
python tools/dxf_to_studio3_advanced.py convert input.dxf output.studio3
python tools/dxf_to_studio3_advanced.py convert input.dxf output.studio3 --orientation portrait
python tools/dxf_to_studio3_advanced.py convert input.dxf output.studio3 --registration --reg_length 10 --reg_thickness 0.5 --reg_inset 5
```

### Options:

- `--orientation`: portrait or landscape (default: landscape)
- `--no_center`: Skip centering paths to page
- `--registration`: Enable registration marks
- `--reg_length`, `--reg_thickness`, `--reg_inset`: Registration mark dimensions (mm)
- `--studio_path`: Path to Silhouette Studio executable
- `--calibration_file`: Path to calibration JSON

### Important Notes:

- **Do not use the computer during conversion** - the script controls mouse/keyboard
- Move mouse to top-left corner to abort (failsafe)
- Press Ctrl+C to cancel
- Coordinates are window-relative, so the window can be at any position

---

## Tool 3: Direct .studio3 Generation (Experimental)

Generate .studio3 files directly by modifying an existing template:

```bash
python tools/generate_studio3.py --paper_size letter --card_size standard --output new_template.studio3 --template cutting_templates/letter-poker-v2.studio3
```

This approach works best when:
- The number of cards matches the template
- The paper size is the same or similar

---

## .studio3 File Format (Reference)

The .studio3 format is a proprietary binary format with these sections:

1. **Header** (0x000-0x3FF): Magic `silhouette05;` + metadata
2. **Document Data** (0x400+): Settings, media type, margins
3. **Shape Entries**: Autoshape text + binary path data + UUIDs
4. **Footer**: CSV metadata + Base64 JSON layer tree

Key details:
- Coordinates: IEEE 754 float, little-endian, millimeters
- Coordinate unit: 1mm = 20 Silhouette Units
- Corner curves: Cubic Bezier

---

## Workflow Recommendations

### For maintaining cutting templates:

1. **Define layouts** in `assets/layouts.json`
2. **Generate DXF** with `generate_studio3.py`
3. **Import into Silhouette Studio** and fine-tune
4. **Save as .studio3** in `cutting_templates/`
5. **Commit** both the DXF source and .studio3 output

### For CI/CD automation:

1. Generate DXF files in your build pipeline
2. Include instructions for users to import DXF
3. Optionally pre-convert using GUI automation

---

## Troubleshooting

### DXF import issues in Silhouette Studio:

- Ensure the DXF uses millimeter units
- Check that arcs/circles are properly defined
- Try opening in Inkscape first, then export as DXF

### GUI automation failures:

- Increase `STARTUP_WAIT` if Silhouette Studio loads slowly
- Check that no dialogs are blocking the main window
- Ensure screen resolution matches expectations

### .studio3 generation issues:

- The template must have similar card count
- Paper size strings must be same length or shorter
