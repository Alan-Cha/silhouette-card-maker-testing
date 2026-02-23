"""
Tests for the Pokemon plugin.
Tests deck format parsing and image fetching from the Limitless CDN and pokemontcg.io.
"""
import os
import shutil
import tempfile
import pytest

from plugins.pokemon.deck_formats import DeckFormat, parse_deck, parse_limitless
from plugins.pokemon.limitless import request_limitless, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestLimitlessFormat:
    """Test Limitless format parsing."""

    def test_parse_limitless_basic(self):
        """Test parsing basic Limitless format."""
        deck_text = "1 Pikachu ex SVI 047\n3 Nest Ball SVI 181"

        parsed_cards = []
        def collect_card(index, name, set_id, card_no, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'set_id': set_id,
                'card_no': card_no,
                'quantity': quantity
            })

        parse_limitless(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Pikachu ex"
        assert parsed_cards[0]['set_id'] == "SVI"
        assert parsed_cards[0]['card_no'] == "047"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Nest Ball"
        assert parsed_cards[1]['quantity'] == 3

    def test_parse_limitless_skips_empty_lines(self):
        """Test that empty lines are skipped."""
        deck_text = "1 Pikachu ex SVI 047\n\n3 Nest Ball SVI 181"

        parsed_cards = []
        def collect_card(index, name, set_id, card_no, quantity):
            parsed_cards.append({'name': name})

        parse_limitless(deck_text, collect_card)

        assert len(parsed_cards) == 2

    def test_parse_limitless_multi_word_name(self):
        """Test parsing a card with a multi-word name including apostrophe."""
        deck_text = "4 Professor's Research SVI 189"

        parsed_cards = []
        def collect_card(index, name, set_id, card_no, quantity):
            parsed_cards.append({'name': name, 'set_id': set_id, 'card_no': card_no, 'quantity': quantity})

        parse_limitless(deck_text, collect_card)

        assert len(parsed_cards) == 1
        assert parsed_cards[0]['name'] == "Professor's Research"
        assert parsed_cards[0]['set_id'] == "SVI"
        assert parsed_cards[0]['card_no'] == "189"
        assert parsed_cards[0]['quantity'] == 4

    def test_parse_limitless_line_pattern(self):
        """Test that the Limitless line pattern matches correctly."""
        import re
        pattern = re.compile(r'^(\d+)\s(.+)\s(\S+)\s(\S+)$')

        assert pattern.match("1 Pikachu ex SVI 047")
        assert pattern.match("4 Professor's Research SVI 189")

        assert not pattern.match("")
        assert not pattern.match("Pikachu ex SVI 047")  # No quantity


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestLimitlessAPI:
    """Test Limitless CDN requests."""

    def test_limitless_cdn_availability(self):
        """Test that the Limitless CDN is available and responding."""
        # Pikachu ex from Scarlet & Violet base set
        response = request_limitless(
            "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/SVI/SVI_047_R_EN_LG.png"
        )
        assert response.status_code == 200
        assert len(response.content) > 0


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card(self, temp_dirs):
        """Test fetching a single Pokemon card."""
        front_dir = temp_dirs

        deck_text = "1 Pikachu ex SVI 047"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.LIMITLESS, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_with_quantity(self, temp_dirs):
        """Test fetching a card with quantity > 1."""
        front_dir = temp_dirs

        deck_text = "2 Pikachu ex SVI 047"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.LIMITLESS, handle_card)

        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
