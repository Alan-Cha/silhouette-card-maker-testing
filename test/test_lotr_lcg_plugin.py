"""
Tests for the Lord of the Rings LCG plugin.
Tests RingsDB references, fellowship/scenario parsing, and public API access.
"""
from io import BytesIO
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from plugins.lotr_lcg.deck_formats import (
    DeckFormat,
    extract_decklist_id,
    extract_fellowship_id,
    extract_scenario_reference,
    parse_deck,
)
from plugins.lotr_lcg.ringsdb import (
    RINGSDB_ALL_CARDS_URL,
    get_handle_card,
    install_default_back,
    request_ringsdb,
)


class TestDeckFormatEnum:
    def test_enum_values(self):
        assert DeckFormat.RINGSDB.value == "ringsdb"
        assert DeckFormat.RINGSDB_FELLOWSHIP.value == "ringsdb_fellowship"
        assert DeckFormat.RINGSDB_SCENARIO.value == "ringsdb_scenario"


class TestDeckReferenceParsing:
    def test_extracts_decklist_id_from_share_url(self):
        deck_id = extract_decklist_id(
            "https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0"
        )
        assert deck_id == "337"

    def test_extracts_decklist_id_from_api_url(self):
        deck_id = extract_decklist_id(
            "https://ringsdb.com/api/public/decklist/337.json"
        )
        assert deck_id == "337"

    def test_extracts_decklist_id_from_bare_id(self):
        assert extract_decklist_id("337") == "337"

    def test_rejects_invalid_reference(self):
        assert extract_decklist_id("https://example.com/deck/337") is None


class TestFellowshipReferenceParsing:
    def test_extracts_fellowship_id_from_share_url(self):
        fellowship_id = extract_fellowship_id(
            "https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship"
        )
        assert fellowship_id == "7100"

    def test_extracts_fellowship_id_from_bare_id(self):
        assert extract_fellowship_id("7100") == "7100"


class TestScenarioReferenceParsing:
    def test_extracts_scenario_id_from_api_url(self):
        scenario_id, scenario_slug = extract_scenario_reference(
            "https://ringsdb.com/api/public/scenario/1.json"
        )
        assert scenario_id == "1"
        assert scenario_slug is None

    def test_extracts_scenario_slug_from_hall_url(self):
        scenario_id, scenario_slug = extract_scenario_reference(
            "https://hallofbeorn.com/LotR/Scenarios/passage-through-mirkwood"
        )
        assert scenario_id is None
        assert scenario_slug == "passage-through-mirkwood"

    def test_extracts_scenario_id_from_bare_id(self):
        scenario_id, scenario_slug = extract_scenario_reference("1")
        assert scenario_id == "1"
        assert scenario_slug is None


class TestParseDeckRouting:
    @patch(
        "plugins.lotr_lcg.deck_formats.build_deck_entries",
        return_value=[
            {
                "card_code": "01001",
                "name": "Aragorn",
                "image_url": "https://ringsdb.com/bundles/cards/01001.png",
                "quantity": 1,
            }
        ],
    )
    @patch(
        "plugins.lotr_lcg.deck_formats.fetch_decklist",
        return_value={"name": "Test Deck", "heroes": {"01001": 1}, "slots": {"01001": 1}},
    )
    @patch("plugins.lotr_lcg.deck_formats.load_card_catalog", return_value={})
    def test_parse_deck_calls_handle_card(
        self,
        _mock_catalog,
        _mock_fetch_decklist,
        _mock_build_entries,
    ):
        seen = []

        def collect_card(index, card_code, name, image_url, quantity, back_image_url=None):
            seen.append((index, card_code, name, image_url, quantity, back_image_url))

        parse_deck("337", DeckFormat.RINGSDB, collect_card)

        assert seen == [
            (
                1,
                "01001",
                "Aragorn",
                "https://ringsdb.com/bundles/cards/01001.png",
                1,
                None,
            )
        ]

    @patch(
        "plugins.lotr_lcg.deck_formats.build_deck_entries",
        return_value=[
            {
                "card_code": "01005",
                "name": "Legolas",
                "image_url": "https://ringsdb.com/bundles/cards/01005.png",
                "quantity": 1,
            }
        ],
    )
    @patch(
        "plugins.lotr_lcg.deck_formats.fetch_fellowship_decks",
        return_value=(
            "Test Fellowship",
            [{"name": "Deck A", "heroes": {"01005": 1}, "slots": {"01005": 1}}],
        ),
    )
    @patch("plugins.lotr_lcg.deck_formats.load_card_catalog", return_value={})
    def test_parse_fellowship_calls_handle_card(
        self,
        _mock_catalog,
        _mock_fetch_fellowship,
        _mock_build_entries,
    ):
        seen = []

        def collect_card(index, card_code, name, image_url, quantity, back_image_url=None):
            seen.append((index, card_code, name, image_url, quantity, back_image_url))

        parse_deck("7100", DeckFormat.RINGSDB_FELLOWSHIP, collect_card)

        assert seen == [
            (
                1,
                "01005",
                "Legolas",
                "https://ringsdb.com/bundles/cards/01005.png",
                1,
                None,
            )
        ]

    @patch(
        "plugins.lotr_lcg.deck_formats.fetch_scenario_entries",
        return_value=[
            {
                "card_code": "Forest-Spider-Core",
                "name": "Forest Spider",
                "image_url": "https://hallofbeorn.com/Images/Cards/Core-Set/Forest-Spider.jpg",
                "back_image_url": None,
                "quantity": 2,
            }
        ],
    )
    @patch(
        "plugins.lotr_lcg.deck_formats.fetch_scenario_metadata",
        return_value={"name": "Passage Through Mirkwood", "nameCanonical": "passage-through-mirkwood"},
    )
    def test_parse_scenario_calls_handle_card(
        self,
        _mock_fetch_scenario_metadata,
        _mock_fetch_scenario_entries,
    ):
        seen = []

        def collect_card(index, card_code, name, image_url, quantity, back_image_url=None):
            seen.append((index, card_code, name, image_url, quantity, back_image_url))

        parse_deck("1", DeckFormat.RINGSDB_SCENARIO, collect_card, scenario_mode="normal")

        assert seen == [
            (
                1,
                "Forest-Spider-Core",
                "Forest Spider",
                "https://hallofbeorn.com/Images/Cards/Core-Set/Forest-Spider.jpg",
                2,
                None,
            )
        ]


class TestBackInstallation:
    def test_install_default_back(self):
        asset_dir = tempfile.mkdtemp()
        back_dir = tempfile.mkdtemp()
        try:
            asset_path = Path(asset_dir) / "Player Card Back.jpg"
            with Image.new("RGB", (10, 10), color="white") as image:
                image.save(asset_path, format="JPEG")

            with patch("plugins.lotr_lcg.ringsdb.ASSET_DIRECTORY", Path(asset_dir)):
                output_path = install_default_back(back_dir, "player")

            assert output_path.exists()
            assert output_path.name == "lotr_lcg_player_back.jpg"
        finally:
            shutil.rmtree(asset_dir)
            shutil.rmtree(back_dir)


class TestLandscapeRotation:
    @staticmethod
    def make_image_bytes(size: tuple[int, int], color: str) -> bytes:
        image = Image.new("RGB", size, color=color)
        output = BytesIO()
        image.save(output, format="JPEG")
        return output.getvalue()

    def test_handle_card_rotates_landscape_front_and_back(self):
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        front_bytes = self.make_image_bytes((600, 426), "red")
        back_bytes = self.make_image_bytes((600, 426), "blue")

        class FakeResponse:
            def __init__(self, content: bytes):
                self.content = content

        def fake_request(url: str):
            if "front" in url:
                return FakeResponse(front_bytes)
            return FakeResponse(back_bytes)

        try:
            with patch("plugins.lotr_lcg.ringsdb.request_ringsdb", side_effect=fake_request):
                handle_card = get_handle_card(front_dir, double_sided_dir)
                handle_card(
                    1,
                    "Quest-Card",
                    "Flies and Spiders",
                    "https://example.com/front.jpg",
                    quantity=1,
                    back_image_url="https://example.com/back.jpg",
                )

            front_files = os.listdir(front_dir)
            back_files = os.listdir(double_sided_dir)

            assert len(front_files) == 1
            assert len(back_files) == 1

            with Image.open(os.path.join(front_dir, front_files[0])) as front_image:
                assert front_image.height > front_image.width

            with Image.open(os.path.join(double_sided_dir, back_files[0])) as back_image:
                assert back_image.height > back_image.width
        finally:
            shutil.rmtree(front_dir)
            shutil.rmtree(double_sided_dir)


@pytest.mark.integration
class TestRingsDBAPI:
    def test_public_cards_endpoint_available(self):
        response = request_ringsdb(RINGSDB_ALL_CARDS_URL)
        cards = response.json()

        assert response.status_code == 200
        assert isinstance(cards, list)
        assert len(cards) > 1000


@pytest.mark.integration
class TestFullFetchWorkflow:
    @pytest.fixture
    def temp_dirs(self):
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        yield front_dir, double_sided_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(double_sided_dir)

    def test_fetch_deck_from_ringsdb(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs
        deck_text = "https://ringsdb.com/decklist/view/337/two-player-core-set-1-2-1.0"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_text, DeckFormat.RINGSDB, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 10

        for filename in files[:5]:
            file_path = os.path.join(front_dir, filename)
            assert os.path.getsize(file_path) > 0

    def test_fetch_fellowship_from_ringsdb(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs
        fellowship_text = "https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(fellowship_text, DeckFormat.RINGSDB_FELLOWSHIP, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 20

    def test_fetch_scenario_from_ringsdb(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs
        scenario_text = "1"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(
            scenario_text,
            DeckFormat.RINGSDB_SCENARIO,
            handle_card,
            scenario_mode="normal",
        )

        front_files = os.listdir(front_dir)
        double_sided_files = os.listdir(double_sided_dir)

        assert len(front_files) >= 10
        assert len(double_sided_files) >= 2
