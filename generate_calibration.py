"""
Generate calibration sheets for printer alignment.

Produces a two-page PDF for each configured paper size. The front page shows a
grid of alignment dots. The back page shows the same grid shifted by (x, y) pixel
offsets with coordinate labels using standard math conventions (positive Y up,
positive X right). Print the PDF double-sided with long-side flip, then compare 
front and back dot positions to measure and correct printer misalignment.
"""

import math
import os
import re
from PIL import Image, ImageDraw, ImageFont

import size_convert
from utilities import load_layout_config

# Specify directory locations
asset_directory = 'assets'

# Static distance from page margin used for all page labels and axis text
MARGIN = 150

layout_config = load_layout_config()

for paper_size, paper_def in layout_config.paper_sizes.items():
    print_width = size_convert.size_to_pixel(paper_def.width, layout_config.ppi)
    print_height = size_convert.size_to_pixel(paper_def.height, layout_config.ppi)

    # Generate a blank white base image
    im = Image.new('RGB', (print_width, print_height), 'white')
    with im:
        font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)
        coord_font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 25)

        front_image = im.copy()
        front_draw = ImageDraw.Draw(front_image)
        front_draw.text((print_width // 2, MARGIN), 'Front', fill=(0, 0, 0), anchor="mt", font=font)

        back_image = im.copy()
        back_draw = ImageDraw.Draw(back_image)
        back_draw.text((print_width // 2, MARGIN), 'Back', fill=(0, 0, 0), anchor="mt", font=font)

        test_size = 25
        test_half_size = math.floor(test_size / 2)
        test_distance = 75

        matrix_size_x = math.floor(print_width / (test_size + test_distance)) - 6
        matrix_half_size_x = math.floor(matrix_size_x / 2)

        matrix_size_y = math.floor(print_height / (test_size + test_distance)) - 6
        matrix_half_size_y = math.floor(matrix_size_y / 2)


        start_x = 0
        if matrix_size_x % 2 > 0:
            start_x = math.floor(print_width / 2) - (matrix_half_size_x * test_distance) - ((matrix_half_size_x + .5) * test_size)
        else:
            if matrix_size_x <= 0:
                raise Exception(f'matrix_size must be greater than 0; received: {matrix_size_x}')
            start_x = math.floor(print_width / 2) - ((matrix_half_size_x - .5) * test_distance) - (matrix_half_size_x * test_size)

        start_y = 0
        if matrix_size_y % 2 > 0:
            start_y = math.floor(print_height / 2) - (matrix_half_size_y * test_distance) - ((matrix_half_size_y + .5) * test_size)
        else:
            if matrix_size_y <= 0:
                raise Exception(f'matrix_size must be greater than 0; received: {matrix_size_y}')
            start_y = math.floor(print_height / 2) - ((matrix_half_size_y - .5) * test_distance) - (matrix_half_size_y * test_size)


        front_draw = ImageDraw.Draw(front_image)
        back_draw = ImageDraw.Draw(back_image)

        for x_index in range(matrix_size_x):
            for y_index in range(matrix_size_y):
                offset_x = x_index * (test_distance + test_size)
                offset_y = y_index * (test_distance + test_size)

                front_element_x = start_x + offset_x
                front_element_y = start_y + offset_y
                front_shape = [(front_element_x, front_element_y), (front_element_x + test_size, front_element_y + test_size)]

                fill="black"
                if x_index == matrix_half_size_x or y_index == matrix_half_size_y:
                    fill="blue"

                front_draw.rectangle(front_shape, fill=fill)

                back_element_x = front_element_x + x_index - matrix_half_size_x
                back_element_y = front_element_y + y_index - matrix_half_size_y
                back_shape = [(back_element_x, back_element_y), (back_element_x + test_size, back_element_y + test_size)]

                back_draw.rectangle(back_shape, fill=fill)

                back_draw.text((back_element_x + test_half_size, back_element_y + test_half_size + 30), f'({x_index - matrix_half_size_x}, {matrix_half_size_y - y_index})', fill="red", anchor="mm", font=coord_font)

        # Back page left-side axis label (vertical, reading top-to-bottom):
        # rotate the image clockwise so we can draw horizontally, then rotate back.
        left_label = '(0, -y) <--- back page ---> (0, +y)'
        back_image = back_image.rotate(-90, expand=True)
        rotated_draw = ImageDraw.Draw(back_image)
        rotated_draw.text((print_height // 2, MARGIN), left_label, fill=(0, 0, 0), anchor="mt", font=font)
        back_image = back_image.rotate(90, expand=True)

        # Back page bottom axis label (horizontal)
        bottom_label = '(-x, 0) <--- back page ---> (+x, 0)'
        back_draw = ImageDraw.Draw(back_image)
        back_draw.text((print_width // 2, print_height - MARGIN - (test_distance / 2)), bottom_label, fill=(0, 0, 0), anchor="mb", font=font)

        # Back page bottom axis label (horizontal)
        angle_label = '+a rotates back page clockwise'
        back_draw = ImageDraw.Draw(back_image)
        back_draw.text((print_width // 2, print_height - MARGIN + (test_distance / 2)), angle_label, fill=(0, 0, 0), anchor="mb", font=font)

        card_list = [front_image, back_image.rotate(180)]
        pdf_path = os.path.join("calibration", f"{paper_size}-calibration.pdf")
        card_list[0].save(pdf_path, save_all=True, append_images=card_list[1:], resolution=300, speed=0, subsampling=0, quality=100)

        # Replace auto-generated timestamps with a fixed placeholder so the PDF
        # doesn't show as modified in git when regenerated with identical content.
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        pdf_bytes = re.sub(rb'D:\d{14}Z', b'D:20000101000000Z', pdf_bytes)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        print(f'Calibration PDF: {pdf_path}')
