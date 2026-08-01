from enum import Enum
from html import unescape
from re import S, compile, search
from time import sleep
from urllib.parse import urljoin

from requests import Response, get

from plugins.lotr_lcg.card_entry import CardEntry

HALL_BASE_URL = "https://hallofbeorn.com"
HALL_SCENARIO_URL_TEMPLATE = f"{HALL_BASE_URL}/LotR/Scenarios/{{scenario_slug}}"
DETAIL_HREF_PATTERN = compile(
    r'<a[^>]+title="(?P<title>[^"]+)"[^>]+href="(?P<href>/LotR/Details/[^"]+)"[^>]*>'
    r"<span[^>]*>.*?</span></a>\s*"
    r'<span[^>]*>(?P<normal>[^<]+)</span>\s*'
    r'<span[^>]*>(?P<easy>[^<]+)</span>\s*'
    r'<span[^>]*>(?P<nightmare>[^<]+)</span>',
    flags=S,
)
CARD_IMAGE_TAG_PATTERN = compile(r'<img[^>]*class="card-image[^"]*"[^>]*>', flags=S)


class ScenarioMode(str, Enum):
    NORMAL = "normal"
    EASY = "easy"
    NIGHTMARE = "nightmare"


def request_hall(query: str) -> Response:
    response = get(
        query,
        headers={"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"},
        timeout=30,
    )
    response.raise_for_status()
    sleep(0.05)
    return response


def parse_quantity(value: str) -> int:
    cleaned = unescape(value).strip()
    if cleaned in {"-", ""}:
        return 0
    return int(cleaned)


def normalize_scenario_mode(value: str | ScenarioMode) -> ScenarioMode:
    if isinstance(value, ScenarioMode):
        return value

    mode_str = value.lower()
    try:
        return ScenarioMode(mode_str)
    except ValueError:
        valid_modes = ", ".join([mode.value for mode in ScenarioMode])
        raise ValueError(f"Unsupported scenario mode: {value}. Valid modes: {valid_modes}")


def scenario_card_code(detail_href: str) -> str:
    return detail_href.rsplit("/", 1)[-1]


def fetch_card_image_urls(detail_href: str) -> list[str]:
    detail_html = request_hall(urljoin(HALL_BASE_URL, detail_href)).text
    image_urls = []
    for image_tag in CARD_IMAGE_TAG_PATTERN.findall(detail_html):
        url_match = search(r'(?:data-src|src)="([^"]+)"', image_tag)
        if url_match:
            image_urls.append(urljoin(HALL_BASE_URL, unescape(url_match.group(1))))
    return image_urls


def fetch_scenario_entries(
    scenario_slug: str,
    scenario_mode: str | ScenarioMode = ScenarioMode.NORMAL,
) -> list[CardEntry]:
    """
    Fetch scenario card entries by scraping Hall of Beorn HTML.

    Hall of Beorn is the only source for detailed scenario card lists with
    individual card quantities per difficulty mode (easy/normal/nightmare).
    Parses HTML to extract card names, quantities, and fetches individual
    card detail pages for image URLs.
    """
    mode = normalize_scenario_mode(scenario_mode)
    scenario_html = request_hall(
        HALL_SCENARIO_URL_TEMPLATE.format(scenario_slug=scenario_slug)
    ).text

    image_cache: dict[str, list[str]] = {}
    entries = []

    for match in DETAIL_HREF_PATTERN.finditer(scenario_html):
        quantity = parse_quantity(match.group(mode.value))
        if quantity <= 0:
            continue

        detail_href = unescape(match.group("href"))
        title = unescape(match.group("title")).strip()
        image_urls = image_cache.get(detail_href)
        if image_urls is None:
            image_urls = fetch_card_image_urls(detail_href)
            image_cache[detail_href] = image_urls

        if not image_urls:
            raise ValueError(f"Could not find images for Hall of Beorn detail page {detail_href}")

        entries.append(
            CardEntry(
                card_code=scenario_card_code(detail_href),
                name=title,
                image_url=image_urls[0],
                quantity=quantity,
                back_image_url=image_urls[1] if len(image_urls) > 1 else None,
            )
        )

    return entries
