from difflib import SequenceMatcher
from functools import partial
from html import unescape
from os import path
from re import IGNORECASE, compile, sub
from time import sleep
from typing import Optional, Tuple
from unicodedata import combining
from unicodedata import normalize as normalize_unicode
from urllib.parse import quote, unquote

from requests import Response, Session

session = Session()

USER_AGENT = 'silhouette-card-maker/0.1'
WIKI_PAGE_TEMPLATE = 'https://www.archonarcana.com/wiki/{title}'
API_URL = 'https://www.archonarcana.com/w139/api.php'

RATE_LIMIT_SECONDS = 0.075

# Minimum similarity for the last-resort fuzzy match to accept a search result.
FUZZY_MATCH_THRESHOLD = 0.8

# The card art is the single MediaWiki "image" anchor on a card page.
IMAGE_ANCHOR_PATTERN = compile(r'<a[^>]*class="image"[^>]*>\s*<img[^>]*\bsrc="([^"]+)"', IGNORECASE)
# MediaWiki thumbnails look like `.../thumb/<file>/<width>px-<file>`; the original drops the thumb segment.
THUMB_PATTERN = compile(r'/thumb/(.+)/[^/]+$')
URL_PATTERN = compile(r'^https?://', IGNORECASE)
WIKI_PATH_PATTERN = compile(r'/wiki/(.+)$')

# Archon Arcana page titles use typographic characters. Map common ASCII input to them,
# e.g. AEmber Imp -> Æmber Imp, Nature's Call -> Nature’s Call, Shae "Cloudkicker" -> Shae “Cloudkicker”.
LIGATURE_PATTERN = compile(r'AE(?=[a-z])')
DOUBLE_QUOTE_PATTERN = compile(r'"([^"]*)"')
ASCII_APOSTROPHE_TRANSLATION = str.maketrans({"'": '\u2019'})
# Fold those typographic characters back to ASCII so different spellings compare equal.
TYPOGRAPHIC_TRANSLATION = str.maketrans({'\u2019': "'", '\u201c': '"', '\u201d': '"'})

def request_archonarcana(url: str, params: Optional[dict] = None, allow_missing: bool = False) -> Optional[Response]:
    r = session.get(url, params=params, headers={'user-agent': USER_AGENT, 'accept': '*/*'})

    sleep(RATE_LIMIT_SECONDS)

    # A missing wiki page responds with 404. Let callers treat that as "does not exist".
    if allow_missing and r.status_code == 404:
        return None

    # Check for 2XX response code
    r.raise_for_status()

    return r

def remove_nonalphanumeric(s: str) -> str:
    return sub(r'[^\w]', '', s)

def normalize_title(title: str) -> str:
    # MediaWiki treats spaces and underscores as equivalent and is case-insensitive on the first letter.
    normalized = sub(r'[\s_]+', ' ', title).strip().lower()
    # Strip accents (Gĕzdrutyŏ -> gezdrutyo) and fold typographic variants so spellings compare equal.
    normalized = ''.join(c for c in normalize_unicode('NFKD', normalized) if not combining(c))
    return normalized.translate(TYPOGRAPHIC_TRANSLATION).replace('\u00e6', 'ae')

def translate_special_characters(title: str) -> str:
    # Convert ASCII input into the typographic characters used in Archon Arcana page titles.
    title = LIGATURE_PATTERN.sub('\u00c6', title)              # AEmber -> Æmber (lowercase "ae" is left alone)
    title = DOUBLE_QUOTE_PATTERN.sub('\u201c\\1\u201d', title) # "Cloudkicker" -> “Cloudkicker”
    return title.translate(ASCII_APOSTROPHE_TRANSLATION)       # Nature's -> Nature’s

def entry_to_title(entry: str) -> str:
    entry = entry.strip()

    if URL_PATTERN.match(entry):
        match = WIKI_PATH_PATTERN.search(entry)
        title = match.group(1) if match else entry.rsplit('/', 1)[-1]
        return unquote(title).replace('_', ' ').strip()

    return entry

def title_to_url(title: str) -> str:
    return WIKI_PAGE_TEMPLATE.format(title=quote(title.replace(' ', '_'), safe="():,'!*-"))

def search_title(query: str) -> Optional[str]:
    params = {
        'action': 'opensearch',
        'search': query,
        'limit': '10',
        'namespace': '0',
        'format': 'json',
    }

    results = request_archonarcana(API_URL, params=params).json()
    titles = results[1] if len(results) > 1 else []
    if not titles:
        return None

    normalized_query = normalize_title(query)

    # Prefer an exact match (ignoring case, spaces/underscores, accents, and typographic characters).
    for title in titles:
        if normalize_title(title) == normalized_query:
            return title

    # Last resort: accept the first result if it is a close match.
    first_title = titles[0]
    if SequenceMatcher(None, normalized_query, normalize_title(first_title)).ratio() >= FUZZY_MATCH_THRESHOLD:
        return first_title

    return None

def extract_image_url(html: str) -> Optional[str]:
    match = IMAGE_ANCHOR_PATTERN.search(html)
    if not match:
        return None

    src = unescape(match.group(1))

    # Derive the full-resolution original from the thumbnail URL.
    return THUMB_PATTERN.sub(r'/\1', src)

def resolve_card(entry: str) -> Tuple[str, str]:
    title = translate_special_characters(entry_to_title(entry))
    response = request_archonarcana(title_to_url(title), allow_missing=True)

    if response is None:
        # Exact title not found. Retry via search to handle casing and space/underscore differences.
        resolved = search_title(title)
        if resolved is not None:
            title = resolved
            response = request_archonarcana(title_to_url(title), allow_missing=True)

    if response is None:
        raise Exception(f'card not found on Archon Arcana: "{title}"')

    image_url = extract_image_url(response.text)
    if image_url is None:
        raise Exception(f'card image not found on Archon Arcana: "{title}"')

    return title, image_url

def fetch_card_art(index: int, card_name: str, quantity: int, front_img_dir: str):
    title, image_url = resolve_card(card_name)

    card_art = request_archonarcana(image_url).content
    clean_name = remove_nonalphanumeric(title)

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{index}{clean_name}{counter + 1}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(front_img_dir: str):
    return partial(fetch_card_art, front_img_dir=front_img_dir)
