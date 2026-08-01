from enum import Enum
from re import sub
from time import sleep

from requests import Response, Session

from plugins.lotr_lcg.card_entry import CardEntry

session = Session()

HALL_BASE_URL = "https://hallofbeorn.com"

# Hall of Beorn has no published API. These /Export routes were found in
# its open-source backend (github.com/danpoage/hall-of-beorn,
# ExportController.cs + RouteConfig.cs) and confirmed working live. Being
# unpublished, they could change without notice.
#
#   GET /Export/Scenarios            -> [{Title, Slug, Product, Number}, ...]
#     Every scenario; only useful for finding a Slug by Title.
#
#   GET /Export/Scenarios/{slug}     -> {Title, Slug, QuestCards, ScenarioCards}
#     `slug` must exactly match one from the list above (case-sensitive --
#     RingsDB's lowercase nameCanonical often doesn't match). An unknown
#     slug returns HTTP 200 with a bare JSON string, not a 404.
#     QuestCards carry their own Front/Back image URLs. ScenarioCards (the
#     encounter deck) only carry a Slug + per-mode quantities; resolve an
#     image via the bulk card index below.
#
#   GET /Export/Cards/{set_type}     -> [{code, name, url, imagesrc}, ...]
#     Bulk card export ("OFFICIAL" = all official releases). `url`'s last
#     path segment is the same Slug used by ScenarioCards.
EXPORT_SCENARIOS_LIST_URL = f"{HALL_BASE_URL}/Export/Scenarios"
EXPORT_SCENARIO_URL_TEMPLATE = f"{HALL_BASE_URL}/Export/Scenarios/{{slug}}"
EXPORT_CARDS_URL_TEMPLATE = f"{HALL_BASE_URL}/Export/Cards/{{set_type}}"
OFFICIAL_SET_TYPE = "OFFICIAL"


class ScenarioMode(str, Enum):
    NORMAL = "normal"
    EASY = "easy"
    NIGHTMARE = "nightmare"


def request_hall(query: str) -> Response:
    response = session.get(
        query,
        headers={"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"},
        timeout=30,
    )
    response.raise_for_status()
    sleep(0.05)
    return response


def normalize_scenario_mode(value: str | ScenarioMode) -> ScenarioMode:
    if isinstance(value, ScenarioMode):
        return value

    mode_str = value.lower()
    try:
        return ScenarioMode(mode_str)
    except ValueError:
        valid_modes = ", ".join([mode.value for mode in ScenarioMode])
        raise ValueError(f"Unsupported scenario mode: {value}. Valid modes: {valid_modes}")


def fetch_all_scenarios() -> list[dict]:
    """Fetch the full scenario list. Only Title/Slug/Product/Number are
    populated here -- see find_scenario_slug for what this is used for."""
    return request_hall(EXPORT_SCENARIOS_LIST_URL).json()


def find_scenario_slug(title: str, scenarios: list[dict]) -> str | None:
    """Look up a scenario's exact slug by title (case-insensitive, exact
    match against `scenarios`). None if no scenario has that title."""
    normalized = title.strip().lower()
    for scenario in scenarios:
        if scenario.get("Title", "").strip().lower() == normalized:
            return scenario.get("Slug")
    return None


def normalize_slug(value: str) -> str:
    return sub(r"[^a-z0-9]", "", value.lower())


def find_scenario_slug_fuzzy(slug: str, scenarios: list[dict]) -> str | None:
    """Find a scenario whose Slug matches once punctuation/casing is
    ignored -- Hall of Beorn's HTML page accepts slightly looser slugs
    than /Export/Scenarios/{slug} does (e.g. "...-Campaign" for the real
    "...-(Campaign)"), so a slug from a pasted page URL may not match exactly."""
    normalized_target = normalize_slug(slug)
    for scenario in scenarios:
        candidate = scenario.get("Slug", "")
        if normalize_slug(candidate) == normalized_target:
            return candidate
    return None


def fetch_scenario_by_slug(slug: str, scenarios: list[dict]) -> dict:
    data = request_hall(EXPORT_SCENARIO_URL_TEMPLATE.format(slug=slug)).json()
    if isinstance(data, dict):
        return data

    # Unrecognized slugs return HTTP 200 with a bare JSON string message
    # ("Scenario {slug} not found") instead of a 404 or an object. Before
    # giving up, retry with a fuzzy-matched slug (see find_scenario_slug_fuzzy).
    fuzzy_slug = find_scenario_slug_fuzzy(slug, scenarios)
    if fuzzy_slug is not None and fuzzy_slug != slug:
        data = request_hall(EXPORT_SCENARIO_URL_TEMPLATE.format(slug=fuzzy_slug)).json()
        if isinstance(data, dict):
            return data

    raise ValueError(str(data))


def load_card_image_index() -> dict[str, str]:
    """Bulk-fetch every official card once and index it by the slug in its
    detail-page URL, so ScenarioCards entries (which only carry that slug,
    not an image) can be resolved without one request per card."""
    cards = request_hall(EXPORT_CARDS_URL_TEMPLATE.format(set_type=OFFICIAL_SET_TYPE)).json()

    index = {}
    for card in cards:
        url = card.get("url")
        image_url = card.get("imagesrc")
        if not url or not image_url:
            continue
        index[url.rsplit("/", 1)[-1]] = image_url

    return index


def build_quest_entries(quest_cards: list[dict]) -> list[CardEntry]:
    entries = []

    for card in quest_cards:
        front = card.get("Front") or {}
        back = card.get("Back")
        entries.append(
            CardEntry(
                card_code=card.get("Slug") or card.get("Title", ""),
                name=card.get("Title", ""),
                image_url=front.get("ImagePath"),
                quantity=card.get("Quantity") or 1,
                back_image_url=back.get("ImagePath") if back else None,
            )
        )

    return entries


def build_encounter_entries(
    scenario_cards: list[dict],
    scenario_mode: ScenarioMode,
    card_image_index: dict[str, str],
) -> list[CardEntry]:
    quantity_field = {
        ScenarioMode.NORMAL: "NormalQuantity",
        ScenarioMode.EASY: "EasyQuantity",
        ScenarioMode.NIGHTMARE: "NightmareQuantity",
    }[scenario_mode]

    entries = []

    for card in scenario_cards:
        quantity = card.get(quantity_field) or 0
        if quantity <= 0:
            continue

        slug = card.get("Slug", "")
        entries.append(
            CardEntry(
                card_code=slug,
                name=card.get("Title", ""),
                image_url=card_image_index.get(slug),
                quantity=quantity,
            )
        )

    return entries


def fetch_scenario_entries(
    scenario_slug: str,
    scenario_mode: str | ScenarioMode,
    scenarios: list[dict],
    card_image_index: dict[str, str],
) -> list[CardEntry]:
    """
    Fetch every card (quest deck + encounter deck) for a scenario. Quest
    cards carry their own image URLs; encounter cards resolve against
    `card_image_index`. `scenarios`/`card_image_index` are passed in (not
    fetched here) so a caller processing several scenarios in one run can
    fetch each bulk payload once and reuse it.
    """
    mode = normalize_scenario_mode(scenario_mode)
    scenario = fetch_scenario_by_slug(scenario_slug, scenarios)

    entries = build_quest_entries(scenario.get("QuestCards") or [])

    scenario_cards = scenario.get("ScenarioCards") or []
    if scenario_cards:
        entries.extend(build_encounter_entries(scenario_cards, mode, card_image_index))

    return entries
