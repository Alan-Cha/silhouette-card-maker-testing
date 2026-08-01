"""
MPCFill image fetching and caching.

The MPCFill API is a Google Apps Script that returns base64-encoded card images.
Each HTTP request has significant latency due to the Google Apps Script cold-start
overhead, so fetching images one at a time is very slow for large decks.

To speed this up, prefetch_mpcfill() uses a ThreadPoolExecutor to fetch multiple
images at the same time. A ThreadPoolExecutor creates a pool of worker threads
(up to MAX_WORKERS) that each make HTTP requests independently. This means
instead of waiting for one request to finish before starting the next, up to
MAX_WORKERS requests can be in flight simultaneously.

All fetched images are stored in _image_cache so that duplicate card IDs
(e.g. 4 copies of the same card across different slots) only require one
network request. When write_slot_image() is called for each slot, it pulls
from the cache via get_cached_image() instead of hitting the network again.
"""

import os
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set

import requests
from filetype.filetype import guess_extension

from .common import remove_nonalphanumeric

session = requests.Session()

# Cache for fetched images: card_id -> decoded image bytes.
# Populated by prefetch_mpcfill() and read by get_cached_image().
_image_cache: dict[str, bytes] = {}

# Maximum number of concurrent HTTP requests during prefetching.
# Each worker thread fetches one image at a time, so 8 workers means
# up to 8 simultaneous downloads.
MAX_WORKERS = 8


def request_mpcfill(card_id: str) -> bytes:
    """Fetch a single card image from MPCFill API and return decoded bytes."""
    base_url = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="
    r = session.get(base_url + card_id, headers={"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"})
    r.raise_for_status()
    return b64decode(r.content)


def fetch_single(card_id: str) -> tuple[str, bytes | None]:
    """Fetch a single card, returning None on failure instead of raising."""
    try:
        image_bytes = request_mpcfill(card_id)
        return (card_id, image_bytes)
    except Exception as e:
        print(f"Error fetching {card_id}: {e}")
        return (card_id, None)


def prefetch_mpcfill(card_ids: Set[str]) -> None:
    """
    Fetch all unique card images in parallel and store them in _image_cache.

    Uses ThreadPoolExecutor to run up to MAX_WORKERS downloads concurrently.
    executor.submit() schedules _fetch_single for each card ID, returning a
    Future object that will hold the result once the download completes.
    as_completed() then yields each Future as it finishes (not necessarily in
    submission order), allowing us to process results as soon as they're ready.
    """
    ids_to_fetch = [cid for cid in card_ids if cid not in _image_cache]

    if not ids_to_fetch:
        return

    print(f"Prefetching {len(ids_to_fetch)} images with {MAX_WORKERS} workers...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all fetch tasks to the thread pool. Each call returns a Future
        # representing the pending result. We map each Future back to its card_id.
        futures = {executor.submit(fetch_single, card_id): card_id for card_id in ids_to_fetch}

        completed = 0
        # as_completed() yields futures in the order they finish, so we can
        # cache results as soon as each download completes.
        for future in as_completed(futures):
            card_id, image_bytes = future.result()
            if image_bytes is not None:
                _image_cache[card_id] = image_bytes
            completed += 1
            if completed % 10 == 0 or completed == len(ids_to_fetch):
                print(f"  Fetched {completed}/{len(ids_to_fetch)} images")

    print("Prefetch complete.")


def get_cached_image(card_id: str) -> bytes | None:
    """Get an image from cache, fetching on-demand if not already cached."""
    if card_id not in _image_cache:
        _, image_bytes = fetch_single(card_id)
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
