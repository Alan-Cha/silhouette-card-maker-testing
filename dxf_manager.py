import ezdxf
import re
import os
import size_convert
from ezdxf import units
from typing import List
import math

output_directory = os.path.join('game', 'output')

def add_rounded_rectangle(msp, x, y, width, height, radius):
    y=-y-height #corner alignment
    # Define corner centers
    bl = (x + radius, y + radius)  # Bottom-left
    br = (x + width - radius, y + radius)  # Bottom-right
    tr = (x + width - radius, y + height - radius)  # Top-right
    tl = (x + radius, y + height - radius)  # Top-left

    # Lines between arcs
    msp.add_line((bl[0], y), (br[0], y))  # Bottom edge
    msp.add_line((x + width, br[1]), (x + width, tr[1]))  # Right edge
    msp.add_line((tr[0], y + height), (tl[0], y + height))  # Top edge
    msp.add_line((x, tl[1]), (x, bl[1]))  # Left edge

    # Corner arcs (always counter-clockwise in DXF)
    msp.add_arc(center=br, radius=radius, start_angle=270, end_angle=360)  # Bottom-right
    msp.add_arc(center=tr, radius=radius, start_angle=0, end_angle=90)     # Top-right
    msp.add_arc(center=tl, radius=radius, start_angle=90, end_angle=180)   # Top-left
    msp.add_arc(center=bl, radius=radius, start_angle=180, end_angle=270)  # Bottom-left

def add_rounded_rectangle_polyline(msp, x, y, width, height, radius):
    y=-y-height #corner alignment
    bulge = math.tan(math.radians(90 / 4))  # bulge for 90-degree arc ≈ 0.4142
    raw_points = [
        (x + width - radius, y, bulge),  # bottom-right arc
        (x + width, y + radius),  # right side
        (x + width, y + height - radius, bulge),  # top-right arc
        (x + width - radius, y + height),  # top line
        (x + radius, y + height, bulge),  # top-left arc
        (x + 0, y + height - radius),  # left side
        (x + 0, y + radius, bulge),  # bottom-left arc
        (x + radius, y),  # bottom line
    ] 

    msp.add_polyline2d(raw_points, format="xyb", close=True)


# Create new DXF document
def generate_dxf(card_width: str, card_height: str, card_radius: str, x_pos: List[int], y_pos: List[int], ppi:int, filename:str):
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
            add_rounded_rectangle_polyline(msp, pos_x, pos_y, width, height, radius)
        

    # Save DXF
    default_output_path = os.path.join(output_directory, f'{filename}.dxf')
    doc.saveas(default_output_path)
    print("Template DXF file created.")