"""
Tests for the Arkham Horror LCG plugin.
Tests deck format parsing and image fetching from ArkhamDB.
"""
import json
import os
import shutil
import tempfile

import pytest
from PIL import Image

from plugins.arkham_horror_lcg.deck_formats import DeckFormat, DECK_URL_PATTERN, handle_slots, parse_deck
from plugins.arkham_horror_lcg.api import fetch_arkhamdb_deck, fetch_card_json, get_handle_card


# --- Unit Tests ---

class TestDeckFormatEnum:
    """Test the DeckFormat enum values."""

    def test_arkhamdb_json_format_value(self):
        assert DeckFormat.ARKHAMDB_JSON.value == 'arkhamdb_json'

    def test_arkhamdb_url_format_value(self):
        assert DeckFormat.ARKHAMDB_URL.value == 'arkhamdb_url'


class TestDeckURLPattern:
    """Test ArkhamDB deck URL pattern matching."""

    def test_deck_url_matches(self):
        match = DECK_URL_PATTERN.match("https://arkhamdb.com/deck/view/12345")
        assert match is not None
        assert match.group(1) == "deck"
        assert match.group(2) == "12345"

    def test_decklist_url_matches(self):
        match = DECK_URL_PATTERN.match("https://arkhamdb.com/decklist/view/12345")
        assert match is not None
        assert match.group(1) == "decklist"
        assert match.group(2) == "12345"

    def test_rejects_invalid_urls(self):
        assert not DECK_URL_PATTERN.match("")
        assert not DECK_URL_PATTERN.match("12345")
        assert not DECK_URL_PATTERN.match("https://example.com/deck/view/12345")
        assert not DECK_URL_PATTERN.match("https://arkhamdb.com/card/01001")


class TestHandleSlots:
    """Test slot/investigator expansion into handle_card calls."""

    def test_investigator_and_slots_are_all_handled(self):
        data = {
            "investigator_code": "01001",
            "slots": {"01006": 1, "01007": 2},
        }

        seen = []
        handle_slots(data, lambda index, code, quantity: seen.append((code, quantity)))

        codes = {code: quantity for code, quantity in seen}
        assert codes["01001"] == 1
        assert codes["01006"] == 1
        assert codes["01007"] == 2
        assert len(seen) == 3

    def test_investigator_already_in_slots_is_added_not_overwritten(self):
        # Defensive case: if a code coincides with the investigator, quantities stack
        # rather than clobbering each other.
        data = {
            "investigator_code": "01001",
            "slots": {"01001": 1},
        }

        seen = []
        handle_slots(data, lambda index, code, quantity: seen.append((code, quantity)))

        assert seen == [("01001", 2)]

    def test_missing_investigator_code_is_skipped(self):
        data = {"slots": {"01006": 1}}

        seen = []
        handle_slots(data, lambda index, code, quantity: seen.append((code, quantity)))

        assert seen == [("01006", 1)]

    def test_errors_from_handle_card_are_collected_not_raised(self):
        data = {"slots": {"01006": 1, "01007": 1}}

        def failing_handle_card(index, code, quantity):
            if code == "01006":
                raise ValueError("boom")

        # Should not raise, even though one card fails.
        handle_slots(data, failing_handle_card)


class TestParseArkhamdbJson:
    """Test the arkhamdb_json format end-to-end (no network)."""

    def test_parse_deck_dispatches_to_json_parser(self):
        deck_text = json.dumps({
            "investigator_code": "01001",
            "slots": {"01006": 1},
        })

        seen = []
        parse_deck(deck_text, DeckFormat.ARKHAMDB_JSON, lambda index, code, quantity: seen.append(code))

        assert "01001" in seen
        assert "01006" in seen

    def test_unrecognized_format_raises(self):
        with pytest.raises(ValueError):
            parse_deck("{}", "not_a_real_format", lambda *args: None)


# --- Integration Tests ---

@pytest.mark.integration
class TestArkhamDBAPI:
    """Test ArkhamDB public API requests."""

    def test_card_json_availability(self):
        card = fetch_card_json("01001")
        assert card.get("code") == "01001"
        assert card.get("imagesrc")

    def test_double_sided_investigator_has_back_image(self):
        card = fetch_card_json("01001")
        assert card.get("double_sided") is True
        assert card.get("backimagesrc")

    def test_linked_card_back_is_embedded(self):
        # 01121a is an encounter card whose back is a separate linked card
        # entry rather than its own backimagesrc.
        card = fetch_card_json("01121a")
        assert not card.get("backimagesrc")
        assert card.get("linked_card", {}).get("imagesrc")

    def test_private_deck_url_is_not_reachable(self):
        # Most /deck/view/<id> IDs belong to decks whose owner has not enabled
        # public sharing. ArkhamDB responds to those with a redirect to its
        # login page rather than an HTTP error, so the JSON parse itself is
        # what fails. This documents that failure mode, which is why
        # test_fetch_deck_from_arkhamdb_personal_deck_url below pins a
        # specific ID that is actually reachable rather than an arbitrary one.
        with pytest.raises(json.JSONDecodeError):
            fetch_arkhamdb_deck("1", is_decklist=False)


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        yield front_dir, double_sided_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(double_sided_dir)

    def test_fetch_deck_from_arkhamdb_json(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs

        deck_text = json.dumps({
            "investigator_code": "01001",
            "slots": {"01006": 1, "01016": 2},
        })

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_text, DeckFormat.ARKHAMDB_JSON, handle_card)

        front_files = os.listdir(front_dir)
        # investigator (1) + 01006 (1) + 01016 (2 copies) = 4 front images
        assert len(front_files) == 4

        for f in front_files:
            assert os.path.getsize(os.path.join(front_dir, f)) > 0

        # The investigator is double-sided, so its back should be present.
        double_sided_files = os.listdir(double_sided_dir)
        assert len(double_sided_files) >= 1

    def test_fetch_deck_from_arkhamdb_decklist_url(self, temp_dirs):
        """Published decklist URL (/decklist/view/<id>), always public."""
        front_dir, double_sided_dir = temp_dirs

        deck_url = "https://arkhamdb.com/decklist/view/1"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_url, DeckFormat.ARKHAMDB_URL, handle_card)

        front_files = os.listdir(front_dir)
        assert len(front_files) >= 1

        for f in front_files:
            assert os.path.getsize(os.path.join(front_dir, f)) > 0

    def test_fetch_deck_from_arkhamdb_personal_deck_url(self, temp_dirs):
        """Personal deck URL (/deck/view/<id>) with public sharing enabled by its
        owner. Unlike published decklists, most /deck/view/ IDs are private and
        redirect to a login page rather than returning deck data (see
        TestArkhamDBAPI.test_private_deck_url_is_not_reachable) -- this is one of
        the few that is reachable, found via a public web search rather than
        pinned arbitrarily."""
        front_dir, double_sided_dir = temp_dirs

        deck_url = "https://arkhamdb.com/deck/view/1405"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_url, DeckFormat.ARKHAMDB_URL, handle_card)

        front_files = os.listdir(front_dir)
        assert len(front_files) >= 1

        for f in front_files:
            assert os.path.getsize(os.path.join(front_dir, f)) > 0

        # This particular deck's investigator (Skids) is double-sided.
        double_sided_files = os.listdir(double_sided_dir)
        assert len(double_sided_files) >= 1

    def test_landscape_card_is_rotated_to_portrait(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs

        # 01105 is a landscape-printed agenda card.
        handle_card = get_handle_card(front_dir, double_sided_dir)
        handle_card(1, "01105", 1)

        front_files = os.listdir(front_dir)
        assert len(front_files) == 1

        with Image.open(os.path.join(front_dir, front_files[0])) as img:
            assert img.height > img.width

        double_sided_files = os.listdir(double_sided_dir)
        assert len(double_sided_files) == 1

        with Image.open(os.path.join(double_sided_dir, double_sided_files[0])) as img:
            assert img.height > img.width
