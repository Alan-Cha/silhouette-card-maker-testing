from enum import Enum
from re import sub
from time import sleep

from requests import Response, Session

from plugins.lotr_lcg.card_entry import CardEntry

session = Session()

HALL_BASE_URL = "https://hallofbeorn.com"

# Hall of Beorn does not publish or document a public API. Everything below
# was reverse engineered from the site's own (open source) backend at
# https://github.com/danpoage/hall-of-beorn -- specifically
# src/HallOfBeorn/Controllers/ExportController.cs (the handlers) and
# src/HallOfBeorn/App_Start/RouteConfig.cs (the "Export/{action}/{id}" route
# that dispatches "/Export/<action>/<id>" requests to that controller). All
# three endpoints below were confirmed working live against production as of
# 2026-08-01. Since none of this is a published, versioned contract, Hall of
# Beorn is free to change or remove it without notice -- if these break,
# check ExportController.cs on GitHub for what changed before assuming the
# site itself is down.
#
#   GET /Export/Scenarios
#     -> [{Title, Slug, Product, Number, QuestCards: [], ScenarioCards: []}, ...]
#     Every scenario Hall of Beorn knows about. QuestCards/ScenarioCards are
#     always empty arrays here regardless of the scenario -- this endpoint
#     is only useful for finding a scenario's exact Slug by Title (see
#     find_scenario_slug), not for its card list.
#
#   GET /Export/Scenarios/{slug}
#     -> {Title, Slug, Product, Number, QuestCards: [...], ScenarioCards: [...]}
#     `slug` must match one returned by the list endpoint above exactly,
#     including case -- e.g. "Passage-Through-Mirkwood", not RingsDB's
#     lowercase nameCanonical "passage-through-mirkwood" (these can differ;
#     RingsDB and Hall of Beorn are independently-run sites that don't
#     coordinate on slugs). An unrecognized slug returns HTTP 200 with a
#     bare JSON string "Scenario {slug} not found", not a 404 or an object,
#     so callers must check the response shape rather than the status code.
#     - QuestCards: fully detailed quest/story cards. Each has Front/Back
#       objects that already carry a direct image URL (Front.ImagePath /
#       Back.ImagePath) -- no follow-up request needed per card.
#     - ScenarioCards: the scenario's encounter deck, as {EncounterSet,
#       Title, Slug, NormalQuantity, EasyQuantity, NightmareQuantity}. No
#       image URL is included here; resolve one by looking this same Slug
#       up in the bulk card index below.
#
#   GET /Export/Cards/{set_type}
#     -> [{code, name, ..., url, imagesrc}, ...] (RingsDB-shaped card records)
#     Bulk export of every card in `set_type` ("OFFICIAL" for all official
#     releases, no fan-made content). `url` is the card's detail page
#     (".../LotR/Details/{slug}"); its trailing path segment is the same
#     Slug used by ScenarioCards above, and `imagesrc` is the card's image.
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
    """Look up a scenario's exact Hall of Beorn slug by title (case-insensitive,
    exact match). `scenarios` is the full list from fetch_all_scenarios() --
    passed in rather than fetched here so callers processing multiple
    scenarios in one run can fetch it once and reuse it. Returns None if no
    scenario has that title."""
    normalized = title.strip().lower()
    for scenario in scenarios:
        if scenario.get("Title", "").strip().lower() == normalized:
            return scenario.get("Slug")
    return None


def normalize_slug(value: str) -> str:
    return sub(r"[^a-z0-9]", "", value.lower())


def find_scenario_slug_fuzzy(slug: str, scenarios: list[dict]) -> str | None:
    """Find a scenario whose real Slug matches once punctuation/casing
    differences are ignored. Hall of Beorn's own /LotR/Scenarios/{slug} HTML
    page is more lenient about this than /Export/Scenarios/{slug} -- e.g. it
    accepts "Passage-Through-Mirkwood-Campaign" for the real slug
    "Passage-Through-Mirkwood-(Campaign)" -- so a slug pulled from a pasted
    page URL can differ slightly from the exact one the Export API expects."""
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
    Fetch every card (quest deck + encounter deck) for a scenario via Hall of
    Beorn's undocumented /Export JSON API (see the module-level comment
    above for how these endpoints were found and what they return). Quest
    cards come back fully detailed with image URLs already included;
    encounter deck cards are resolved against a bulk card index keyed by
    their detail-page slug. If a card's image can't be resolved, its
    CardEntry.image_url is left None -- fetch_card in ringsdb.py raises
    clearly for that case, which the caller's per-card error handling
    collects instead of the card silently vanishing.

    `scenarios` (fetch_all_scenarios()) and `card_image_index`
    (load_card_image_index()) are both bulk, scenario-independent fetches --
    passed in rather than fetched here so a caller processing several
    scenarios in one run (e.g. a whole campaign) fetches each once and
    reuses it, instead of re-fetching Hall of Beorn's full scenario list and
    full official card index (a multi-MB payload) once per scenario.
    """
    mode = normalize_scenario_mode(scenario_mode)
    scenario = fetch_scenario_by_slug(scenario_slug, scenarios)

    entries = build_quest_entries(scenario.get("QuestCards") or [])

    scenario_cards = scenario.get("ScenarioCards") or []
    if scenario_cards:
        entries.extend(build_encounter_entries(scenario_cards, mode, card_image_index))

    return entries
