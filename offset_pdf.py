import os

import click
import json
import pypdfium2 as pdfium

from utilities import offset_images

# Dimensions of the resized letter-sized sheet
print_width = 3300
print_height = 2550

@click.command()
@click.argument("pdf_path")
@click.option("--output_pdf_path", help="The desired path of the output PDF.")
@click.option("-x", "--x_offset", type=int, help="The desired offset in the x-axis.")
@click.option("-y", "--y_offset", type=int, help="The desired offset in the y-axis.")


def offset_pdf(pdf_path: str, output_pdf_path: str, x_offset, y_offset):

    x_from_config, y_from_config = load_offset_data()
    # Use to check if user wants to store new offset values
    new_x_offset = x_offset
    new_y_offset = y_offset

    if x_offset is None:
        # If x_offset is not provided, use the saved value from the config file if available
        if x_from_config is not None:
            x_offset = x_from_config
        else:
            # If only y_offset is provided and x_offset is not provided, default x_offset to 0
            x_offset = 0

    if y_offset is None:
        # If y_offset is not provided, use the saved value from the config file if available
        if y_from_config is not None:
            y_offset = y_from_config
        else:
            # If only x_offset is provided and y_offset is not provided, default y_offset to 0
            y_offset = 0

    if new_x_offset is not None or new_y_offset is not None:
        print('Would you like to save your offset data for future use? (This will create a file called "data/offset_data.json") [y/n]')
        user_input = input().strip().lower()
        if user_input == 'y' or user_input == 'yes':
            save_data(x_offset, y_offset)
    else:
        print("Using saved offset values from the config file.")
    

    pdf = pdfium.PdfDocument(pdf_path)
    
    # Get all the raw page images from the PDF
    raw_images = []
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        raw_images.append(page.render(scale = 300/72).to_pil().resize((print_width, print_height)))
        
    # Offset images
    final_images = offset_images(raw_images, x_offset, y_offset)
    
    # The default for output_pdf_path is the original path but with _offset.py appended to the end.
    if output_pdf_path is None:
        output_pdf_path = f'{pdf_path.removesuffix(".py")}_offset.py'
    
    output_pdf_path = os.path.join(f"{pdf_path}_offset.pdf")
    final_images[0].save(output_pdf_path, save_all=True, append_images=final_images[1:])
    print(f'offset PDF: {output_pdf_path}')


def save_data(x_offset, y_offset) -> None:
        # Create the directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        # Save the offset data to a JSON file
        offset_data = {
            "x_offset": x_offset,
            "y_offset": y_offset
        }
        with open('data/offset_data.json', 'w') as offset_file:
            json.dump(offset_data, offset_file)
        print('Offset data saved!')


def read_data_file() -> dict:
    if os.path.exists('data/offset_data.json'):
        with open('data/offset_data.json', 'r') as offset_file:
            offset_data = json.load(offset_file)
            return offset_data
    else:
        return None


def load_offset_data() -> tuple:
    offset_data = read_data_file()

    # Check if data is valid, any non-integer values will default to 0
    if offset_data:
        if offset_data['x_offset'] is None:
            print("The saved x_offset is invalid. Defaulting to 0.")
            x_offset = 0  # Default to 0 if the saved value is None
        else:
            x_offset = offset_data['x_offset']  # Use the saved value if it's valid
        if offset_data['y_offset'] is None:
            print("The saved y_offset is invalid. Defaulting to 0.")
            y_offset = 0
        else:
            y_offset = offset_data['y_offset']
        # If x_offset or y_offset is different from the saved values, update the saved data
        if x_offset != offset_data['x_offset'] or y_offset != offset_data['y_offset']:
            save_data(x_offset, y_offset)

    return (x_offset, y_offset)


if __name__ == '__main__':
    offset_pdf()