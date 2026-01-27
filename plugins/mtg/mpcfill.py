import os
import time
import requests
from base64 import b64decode
from filetype.filetype import guess_extension

from common import remove_nonalphanumeric


def request_mpcfill(card_id: str, retries: int = 3, delay: int = 1) -> requests.Response:
    """
    Fetch card image data from MPCFill via the official Google Apps Script endpoint.
    Includes retry protection for connection resets.
    """
    base_url = (
        "https://script.google.com/macros/s/"
        "AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4"
        "/exec?id="
    )

    for attempt in range(retries):
        try:
            r = requests.get(
                base_url + card_id,
                headers={
                    "user-agent": "silhouette-card-maker/0.1",
                    "accept": "*/*",
                },
                timeout=15,
            )
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                raise
            print(f"Retrying card {card_id} ({attempt + 1}/{retries})...")
            time.sleep(delay)


def fetch_card(index, card_id, name, back, quantity, front_dir, double_sided_dir):
    """
    Download card images with full resume support.
    Skips already-downloaded files regardless of extension.
    """

    safe_name = remove_nonalphanumeric(name)

    for i in range(quantity):
        #base_path = os.path.join(front_dir, f"{index}_{i}")

        safe_name = remove_nonalphanumeric(name)
        base_path = os.path.join(front_dir, f"{index}{safe_name}{i + 1}")

        #  Resume logic: skip if file already exists in any known format
        for ext in ("png", "jpg", "jpeg", "webp"):
            existing = f"{base_path}.{ext}"
            if os.path.exists(existing):
                print(f"Skipping existing file: {existing}")
                break
        else:
            # No existing file found → download
            try:
                response = request_mpcfill(card_id)
            except Exception as e:
                print(f"Failed to fetch card {index} ({name}): {e}")
                return

            content = response.content

            #  Decode base64 if applicable
            try:
                decoded = b64decode(content, validate=True)
                content = decoded
            except Exception:
                pass  # Not base64, continue with raw bytes

            #  Detect file extension from binary content
            ext = guess_extension(content) or "png"
            front_path = f"{base_path}.{ext}"

            with open(front_path, "wb") as f:
                f.write(content)


def configured_fetch_card(front_dir, double_sided_dir):
    """
    Wrapper used by the deck parser.
    """
    def _fetch(index, card_id, name, back, quantity):
        fetch_card(
            index,
            card_id,
            name,
            back,
            quantity,
            front_dir,
            double_sided_dir,
        )
    return _fetch


def get_handle_card(front_dir, double_sided_dir):
    """
    Backward-compatible entry point expected by fetch.py
    """
    return configured_fetch_card(front_dir, double_sided_dir)
