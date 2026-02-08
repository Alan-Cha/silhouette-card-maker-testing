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

## Tool 2: GUI Automation (Batch DXF to Studio3)

If you have many DXF files, use the automation scripts to batch convert them.

### Python Script (Cross-platform):

```bash
# Install requirements
pip install pyautogui pillow pywinauto

# Run conversion
python tools/dxf_to_studio3.py input_folder/ output_folder/

# Dry run (list files without converting)
python tools/dxf_to_studio3.py input_folder/ --dry-run
```

### PowerShell Script (Windows):

```powershell
.\tools\dxf_to_studio3.ps1 -InputFolder "C:\DXF_Files" -OutputFolder "C:\Studio3_Files"
```

### Important Notes:

- **Do not use the computer during conversion** - the script controls mouse/keyboard
- Move mouse to top-left corner to abort (failsafe)
- Press Ctrl+C to cancel

---

## Tool 3: Direct .studio3 Generation (Experimental)

Generate .studio3 files directly by modifying an existing template:

```bash
python tools/generate_studio3.py --paper_size letter --card_size standard --output new_template.studio3 --template cutting_templates/letter_poker_v2.studio3
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
