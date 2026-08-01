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

from plugins.lotr_lcg.card_entry import CardEntry

import pytest
from PIL import Image

from plugins.lotr_lcg.deck_formats import (
    DeckFormat,
    extract_decklist_id,
    extract_fellowship_id,
    extract_hallofbeorn_slug,
    extract_ringsdb_scenario_id,
    parse_deck,
)
from plugins.lotr_lcg.ringsdb import (
    RINGSDB_ALL_CARDS_URL,
    get_handle_card,
    request_ringsdb,
)


class TestDeckFormatEnum:
    def test_enum_values(self):
        assert DeckFormat.RINGSDB_URL.value == "ringsdb_url"
        assert DeckFormat.RINGSDB_FELLOWSHIP_URL.value == "ringsdb_fellowship_url"
        assert DeckFormat.RINGSDB_SCENARIO_URL.value == "ringsdb_scenario_url"
        assert DeckFormat.HALLOFBEORN_URL.value == "hallofbeorn_url"


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
        scenario_id = extract_ringsdb_scenario_id(
            "https://ringsdb.com/api/public/scenario/1.json"
        )
        assert scenario_id == "1"

    def test_extracts_scenario_slug_from_hall_url(self):
        scenario_slug = extract_hallofbeorn_slug(
            "https://hallofbeorn.com/LotR/Scenarios/passage-through-mirkwood"
        )
        assert scenario_slug == "passage-through-mirkwood"

    def test_extracts_scenario_id_from_bare_id(self):
        scenario_id = extract_ringsdb_scenario_id("1")
        assert scenario_id == "1"


class TestParseDeckRouting:
    @patch(
        "plugins.lotr_lcg.deck_formats.build_deck_entries",
        return_value=[
            CardEntry(
                card_code="01001",
                name="Aragorn",
                image_url="https://ringsdb.com/bundles/cards/01001.png",
                quantity=1,
            )
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

        parse_deck("337", DeckFormat.RINGSDB_URL, collect_card)

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
            CardEntry(
                card_code="01005",
                name="Legolas",
                image_url="https://ringsdb.com/bundles/cards/01005.png",
                quantity=1,
            )
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

        parse_deck("7100", DeckFormat.RINGSDB_FELLOWSHIP_URL, collect_card)

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
            CardEntry(
                card_code="Forest-Spider-Core",
                name="Forest Spider",
                image_url="https://hallofbeorn.com/Images/Cards/Core-Set/Forest-Spider.jpg",
                quantity=2,
                back_image_url=None,
            )
        ],
    )
    @patch(
        "plugins.lotr_lcg.deck_formats.fetch_scenario_metadata",
        return_value={"name": "Passage Through Mirkwood", "nameCanonical": "passage-through-mirkwood"},
    )
    @patch(
        "plugins.lotr_lcg.deck_formats.find_scenario_slug",
        return_value="Passage-Through-Mirkwood",
    )
    def test_parse_scenario_calls_handle_card(
        self,
        _mock_find_scenario_slug,
        _mock_fetch_scenario_metadata,
        _mock_fetch_scenario_entries,
    ):
        seen = []

        def collect_card(index, card_code, name, image_url, quantity, back_image_url=None):
            seen.append((index, card_code, name, image_url, quantity, back_image_url))

        parse_deck("1", DeckFormat.RINGSDB_SCENARIO_URL, collect_card, scenario_mode="normal")

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
        parse_deck(deck_text, DeckFormat.RINGSDB_URL, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 10

        for filename in files[:5]:
            file_path = os.path.join(front_dir, filename)
            assert os.path.getsize(file_path) > 0

    def test_fetch_fellowship_from_ringsdb(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs
        fellowship_text = "https://ringsdb.com/fellowship/view/7100/beginnermono-spherefellowship"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(fellowship_text, DeckFormat.RINGSDB_FELLOWSHIP_URL, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 20

    def test_fetch_scenario_from_ringsdb(self, temp_dirs):
        front_dir, double_sided_dir = temp_dirs
        scenario_text = "1"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(
            scenario_text,
            DeckFormat.RINGSDB_SCENARIO_URL,
            handle_card,
            scenario_mode="normal",
        )

        front_files = os.listdir(front_dir)
        double_sided_files = os.listdir(double_sided_dir)

        assert len(front_files) >= 10
        assert len(double_sided_files) >= 2


@pytest.mark.integration
class TestExampleDecklistsFromDocumentation:
    """
    Integration tests that verify the specific example decklists documented in the README.
    These tests make real API calls to RingsDB and Hall of Beorn.
    """

    @pytest.fixture
    def temp_dirs(self):
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        yield front_dir, double_sided_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(double_sided_dir)

    def test_ringsdb_decklist_337_contains_documented_heroes(self, temp_dirs):
        """
        Verifies that decklist #337 (Two Player Core Set) contains the heroes
        documented in the README: Legolas, Thalin, and Éowyn.
        """
        front_dir, double_sided_dir = temp_dirs
        deck_text = "337"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_text, DeckFormat.RINGSDB_URL, handle_card)

        files = os.listdir(front_dir)
        filenames_str = " ".join(files)

        # Verify documented heroes are present
        assert any("Legolas" in f for f in files), "Legolas should be in decklist #337"
        assert any("Thalin" in f for f in files), "Thalin should be in decklist #337"
        assert any("owyn" in f or "Eowyn" in f for f in files), "Éowyn should be in decklist #337"

        # Verify some documented player cards are present
        assert any("Gondorian_Spearman" in f for f in files), "Gondorian Spearman should be in decklist #337"
        assert any("Gandalf" in f for f in files), "Gandalf should be in decklist #337"

        # Verify total card count matches documented structure
        # Decklist has 3 heroes + 27 other cards (with quantities)
        assert len(files) >= 25, f"Expected at least 25 card images, got {len(files)}"

    def test_ringsdb_bare_id_format(self, temp_dirs):
        """
        Verifies that bare decklist ID format works as documented in README.
        """
        front_dir, double_sided_dir = temp_dirs

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck("337", DeckFormat.RINGSDB_URL, handle_card)

        files = os.listdir(front_dir)
        assert len(files) > 0, "Bare ID '337' should fetch cards"

    def test_ringsdb_fellowship_7100_contains_multiple_decks(self, temp_dirs):
        """
        Verifies that fellowship #7100 (Beginner Mono-Sphere Fellowship)
        contains cards from multiple decks as documented in README.
        """
        front_dir, double_sided_dir = temp_dirs
        fellowship_text = "7100"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(fellowship_text, DeckFormat.RINGSDB_FELLOWSHIP_URL, handle_card)

        files = os.listdir(front_dir)

        # Fellowship should have cards from multiple decks
        assert len(files) >= 20, f"Fellowship should have cards from multiple decks, got {len(files)}"

        # Verify images are valid
        for filename in files[:3]:
            file_path = os.path.join(front_dir, filename)
            assert os.path.getsize(file_path) > 1000, f"{filename} should be a valid image file"

    def test_scenario_1_passage_through_mirkwood_structure(self, temp_dirs):
        """
        Verifies that scenario #1 (Passage Through Mirkwood) has the structure
        documented in README: quest cards in double_sided, encounter cards in front.
        """
        front_dir, double_sided_dir = temp_dirs
        scenario_text = "1"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(
            scenario_text,
            DeckFormat.RINGSDB_SCENARIO_URL,
            handle_card,
            scenario_mode="normal",
        )

        front_files = os.listdir(front_dir)
        double_sided_files = os.listdir(double_sided_dir)

        # Should have encounter cards in front directory
        assert len(front_files) >= 8, f"Should have encounter cards, got {len(front_files)}"

        # Should have quest cards (double-sided) in double_sided directory
        assert len(double_sided_files) >= 2, f"Should have quest cards, got {len(double_sided_files)}"

        # Verify some documented encounter cards
        front_files_str = " ".join(front_files)
        assert any("Forest_Spider" in f or "forest_spider" in f.lower() for f in front_files), \
            "Forest Spider should be in scenario #1"

    def test_scenario_mode_variations(self, temp_dirs):
        """
        Verifies that different scenario modes (easy, normal, nightmare)
        produce different card quantities as documented in README.
        """
        front_dir, double_sided_dir = temp_dirs
        scenario_text = "1"

        # Test normal mode
        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(
            scenario_text,
            DeckFormat.RINGSDB_SCENARIO_URL,
            handle_card,
            scenario_mode="normal",
        )

        normal_count = len(os.listdir(front_dir))

        # Clean up for easy mode test
        for f in os.listdir(front_dir):
            os.remove(os.path.join(front_dir, f))
        for f in os.listdir(double_sided_dir):
            os.remove(os.path.join(double_sided_dir, f))

        # Test easy mode
        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(
            scenario_text,
            DeckFormat.RINGSDB_SCENARIO_URL,
            handle_card,
            scenario_mode="easy",
        )

        easy_count = len(os.listdir(front_dir))

        # Easy mode should have fewer or equal encounter cards than normal
        assert easy_count <= normal_count, \
            f"Easy mode ({easy_count}) should have <= cards than normal ({normal_count})"

    def test_landscape_quest_cards_rotated(self, temp_dirs):
        """
        Verifies that landscape quest cards are rotated to portrait orientation
        as documented in README.
        """
        front_dir, double_sided_dir = temp_dirs
        scenario_url = "https://hallofbeorn.com/LotR/Scenarios/Passage-Through-Mirkwood-Campaign"

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(
            scenario_url,
            DeckFormat.HALLOFBEORN_URL,
            handle_card,
            scenario_mode="normal",
        )

        double_sided_files = os.listdir(double_sided_dir)

        # Check that quest cards are portrait (height > width) after rotation
        for filename in double_sided_files[:2]:
            file_path = os.path.join(double_sided_dir, filename)
            with Image.open(file_path) as img:
                # Quest cards should be rotated to portrait orientation
                assert img.height > img.width, \
                    f"Quest card {filename} should be portrait orientation (rotated from landscape)"
