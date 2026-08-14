from difflib import SequenceMatcher
from functools import partial
from os import path
from re import IGNORECASE, compile, sub
from time import sleep
from typing import Optional, Tuple
from unicodedata import combining
from unicodedata import normalize as normalize_unicode
from urllib.parse import unquote

from requests import Response, Session

session = Session()

USER_AGENT = 'silhouette-card-maker/0.1'
API_URL = 'https://www.archonarcana.com/w139/api.php'

RATE_LIMIT_SECONDS = 0.075

# Minimum similarity for the last-resort fuzzy match to accept a search result.
FUZZY_MATCH_THRESHOLD = 0.8

URL_PATTERN = compile(r'^https?://', IGNORECASE)
# Stop at '?' or '#' so a pasted URL's query string or fragment isn't swept into the title.
WIKI_PATH_PATTERN = compile(r'/wiki/([^?#]+)')

# Archon Arcana page titles use typographic characters. Map common ASCII input to them,
# e.g. AEmber Imp -> Æmber Imp, Nature's Call -> Nature’s Call, Shae "Cloudkicker" -> Shae “Cloudkicker”.
LIGATURE_PATTERN = compile(r'AE(?=[a-z])')
DOUBLE_QUOTE_PATTERN = compile(r'"([^"]*)"')
ASCII_APOSTROPHE_TRANSLATION = str.maketrans({"'": '\u2019'})
# Fold those typographic characters back to ASCII so different spellings compare equal.
TYPOGRAPHIC_TRANSLATION = str.maketrans({'\u2019': "'", '\u201c': '"', '\u201d': '"'})

def request_archonarcana(url: str, params: Optional[dict] = None) -> Response:
    r = session.get(url, params=params, headers={'user-agent': USER_AGENT, 'accept': '*/*'})

    sleep(RATE_LIMIT_SECONDS)

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

def query_page_image(title: str) -> Optional[Tuple[str, Optional[str]]]:
    # Look up a page by title through the MediaWiki API, following redirects. Returns
    # None if the page does not exist, otherwise (canonical title, original image URL
    # or None if the page has no image). This avoids fetching and scraping the rendered
    # wiki page, which the API returns as structured data directly.
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'pageimages',
        'piprop': 'original',
        'redirects': '1',
        'format': 'json',
    }

    pages = request_archonarcana(API_URL, params=params).json().get('query', {}).get('pages', {})
    page = next(iter(pages.values()), None)

    if page is None or 'missing' in page:
        return None

    return page.get('title', title), page.get('original', {}).get('source')

def resolve_card(entry: str) -> Tuple[str, str]:
    title = translate_special_characters(entry_to_title(entry))
    result = query_page_image(title)

    if result is None:
        # Exact title not found. Retry via search to handle casing and space/underscore differences.
        resolved = search_title(title)
        if resolved is not None and resolved != title:
            result = query_page_image(resolved)
        if resolved is not None:
            title = resolved

    if result is None:
        raise Exception(f'card not found on Archon Arcana: "{title}"')

    title, image_url = result
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
