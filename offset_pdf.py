import os
import click
import pypdfium2 as pdfium

from utilities import (
    load_saved_offset, 
    offset_images, 
    save_offset, 
    save_offset_profile,
    load_offset_profiles,
    list_offset_profiles,
    delete_offset_profile,
    set_default_offset_profile
)

output_directory = os.path.join('game', 'output')
default_output_pdf_path = os.path.join(output_directory, 'game.pdf')

@click.command()
@click.option("--pdf_path", default=default_output_pdf_path, help="The path of the input PDF.")
@click.option("--output_pdf_path", help="The desired path of the offset PDF.")
@click.option("-x", "--x_offset", type=int, help="The desired offset in the x-axis.")
@click.option("-y", "--y_offset", type=int, help="The desired offset in the y-axis.")
@click.option("-s", "--save", default=False, is_flag=True, help="Save the x and y offset values (legacy mode).")
@click.option("--save_profile", help="Save offset as a named profile (e.g., 'letter_printer', 'a4_office').")
@click.option("--paper_size", help="Paper size for the profile (e.g., 'letter', 'a4', 'tabloid').")
@click.option("--description", help="Description for the offset profile.")
@click.option("--list_profiles", default=False, is_flag=True, help="List all saved offset profiles.")
@click.option("--delete_profile", help="Delete a saved offset profile by name.")
@click.option("--set_default", help="Set a profile as the default.")
@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")

def offset_pdf(pdf_path, output_pdf_path, x_offset, y_offset, save, save_profile, paper_size, description, list_profiles, delete_profile, set_default, ppi):
    
    # Handle profile management commands first
    if list_profiles:
        profiles = load_offset_profiles()
        if not profiles.profiles:
            print("No offset profiles found.")
        else:
            print(f"Available offset profiles:")
            print(f"Default: {profiles.default_profile or 'None'}")
            print()
            for name, profile in profiles.profiles.items():
                default_marker = " (default)" if name == profiles.default_profile else ""
                print(f"  {name}{default_marker}")
                print(f"    Description: {profile.description}")
                print(f"    Paper Size: {profile.paper_size or 'Not specified'}")
                print(f"    Offsets: x={profile.x_offset}, y={profile.y_offset}")
                print(f"    Created: {profile.created_at}")
                print()
        return
    
    if delete_profile:
        delete_offset_profile(delete_profile)
        return
    
    if set_default:
        set_default_offset_profile(set_default)
        return
    
    # Proceed with offset calculation and PDF processing
    new_x_offset = 0
    new_y_offset = 0

    # Load legacy offset if available
    saved_offset = load_saved_offset()
    if saved_offset is not None:
        new_x_offset = saved_offset.x_offset
        new_y_offset = saved_offset.y_offset
        print(f'Loaded legacy offset: x={new_x_offset}, y={new_y_offset}')

    # Check for new offset values
    if x_offset is not None:
        new_x_offset = x_offset

    if y_offset is not None:
        new_y_offset = y_offset

    print(f'Using x offset: {new_x_offset}, y offset: {new_y_offset}')

    # Save offset (legacy mode or new profile mode)
    if save:
        save_offset(new_x_offset, new_y_offset)
        print('Saved offset (legacy mode)')
    
    if save_profile:
        if x_offset is None or y_offset is None:
            print("Error: Both --x_offset and --y_offset must be specified when saving a profile")
            return
        
        save_offset_profile(
            name=save_profile,
            x_offset=new_x_offset,
            y_offset=new_y_offset,
            paper_size=paper_size or "",
            description=description or f"Offset profile for {paper_size or 'custom setup'}"
        )

    try:
        pdf = pdfium.PdfDocument(pdf_path)

        # Get all the raw page images from the PDF
        raw_images = []
        for page_number in range(len(pdf)):
            print(f"Page {page_number + 1}")
            page = pdf.get_page(page_number)
            raw_images.append(page.render(ppi/72).to_pil())

        # Offset images
        final_images = offset_images(raw_images, new_x_offset, new_y_offset, ppi)

        # The default for output_pdf_path is the original path but with _offset.py appended to the end.
        if output_pdf_path is None:
            output_pdf_path = f'{pdf_path.removesuffix(".pdf")}_offset.pdf'

        final_images[0].save(output_pdf_path, save_all=True, append_images=final_images[1:], resolution=ppi, speed=0, subsampling=0, quality=100)
        print(f'Offset PDF: {output_pdf_path}')
    except FileNotFoundError as e:
        print(f"Cannot offset nonexistent PDF: {e}")

if __name__ == '__main__':
    offset_pdf()