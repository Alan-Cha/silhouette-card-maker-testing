import ezdxf
import re
import size_convert
from ezdxf import units
from typing import List
import math

# Write fixed timestamps and GUIDs so regenerated files are deterministic.
ezdxf.options.write_fixed_meta_data_for_testing = True

def add_rounded_rectangle(msp, x, y, width, height, radius):
    """Add a rounded rectangle as separate LINE + ARC entities (screen Y-down coords).

    Uses separate LINE and ARC entities, NOT a closed polyline (POLYLINE2D/LWPOLYLINE).

    ENTITY TYPE INVESTIGATION SUMMARY
    ----------------------------------
    Two conflicting requirements exist for Silhouette Studio (SS) DXF import:
      (A) Correct image fill orientation (not vertically flipped)
      (B) Individually selectable card paths after import

    POLYLINE2D / LWPOLYLINE (single entity per card):
      - Satisfies (B): each card is one entity, individually selectable after ungrouping.
      - Fails (A): image fills appear vertically flipped in SS, regardless of winding
        direction (CCW/CW), starting vertex, or Y-coordinate convention.
        Tested exhaustively across ~10 variants with no fix found.

    Separate LINE + ARC entities (8 entities per card):
      - Satisfies (A): correct image fill orientation.
      - Fails (B) when 2+ cards are present: SS merges all LINE/ARC entities from the
        file into a single compound path, making cards inseparable.
        Tested with: same layer, per-card DXF layers, DXF GROUP entities -- all merged.
        A single-card DXF works fine (1 card = 1 selectable shape).

    DXF layers and DXF GROUP entities have no effect on SS selectability.
    HATCH entities (LINE+ARC edge path) are invisible/ignored by SS entirely.

    SOLUTION
    --------
    Use LINE + ARC entities (correct fill orientation), and in dxf_to_studio3.py
    use Ctrl+Shift+E ("Release Compound Path") after importing, which breaks the
    merged compound shape into individually selectable card paths.
    """
    # Convert screen Y-down (origin top-left) to DXF Y-up (origin bottom-left)
    y = -y - height

    bl = (x + radius, y + radius)
    br = (x + width - radius, y + radius)
    tr = (x + width - radius, y + height - radius)
    tl = (x + radius, y + height - radius)

    msp.add_line((bl[0], y),         (br[0], y))           # Bottom edge
    msp.add_line((x + width, br[1]), (x + width, tr[1]))   # Right edge
    msp.add_line((tr[0], y + height),(tl[0], y + height))  # Top edge
    msp.add_line((x, tl[1]),         (x, bl[1]))            # Left edge

    # Corner arcs, CCW in DXF Y-up convention
    msp.add_arc(center=br, radius=radius, start_angle=270, end_angle=360)  # BR
    msp.add_arc(center=tr, radius=radius, start_angle=0,   end_angle=90)   # TR
    msp.add_arc(center=tl, radius=radius, start_angle=90,  end_angle=180)  # TL
    msp.add_arc(center=bl, radius=radius, start_angle=180, end_angle=270)  # BL


# Create new DXF document
def generate_dxf(card_width: str, card_height: str, card_radius: str, x_pos: List[int], y_pos: List[int], ppi:int, output_path:str):
    doc = ezdxf.new(dxfversion='R2010')
    float_pattern = r"(?:\d+\.\d*|\.\d+|\d+)"  # matches 1.0, .5, or 2
    # Match in or mm (default=mm)
    in_width = re.fullmatch(rf"({float_pattern})in", card_width)
    if in_width:
        doc.units = units.IN
        width = size_convert.size_to_in(card_width)
        height = size_convert.size_to_in(card_height)
        radius = size_convert.size_to_in(card_radius)
    else:
        doc.units = units.MM
        width = size_convert.size_to_mm(card_width)
        height = size_convert.size_to_mm(card_height)
        radius = size_convert.size_to_mm(card_radius)

    msp = doc.modelspace()

    for x in range(len(x_pos)):
        for y in range(len(y_pos)):
            if doc.units == units.IN:
                pos_x = x_pos[x] / ppi
                pos_y = y_pos[y] / ppi
            else:
                pos_x = x_pos[x] * 25.4 / ppi
                pos_y = y_pos[y] * 25.4 / ppi
            add_rounded_rectangle(msp, pos_x, pos_y, width, height, radius)


    # Strip non-deterministic metadata so regenerated files don't produce
    # spurious diffs when the geometry hasn't changed.
    for var in (
        "$TDCREATE", "$TDUCREATE",
        "$TDUPDATE", "$TDUUPDATE",
        "$FINGERPRINTGUID", "$VERSIONGUID",
    ):
        if var in doc.header:
            del doc.header[var]

    # Save DXF
    doc.saveas(output_path)