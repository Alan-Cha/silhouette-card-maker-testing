import os
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set

import requests
from filetype.filetype import guess_extension

from common import remove_nonalphanumeric

# Cache for fetched images: card_id -> decoded image bytes
_image_cache: dict[str, bytes] = {}

# Number of parallel workers for fetching
MAX_WORKERS = 8


def request_mpcfill(card_id: str) -> bytes:
    """Fetch a single card image from MPCFill API and return decoded bytes."""
    base_url = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="
    r = requests.get(base_url + card_id, headers={"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"})
    r.raise_for_status()
    return b64decode(r.content)


def _fetch_single(card_id: str) -> tuple[str, bytes | None]:
    """Fetch a single card and return (card_id, image_bytes)."""
    try:
        image_bytes = request_mpcfill(card_id)
        return (card_id, image_bytes)
    except Exception as e:
        print(f"Error fetching {card_id}: {e}")
        return (card_id, None)


def prefetch_images(card_ids: Set[str]) -> None:
    """Prefetch all unique card images in parallel and cache them."""
    # Filter out already cached IDs
    ids_to_fetch = [cid for cid in card_ids if cid not in _image_cache]

    if not ids_to_fetch:
        return

    print(f"Prefetching {len(ids_to_fetch)} images with {MAX_WORKERS} workers...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_single, card_id): card_id for card_id in ids_to_fetch}

        completed = 0
        for future in as_completed(futures):
            card_id, image_bytes = future.result()
            if image_bytes is not None:
                _image_cache[card_id] = image_bytes
            completed += 1
            if completed % 10 == 0 or completed == len(ids_to_fetch):
                print(f"  Fetched {completed}/{len(ids_to_fetch)} images")

    print("Prefetch complete.")


def get_cached_image(card_id: str) -> bytes | None:
    """Get an image from cache, fetching if not present."""
    if card_id not in _image_cache:
        _, image_bytes = _fetch_single(card_id)
        if image_bytes:
            _image_cache[card_id] = image_bytes
    return _image_cache.get(card_id)


def write_slot_image(
    slot: int,
    card_id: str,
    name: str,
    output_dir: str,
) -> None:
    """Write a single image file for a slot."""
    card_art = get_cached_image(card_id)
    if card_art is None:
        print(f"  Warning: No image data for slot {slot} ({name})")
        return

    clean_name = remove_nonalphanumeric(name)
    card_art_ext = guess_extension(card_art)
    image_path = os.path.join(output_dir, f'{slot}{clean_name}.{card_art_ext}')

    with open(image_path, 'wb') as f:
        f.write(card_art)


def get_handle_card(
    front_img_dir: str,
    double_sided_dir: str
):
    """
    Return a handler function for MPCFill cards.

    Handler signature: (slot, front_id, front_name, back_id, back_name)
    Creates one front image per slot, and one back image per slot (if back exists).
    Back images use the front name so create_pdf.py can match them.
    """
    def handle_slot(slot: int, front_id: str, front_name: str, back_id: str | None, back_name: str | None):
        # Write front image
        write_slot_image(slot, front_id, front_name, front_img_dir)

        # Write back image if present - use FRONT name for matching
        if back_id:
            write_slot_image(slot, back_id, front_name, double_sided_dir)

    return handle_slot
