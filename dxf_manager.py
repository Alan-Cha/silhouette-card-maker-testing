import math
import ezdxf
import re
import size_convert
from ezdxf import units
from typing import List

# Write fixed timestamps and GUIDs so regenerated files are deterministic.
ezdxf.options.write_fixed_meta_data_for_testing = True

def add_rounded_rectangle(msp, x, y, width, height, radius):
    """Add a rounded rectangle as a single closed LWPOLYLINE with bulge factors.

    Uses LWPOLYLINE with bulge-encoded arcs so Silhouette Studio sees one
    connected path and renders smooth line-to-arc transitions.

    LINE + ARC entities (tried instead, twice) were rejected both times:
    - Loose LINE/ARC entities in modelspace get merged by SS into a single
      compound path across all cards in the file, making individual cards
      unselectable after import.
    - Wrapping the LINE+ARC shape in a block and placing each card via an
      INSERT avoids that merge (each INSERT is one selectable object), but
      SS then renders the line-to-arc joins with a visible sharp corner on
      one side of each arc instead of a smooth transition. Verified on SS
      5.0.414ss. This alone rules out LINE+ARC regardless of the
      selectability fix, since a sharp corner artifact on the cutting path
      isn't acceptable.

    NOTE: SS vertically mirrors image fills for closed-polyline entities
    (LINE+ARC does not have this problem, but can't be used — see above).
    dxf_to_studio3.py's flip_vertically() step corrects the fill by flipping
    the whole imported object, which also mirrors the cutting path itself.
    That's accepted here because generate_dxf() only supports a single
    uniform corner radius, so every card shape is vertically symmetric and
    mirroring it has no visible effect on the cut.

    Bulge factor for a 90° CCW arc = tan(22.5°) ≈ 0.4142.
    Positive bulge = CCW arc (left of travel direction).
    """
    # Convert screen Y-down (origin top-left) to DXF Y-up (origin bottom-left)
    y = -y - height

    BULGE = math.tan(math.radians(22.5))  # 90° CCW corner arc

    # Vertices: arc-start vertices carry the bulge value; edge-end vertices carry none.
    # Format: (x, y, bulge) — omitting bulge defaults to 0 (straight segment).
    points = [
        (x + width - radius, y,              BULGE),  # BR arc start
        (x + width,          y + radius),             # end of BR arc / bottom of right edge
        (x + width,          y + height - radius, BULGE),  # TR arc start
        (x + width - radius, y + height),             # end of TR arc / right of top edge
        (x + radius,         y + height,     BULGE),  # TL arc start
        (x,                  y + height - radius),    # end of TL arc / top of left edge
        (x,                  y + radius,     BULGE),  # BL arc start
        (x + radius,         y),                      # end of BL arc / left of bottom edge
    ]
    msp.add_polyline2d(points, format="xyb", close=True)


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