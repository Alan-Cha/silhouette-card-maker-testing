"""
Tests for the MTG plugin.
Tests deck format parsing and image fetching from Scryfall.
"""
import os
import shutil
import tempfile
import pytest

from plugins.mtg.deck_formats import (
    DeckFormat,
    parse_deck,
    parse_simple_list,
    parse_mtga,
    parse_mtgo,
    parse_archidekt,
    parse_deckstats,
    parse_moxfield,
    parse_scryfall_json,
)
from plugins.mtg.scryfall import request_scryfall, get_handle_card
from plugins.mtg.patterns import MOXFIELD_PATTERN, DECKSTATS_PATTERN

# --- Unit Tests for Deck Format Parsing ---

class TestDeckFormatParsing:
    """Test regex pattern matching for special deck format cases."""

    def test_star_symbol_in_collector_number(self):
        """Test that Moxfield star symbol in collector numbers is matched."""
        # Moxfield exports can include ★ in collector numbers for special versions
        line = "1 Sol Ring (SLD) 123★"
        match = MOXFIELD_PATTERN.match(line)

        assert match is not None
        assert match.group(1) == "1"
        assert match.group(2) == "Sol Ring"
        assert match.group(3) == "SLD"
        assert match.group(4) == "123★"


    def test_collector_number_with_dash(self):
        """Test that collector numbers with dashes are matched."""
        # Collector numbers like "123-456" should also be captured
        line = "1 Some Card (SET) 123-456"
        match = MOXFIELD_PATTERN.match(line)

        assert match is not None
        assert match.group(4) == "123-456"


    def test_quantity_with_x(self):
        """Test that quantities with "x" suffix are matched."""
        # Moxfield format can include "x" after quantity (e.g. "4x")
        line = "4x Lightning Bolt (2XM) 117"
        match = MOXFIELD_PATTERN.match(line)

        assert match is not None
        assert match.group(1) == "4"
        assert match.group(2) == "Lightning Bolt"
        assert match.group(3) == "2XM"
        assert match.group(4) == "117"


    def test_deckstats_star_symbol_in_collector_number(self):
        """Test that Deckstats star symbol in collector numbers is matched."""
        # Deckstats can include ★ in collector numbers
        # e.g. "1 [SLD#1494★] Sol Ring"
        line = "1 [SLD#1494★] Sol Ring"
        match = DECKSTATS_PATTERN.match(line)

        assert match is not None
        assert match.group(1) == "1"
        assert match.group(2) == "SLD"
        assert match.group(3) == "1494★"
        assert match.group(4) == "Sol Ring"

class TestSimpleFormat:
    """Test the simple card name list format."""

    def test_parse_simple_list(self):
        """Test parsing a simple list of card names."""
        deck_text = """Isshin, Two Heavens as One
Arid Mesa
Battlefield Forge"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_simple_list(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['name'] == "Isshin, Two Heavens as One"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Arid Mesa"
        assert parsed_cards[2]['name'] == "Battlefield Forge"


class TestMTGAFormat:
    """Test MTG Arena format parsing."""

    def test_parse_mtga_with_set_info(self):
        """Test parsing MTGA format with set and collector number."""
        deck_text = """Deck
2 Arid Mesa (MH2) 244
1 Lion Sash (NEO) 26"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_mtga(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Arid Mesa"
        assert parsed_cards[0]['set_code'] == "MH2"
        assert parsed_cards[0]['collector_number'] == "244"
        assert parsed_cards[0]['quantity'] == 2

    def test_parse_mtga_without_set_info(self):
        """Test parsing MTGA format without set information."""
        deck_text = """Deck
2x Mountain
1 Lightning Bolt"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_mtga(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Mountain"
        assert parsed_cards[0]['set_code'] == ""


class TestMTGOFormat:
    """Test MTG Online format parsing."""

    def test_parse_mtgo(self):
        """Test parsing MTGO format."""
        deck_text = """1 Ainok Bond-Kin
2 Witch Enchanter

SIDEBOARD:
1 Containment Priest"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_mtgo(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['name'] == "Ainok Bond-Kin"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Witch Enchanter"
        assert parsed_cards[1]['quantity'] == 2


class TestArchidektFormat:
    """Test Archidekt format parsing."""

    def test_parse_archidekt(self):
        """Test parsing Archidekt format with tags and foil markers."""
        deck_text = """1x Agadeem's Awakening // Agadeem, the Undercrypt (znr) 90 [Resilience,Land]
1x Ashnod's Altar (ema) 218 *F* [Mana Advantage]"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_archidekt(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Agadeem's Awakening // Agadeem, the Undercrypt"
        assert parsed_cards[0]['set_code'] == "znr"
        assert parsed_cards[0]['collector_number'] == "90"


class TestDeckstatsFormat:
    """Test Deckstats format parsing."""

    def test_parse_deckstats_with_set(self):
        """Test parsing Deckstats format with set info."""
        deck_text = """//Main
1 [2XM#310] Ash Barrens
1 Blinkmoth Nexus"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_deckstats(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Ash Barrens"
        assert parsed_cards[0]['set_code'] == "2XM"
        assert parsed_cards[0]['collector_number'] == "310"
        assert parsed_cards[1]['name'] == "Blinkmoth Nexus"
        assert parsed_cards[1]['set_code'] == ""


class TestMoxfieldFormat:
    """Test Moxfield format parsing."""

    def test_parse_moxfield(self):
        """Test parsing Moxfield format."""
        deck_text = """1 Ainok Bond-Kin (2X2) 5
2 Witch Enchanter // Witch-Blessed Meadow (MH3) 239"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_moxfield(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Ainok Bond-Kin"
        assert parsed_cards[0]['set_code'] == "2X2"
        assert parsed_cards[1]['name'] == "Witch Enchanter // Witch-Blessed Meadow"


class TestScryfallJsonFormat:
    """Test Scryfall JSON format parsing."""

    def test_parse_scryfall_json(self):
        """Test parsing Scryfall deck builder JSON."""
        deck_text = """{
  "entries": {
    "mainboard": [
      {
        "count": 2,
        "card_digest": {
          "name": "Lightning Bolt",
          "collector_number": "141",
          "set": "clu"
        }
      }
    ]
  }
}"""

        parsed_cards = []
        def collect_card(index, name, set_code, collector_number, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_code': set_code,
                'collector_number': collector_number,
                'quantity': quantity
            })

        parse_scryfall_json(deck_text, collect_card)

        assert len(parsed_cards) == 1
        assert parsed_cards[0]['name'] == "Lightning Bolt"
        assert parsed_cards[0]['set_code'] == "clu"
        assert parsed_cards[0]['quantity'] == 2


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestScryfallAPI:
    """Test Scryfall API requests."""

    def test_scryfall_api_availability(self):
        """Test that Scryfall API is available and responding."""
        response = request_scryfall("https://api.scryfall.com/cards/named?exact=Lightning+Bolt")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data.get('name') == "Lightning Bolt"


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        yield front_dir, double_sided_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(double_sided_dir)

    def test_fetch_single_card_simple_format(self, temp_dirs):
        """Test fetching a single card using simple format."""
        front_dir, double_sided_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "Lightning Bolt"

        handle_card = get_handle_card(
            ignore_set_and_collector_number=False,
            prefer_older_sets=False,
            prefer_sets=[],
            prefer_showcase=False,
            prefer_extra_art=False,
            tokens=False,
            front_img_dir=front_dir,
            double_sided_dir=double_sided_dir
        )

        parse_deck(deck_text, DeckFormat.SIMPLE, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_double_faced_card(self, temp_dirs):
        """Test fetching a double-faced card."""
        front_dir, double_sided_dir = temp_dirs

        # Use a modal double-faced card
        deck_text = "1 Agadeem's Awakening // Agadeem, the Undercrypt (ZNR) 90"

        handle_card = get_handle_card(
            ignore_set_and_collector_number=False,
            prefer_older_sets=False,
            prefer_sets=[],
            prefer_showcase=False,
            prefer_extra_art=False,
            tokens=False,
            front_img_dir=front_dir,
            double_sided_dir=double_sided_dir
        )

        parse_deck(deck_text, DeckFormat.MTGA, handle_card)

        # Check front side was saved
        front_files = os.listdir(front_dir)
        assert len(front_files) >= 1

        for f in front_files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_with_quantity(self, temp_dirs):
        """Test fetching cards with quantity > 1."""
        front_dir, double_sided_dir = temp_dirs

        deck_text = "2 Lightning Bolt"

        handle_card = get_handle_card(
            ignore_set_and_collector_number=False,
            prefer_older_sets=False,
            prefer_sets=[],
            prefer_showcase=False,
            prefer_extra_art=False,
            tokens=False,
            front_img_dir=front_dir,
            double_sided_dir=double_sided_dir
        )

        parse_deck(deck_text, DeckFormat.MTGO, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
