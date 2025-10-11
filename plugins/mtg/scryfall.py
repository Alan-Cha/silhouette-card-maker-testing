import os
from typing import List, Set, Tuple
import re
import requests
import time
from io import BytesIO
from PIL import Image
import numpy as np

double_sided_layouts = ['transform', 'modal_dfc']

def request_scryfall(
    query: str,
) -> requests.Response:
    r = requests.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    # Sleep for 150 milliseconds, greater than the 100ms requested by Scryfall API documentation
    time.sleep(0.15)

    return r

def fix_card_borders(image_bytes: bytes, border_width: int = 5, brightness_threshold: int = 50) -> bytes:
    """
    Detect and fix grey/dark blue borders on MTG cards by painting them pure black.
    
    Args:
        image_bytes: Image data in bytes
        border_width: Width of border to analyze/fix in pixels
        brightness_threshold: Maximum brightness (0-255) to consider as border
    
    Returns:
        Fixed image data in bytes
    """
    # Load image from bytes
    img = Image.open(BytesIO(image_bytes))
    
    # Convert to numpy array for processing
    img_array = np.array(img)
    height, width = img_array.shape[:2]
    
    # Check if image has alpha channel
    has_alpha = img_array.shape[2] == 4 if len(img_array.shape) == 3 else False
    
    # Define border regions to check/fix
    # Top border
    top_region = img_array[0:border_width, :, :3] if has_alpha else img_array[0:border_width, :, :]
    # Bottom border
    bottom_region = img_array[height-border_width:height, :, :3] if has_alpha else img_array[height-border_width:height, :, :]
    # Left border
    left_region = img_array[:, 0:border_width, :3] if has_alpha else img_array[:, 0:border_width, :]
    # Right border
    right_region = img_array[:, width-border_width:width, :3] if has_alpha else img_array[:, width-border_width:width, :]
    
    # Calculate brightness for each region (average of RGB channels)
    def get_brightness(region):
        return np.mean(region, axis=2)
    
    # Paint dark borders black
    def paint_border_black(region, img_slice):
        brightness = get_brightness(region)
        # Find pixels that are dark but not already black
        dark_mask = (brightness > 0) & (brightness < brightness_threshold)
        
        if has_alpha:
            # Paint RGB channels black, preserve alpha
            img_slice[:, :, 0][dark_mask] = 0  # R
            img_slice[:, :, 1][dark_mask] = 0  # G
            img_slice[:, :, 2][dark_mask] = 0  # B
        else:
            # Paint all channels black
            img_slice[dark_mask] = 0
    
    # Apply border fix to each edge
    paint_border_black(top_region, img_array[0:border_width, :])
    paint_border_black(bottom_region, img_array[height-border_width:height, :])
    paint_border_black(left_region, img_array[:, 0:border_width])
    paint_border_black(right_region, img_array[:, width-border_width:width])
    
    # Convert back to PIL Image
    fixed_img = Image.fromarray(img_array.astype(np.uint8))
    
    # Save to bytes
    output = BytesIO()
    fixed_img.save(output, format='PNG')
    return output.getvalue()

def fetch_card_art(
    index: int,
    quantity: int,

    clean_card_name: str,
    card_set: int,
    card_collector_number: int,
    layout: str,

    front_img_dir: str,
    double_sided_dir: str,
    fix_borders: bool = False
) -> None:
    # Query for the front side
    card_front_image_query = f'https://api.scryfall.com/cards/{card_set}/{card_collector_number}/?format=image&version=png'
    card_art = request_scryfall(card_front_image_query).content
    if card_art is not None:
        # Apply border fix if requested
        if fix_borders:
            card_art = fix_card_borders(card_art)

        # Save image based on quantity
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.png')

            with open(image_path, 'wb') as f:
                f.write(card_art)

    # Get backside of card, if it exists
    if layout in double_sided_layouts:
        card_back_image_query = f'{card_front_image_query}&face=back'
        card_art = request_scryfall(card_back_image_query).content
        if card_art is not None:
            # Apply border fix if requested
            if fix_borders:
                card_art = fix_card_borders(card_art)

            # Save image based on quantity
            for counter in range(quantity):
                image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.png')

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def remove_nonalphanumeric(s: str) -> str:
    return re.sub(r'[^\w]', '', s)

def find_cheapest_printing(printings: List) -> Tuple[dict, float]:
    """
    Find the cheapest printing with a valid USD price.
    
    Args:
        printings: List of card printing dictionaries from Scryfall
    
    Returns:
        Tuple of (cheapest_printing_dict, price) or (None, None) if no prices found
    """
    cheapest = None
    lowest_price = float('inf')
    
    for printing in printings:
        price_str = printing.get('prices', {}).get('usd')
        if price_str:
            try:
                price = float(price_str)
                if price < lowest_price:
                    lowest_price = price
                    cheapest = printing
            except (ValueError, TypeError):
                continue
    
    return (cheapest, lowest_price) if cheapest else (None, None)

def partition_printings(printings: List, condition: List) -> Tuple[List, List]:
    matches = []
    non_matches = []
    for card in printings:
        (matches if condition(card) else non_matches).append(card)
    return matches, non_matches

def progressive_filtering(printings: List, filters):
    pool = printings
    leftovers = []

    for condition in filters:
        matched, not_matched = partition_printings(pool, condition)
        leftovers = not_matched + leftovers
        pool = matched or pool  # Only narrow if we have any matches

    return pool + leftovers

def filtering(printings: List, filters):
    pool = printings

    for condition in filters:
        matched, _ = partition_printings(pool, condition)
        pool = matched

    return pool

def fetch_card(
    index: int,
    quantity: int,

    card_set: str,
    card_collector_number: str,
    ignore_set_and_collector_number: bool,

    name: str,

    prefer_older_sets: bool,
    preferred_sets: Set[str],

    prefer_showcase: bool,
    prefer_extra_art: bool,

    front_img_dir: str,
    double_sided_dir: str,
    
    fix_borders: bool = False,
    show_cost: bool = False,
    cheapest_version: bool = False
) -> float:
    card_price = None
    selected_set = None
    
    if not ignore_set_and_collector_number and card_set != "" and card_collector_number != "":
        card_info_query = f"https://api.scryfall.com/cards/{card_set}/{card_collector_number}"

        # Query for card info
        card_json = request_scryfall(card_info_query).json()
        
        # Extract price if showing cost
        if show_cost:
            price_str = card_json.get('prices', {}).get('usd')
            if price_str:
                try:
                    card_price = float(price_str) * quantity
                    selected_set = card_set
                except (ValueError, TypeError):
                    pass

        fetch_card_art(index, quantity, remove_nonalphanumeric(card_json['name']), card_set, card_collector_number, card_json['layout'], front_img_dir, double_sided_dir, fix_borders)

    else:
        if name == "":
            raise Exception()

        # Filter out symbols from card names
        clear_card_name = remove_nonalphanumeric(name)

        card_info_query = f'https://api.scryfall.com/cards/named?exact={clear_card_name}'

        # Query for card info
        card_json = request_scryfall(card_info_query).json()

        set = card_json["set"]
        collector_number = card_json["collector_number"]

        # If cheapest version is requested or preferred options are used, then filter over prints
        if cheapest_version or prefer_older_sets or len(preferred_sets) > 0 or prefer_showcase or prefer_extra_art:
            # Get available printings
            prints_search_json = request_scryfall(card_json['prints_search_uri']).json()
            card_printings = prints_search_json['data']

            if cheapest_version:
                # Find the cheapest printing, ignoring all other preferences
                cheapest_print, price = find_cheapest_printing(card_printings)
                if cheapest_print:
                    set = cheapest_print["set"]
                    collector_number = cheapest_print["collector_number"]
                    if show_cost:
                        card_price = price * quantity
                        selected_set = set
                else:
                    print(f'No price found for "{name}". Using default printing.')
            else:
                # Optional reverse for older preferences
                if prefer_older_sets:
                    card_printings.reverse()

                # Define filters in order of preference
                filters = [
                    lambda c: c['nonfoil'],
                    lambda c: not c['digital'],
                    lambda c: not c['promo'],
                    lambda c: c['set'] in preferred_sets,
                    lambda c: not prefer_showcase ^ ('frame_effects' in c and 'showcase' in c['frame_effects']),
                    lambda c: not prefer_extra_art ^ (c['full_art'] or c['border_color'] == "borderless" or ('frame_effects' in c and 'extendedart' in c['frame_effects']))
                ]

                # Apply progressive filtering
                filtered_printings = progressive_filtering(card_printings, filters)

                if len(filtered_printings) == 0:
                    print(f'No printings found for "{name}" with preferred options. Using default instead.')
                else:
                    best_print = filtered_printings[0]
                    set = best_print["set"]
                    collector_number = best_print["collector_number"]
                    
                    # Extract price if showing cost
                    if show_cost:
                        price_str = best_print.get('prices', {}).get('usd')
                        if price_str:
                            try:
                                card_price = float(price_str) * quantity
                                selected_set = set
                            except (ValueError, TypeError):
                                pass
        
        # If no filtering was done and we need price, get it from the default card
        if show_cost and card_price is None:
            price_str = card_json.get('prices', {}).get('usd')
            if price_str:
                try:
                    card_price = float(price_str) * quantity
                    selected_set = set
                except (ValueError, TypeError):
                    pass

        # Fetch card art
        fetch_card_art(
            index,
            quantity,
            clear_card_name,
            set,
            collector_number,
            card_json['layout'],
            front_img_dir,
            double_sided_dir,
            fix_borders
        )
    
    # Display price information if requested
    if show_cost:
        if card_price is not None:
            unit_price = card_price / quantity if quantity > 0 else 0
            print(f'  Price: ${unit_price:.2f} x {quantity} = ${card_price:.2f} (set: {selected_set})')
        else:
            print(f'  Price: N/A')
    
    return card_price if card_price is not None else 0.0

def get_handle_card(
    ignore_set_and_collector_number: bool,

    prefer_older_sets: bool,
    preferred_sets: Set[str],

    prefer_showcase: bool,
    prefer_extra_art: bool,

    front_img_dir: str,
    double_sided_dir: str,
    
    fix_borders: bool = False,
    show_cost: bool = False,
    cheapest_version: bool = False
):
    # Use a list to track total cost (mutable container for closure)
    total_cost = [0.0]
    card_count = [0]
    
    def configured_fetch_card(index: int, name: str, card_set: str = None, card_collector_number: int = None, quantity: int = 1):
        cost = fetch_card(
            index,
            quantity,

            card_set,
            card_collector_number,
            ignore_set_and_collector_number,

            name,

            prefer_older_sets,
            preferred_sets,

            prefer_showcase,
            prefer_extra_art,

            front_img_dir,
            double_sided_dir,
            
            fix_borders,
            show_cost,
            cheapest_version
        )
        
        if show_cost:
            total_cost[0] += cost
            card_count[0] += 1
    
    def print_total():
        if show_cost and card_count[0] > 0:
            print(f'\n{"="*50}')
            print(f'Total deck cost: ${total_cost[0]:.2f} USD')
            print(f'{"="*50}')
    
    configured_fetch_card.print_total = print_total
    return configured_fetch_card