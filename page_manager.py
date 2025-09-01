import json
import math
import os
from types import SimpleNamespace
from xml.dom import ValidationErr
from dxf_manager import generate_dxf
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
from PIL import Image
import io
import size_convert

# Specify directory locations
sizing_path = os.path.join('assets', 'sizing.json')


def generate_layout(
    card_size: str,
    paper_size: str,
    orientation: bool, #true=horizontal / false:vertical
    card_width: str = None,
    card_height: str = None,
    card_radius: str = None,
    paper_width: str = None,
    paper_height: str = None,
    inset: str = None, 
    thickness: str = None, 
    length: str = None, 
    dxf: bool = False
):
    with open(sizing_path, 'r') as sizing_file:
        try:
            sizing = json.load(sizing_file, object_hook=lambda d: SimpleNamespace(**d))

        except ValidationErr as e:
            raise Exception(f'Cannot parse sizing.json: {e}.')

        if card_size=="custom":
            if card_width is None or card_height is None or card_radius is None:
                raise Exception(f'Error: card_width and card_height and card_radius required for custom card size.')
        else:
            # card_layout_size represents the size of a card
            if not hasattr(sizing.card_sizes, card_size):
                raise Exception(f'Unsupported card size "{card_size}". Try card sizes: {sizing.card_sizes.keys()}.')
            card_width = getattr(sizing.card_sizes, card_size).width
            card_height = getattr(sizing.card_sizes, card_size).height
            card_radius = getattr(sizing.card_sizes, card_size).radius
        
        if paper_size=="custom":
            if paper_width is None or paper_height is None:
                raise Exception(f'Error: paper_width and paper_height required for custom paper size.')
        else:
            # paper_layout represents the size of a paper and all possible card layouts
            if not hasattr(sizing.paper_sizes, paper_size):
                raise Exception(f'Unsupported paper size "{paper_size}". Try paper sizes: {sizing.paper_sizes.keys()}.')
            paper_width=getattr(sizing.paper_sizes, paper_size).width
            paper_height=getattr(sizing.paper_sizes, paper_size).height

    return generate_custom_layout(card_width, 
                            card_height, 
                            card_radius, 
                            paper_width,
                            paper_height,
                            orientation,
                            sizing.ppi,
                            card_size,
                            paper_size,
                            inset if inset is not None else sizing.silhouette.inset, 
                            thickness if thickness is not None else sizing.silhouette.thickness, 
                            length if length is not None else sizing.silhouette.length, 
                            dxf
                            )
    
def generate_reg_mark(
    paper_size: str,
    paper_width: str = None,
    paper_height: str = None,
    inset: str = None, 
    thickness: str = None, 
    length: str = None, 
):
    with open(sizing_path, 'r') as sizing_file:
        try:
            sizing = json.load(sizing_file, object_hook=lambda d: SimpleNamespace(**d))

        except ValidationErr as e:
            raise Exception(f'Cannot parse sizing.json: {e}.')
        
        if paper_size=="custom":
            if paper_width is None or paper_height is None:
                raise Exception(f'Error: paper_width and paper_height required for Custom size.')
        else:
            # paper_layout represents the size of a paper and all possible card layouts
            if not hasattr(sizing.paper_sizes, paper_size):
                raise Exception(f'Unsupported paper size "{paper_size}". Try paper sizes: {sizing.paper_sizes.keys()}.')
            paper_width=getattr(sizing.paper_sizes, paper_size).width
            paper_height=getattr(sizing.paper_sizes, paper_size).height
            
        return generate_custom_reg_mark(paper_width,
                                paper_height,
                                inset if inset is not None else sizing.silhouette.inset, 
                                thickness if thickness is not None else sizing.silhouette.thickness, 
                                length if length is not None else sizing.silhouette.length, 
                                sizing.ppi)


def generate_custom_layout(
    card_width: str,
    card_height: str,
    card_radius: str,
    page_width: str,
    page_height: str,
    orientation: bool, #true=horizontal / false:vertical
    ppi: int,
    card_size: str,
    paper_size: str,    
    inset: str, 
    thickness: str, 
    length: str, 
    dxf: bool
):
    #maximum bleed of 1mm and space to registration marks of 2mm
    bleed_x_px = size_convert.size_to_pixel("1mm", ppi)
    bleed_y_px = bleed_x_px
    space_x_px = size_convert.size_to_pixel("2mm", ppi)
    space_y_px = space_x_px
    
    #Page size to pixels
    page_width_px = size_convert.size_to_pixel(page_width, ppi)
    page_height_px = size_convert.size_to_pixel(page_height, ppi)
    
    #10mm min inset + 5mm length of silhouette at 300ppi + 1/2 thickness
    min_margin = size_convert.size_to_pixel(inset, ppi)
    margin_x = size_convert.size_to_pixel(inset, ppi) + size_convert.size_to_pixel(length, ppi) + round(size_convert.size_to_pixel(thickness, ppi)/2)
    margin_y = margin_x
    
    if orientation:
        card_width_px = size_convert.size_to_pixel(card_height, ppi)
        card_height_px = size_convert.size_to_pixel(card_width, ppi)
    else:
        card_width_px = size_convert.size_to_pixel(card_width, ppi)
        card_height_px = size_convert.size_to_pixel(card_height, ppi)
    
    available_width = page_width_px - (2 * (margin_x))
    available_height = page_height_px - (2 * (margin_y))
    
    min_available_width = page_width_px - (2 * min_margin)
    min_available_height = page_height_px - (2 * min_margin)
    
    #calculate num rows/cols
    num_rows = math.floor((available_height) / (card_height_px))
    num_cols = math.floor((available_width) / (card_width_px))
    
    #Validate is space available outside main margins
    max_num_rows = math.floor((min_available_height) / (card_height_px))
    max_num_cols = math.floor((min_available_width) / (card_width_px))
    
    #Validate which margin to expand
    if num_rows<max_num_rows and num_cols<max_num_cols:
        #Expand side with biggest spare room (best bleed)
        filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))
        filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))
        if (filled_height - available_height) > (filled_width - available_width):
            num_rows=max_num_rows
            margin_y=min_margin
            space_y_px = 0
            available_height = min_available_height
        else:
            num_cols=max_num_cols
            margin_x=min_margin
            space_x_px = 0
            available_width = min_available_width
    elif num_rows<max_num_rows and num_cols==max_num_cols:
        num_rows=max_num_rows
        margin_y=min_margin
        space_y_px = 0
        available_height = min_available_height
    elif num_rows==max_num_rows and num_cols<max_num_cols:
        num_cols=max_num_cols
        margin_x=min_margin
        space_x_px = 0
        available_width = min_available_width
    else:
        filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))
        filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))
        if 2 * bleed_x_px < available_width - filled_width:
            margin_y=min_margin
            available_height = min_available_height          
        if 2 * bleed_y_px < available_height - filled_height:    
            available_width = min_available_width
            margin_x=min_margin
            
        
    #Calculate max bleed and min space to registration marks
    filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))
    filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))

    while available_height < filled_height:
        if bleed_y_px == 0:
            space_y_px = space_y_px - 1 
        else:
            bleed_y_px = bleed_y_px - 1
        filled_height = card_height_px * num_rows + (2 * space_y_px) + (bleed_y_px * (num_rows - 1))

    while available_width < filled_width:
        if bleed_x_px == 0:
            space_x_px = space_x_px - 1 
        else:
            bleed_x_px = bleed_x_px - 1
        filled_width = card_width_px * num_cols + (2 * space_x_px) + (bleed_x_px * (num_cols - 1))


    start_x = round(margin_x + space_x_px + ((available_width - filled_width) / 2))
    start_y = round(margin_y + space_y_px + ((available_height - filled_height) / 2))
    
    x_pos=[start_x]
    y_pos=[start_y]
        
    for x in range(1, num_cols):  # fill remanining values
        x_pos.append(start_x + (x * (card_width_px + bleed_x_px)))
    
    for y in range(1, num_rows):  # fill remanining values
        y_pos.append(start_y + (y * (card_height_px + bleed_y_px)))
        
    custom_paper_size = ""
    if paper_size=="custom":
        custom_paper_size = f'({page_width}x{page_height})'
        
    custom_card_size = ""
    if card_size=="custom":
        custom_card_size = f'({card_width}x{card_height}R{card_radius})'
    
    orientation_text = "horizontal" if orientation else "vertical"
    
    #Generate template
    if dxf:
        if orientation:
            generate_dxf(card_height, card_width, card_radius, x_pos, y_pos, ppi, f"{paper_size}{custom_paper_size}_{card_size}{custom_card_size}_{orientation_text}_{len(x_pos)}x{len(y_pos)}")
        else:
            generate_dxf(card_width, card_height, card_radius, x_pos, y_pos, ppi, f"{paper_size}{custom_paper_size}_{card_size}{custom_card_size}_{orientation_text}_{len(x_pos)}x{len(y_pos)}")
    
        
    card_sizes={}
    card_sizes[card_size] = {
                                "width": card_width_px,
                                "height": card_height_px
                            }
    
    card_layouts={}
    card_layouts[card_size] = {
                                "x_pos": x_pos,
                                "y_pos": y_pos,
                                "template": f"{paper_size}{custom_paper_size}_{card_size}{custom_card_size}_{orientation_text}_{len(x_pos)}x{len(y_pos)}"
                            }
    paper_layouts={}
    paper_layouts[paper_size] = {
                                "width":page_width_px,
                                "height":page_height_px,
                                "card_layouts":card_layouts
                            }
    return {
        "card_sizes": card_sizes,
        "paper_layouts": paper_layouts
    }
    
    
def generate_custom_reg_mark(paper_width:str, paper_height:str, inset:str, thickness:str, length:str, dpi:int):
    # Paper size in mm
    paper_width_mm = size_convert.size_to_mm(paper_width)
    paper_height_mm = size_convert.size_to_mm(paper_height)
    inset_mm = size_convert.size_to_mm(inset)
    thickness_mm = size_convert.size_to_mm(thickness)
    thickness_pt = size_convert.size_to_pt(thickness)
    length_mm= size_convert.size_to_mm(length)

    # Create figure
    fig = plt.figure(figsize=(paper_width_mm / 25.4, paper_height_mm / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])  # Use full canvas
    ax.set_xlim(0, paper_width_mm)
    ax.set_ylim(0, paper_height_mm)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('white')

    # Add filled black square (5x5mm at 10mm from left and bottom)
    square = Rectangle(
    (inset_mm, paper_height_mm - inset_mm - 5),       # (x, y) position in mm
    5,              # width in mm
    5,              # height in mm
    facecolor='black',
    edgecolor='black',
    linewidth=thickness_pt
    )
    ax.add_patch(square)

    # Horizontal line bottom-left
    x_end = inset_mm + length_mm - (thickness_mm/2)
    x_start = inset_mm
    y_start = inset_mm  
    y_end = inset_mm

    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)


    # Vertical line bottom left
    x_end = inset_mm
    x_start = inset_mm
    y_start = inset_mm
    y_end = inset_mm + length_mm - (thickness_mm/2)

    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)


    # Horizontal line top-right
    x_end = paper_width_mm - inset_mm
    x_start = x_end - length_mm + (thickness_mm/2)
    y_start = paper_height_mm - inset_mm
    y_end = paper_height_mm - inset_mm
    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)

    # Vertical line top-right
    x_end = paper_width_mm - inset_mm
    x_start = paper_width_mm - inset_mm
    y_start = paper_height_mm - inset_mm 
    y_end = y_start - length_mm + (thickness_mm/2)
    line = mlines.Line2D([x_start, x_end], [y_start, y_end], color='black', linewidth=thickness_pt)
    ax.add_line(line)

    # Save output
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='jpg')
    img_buf.seek(0)
    return Image.open(img_buf)