"""
Tests for the Netrunner plugin.
Tests deck format parsing and image fetching from NRO Proxy.
"""
import os
import shutil
import tempfile
import pytest

from plugins.netrunner.deck_formats import (
    DeckFormat,
    parse_deck,
    parse_text,
    parse_bbcode,
    parse_markdown,
    parse_plain_text,
    parse_jinteki,
)
from plugins.netrunner.api import request_api, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestTextFormat:
    """Test text format parsing."""

    def test_parse_text(self):
        """Test parsing text format."""
        deck_text = """Agenda (3)
1x Longevity Serum (System Gateway)
2x Regenesis (Midnight Sun)"""

        parsed_cards = []
        def collect_card(index, name, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_text(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Longevity Serum"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Regenesis"
        assert parsed_cards[1]['quantity'] == 2


class TestBBCodeFormat:
    """Test BBCode format parsing."""

    def test_parse_bbcode(self):
        """Test parsing BBCode format."""
        deck_text = """[b]Agenda (2)[/b]
3x [url=https://netrunnerdb.com/en/card/34040]Fujii Asset Retrieval[/url] [i](The Automata Initiative)[/i]
1x [url=https://netrunnerdb.com/en/card/30044]Longevity Serum[/url] [i](System Gateway)[/i]"""

        parsed_cards = []
        def collect_card(index, name, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_bbcode(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Fujii Asset Retrieval"
        assert parsed_cards[0]['quantity'] == 3


class TestMarkdownFormat:
    """Test Markdown format parsing."""

    def test_parse_markdown(self):
        """Test parsing Markdown format."""
        deck_text = """###Agenda (2)
* 3x [Fujii Asset Retrieval](https://netrunnerdb.com/en/card/34040) _(The Automata Initiative)_
* 1x [Longevity Serum](https://netrunnerdb.com/en/card/30044) _(System Gateway)_"""

        parsed_cards = []
        def collect_card(index, name, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_markdown(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Fujii Asset Retrieval"
        assert parsed_cards[0]['quantity'] == 3


class TestPlainTextFormat:
    """Test plain text format parsing."""

    def test_parse_plain_text(self):
        """Test parsing plain text format."""
        deck_text = """Agenda (2)
3x Fujii Asset Retrieval
1x Longevity Serum"""

        parsed_cards = []
        def collect_card(index, name, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_plain_text(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Fujii Asset Retrieval"
        assert parsed_cards[1]['name'] == "Longevity Serum"


class TestJintekiFormat:
    """Test Jinteki format parsing."""

    def test_parse_jinteki(self):
        """Test parsing Jinteki format."""
        deck_text = """3 Fujii Asset Retrieval
1 Longevity Serum
2 Regenesis"""

        parsed_cards = []
        def collect_card(index, name, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_jinteki(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['name'] == "Fujii Asset Retrieval"
        assert parsed_cards[0]['quantity'] == 3
        assert parsed_cards[2]['name'] == "Regenesis"


# --- Integration Tests for API and Image Fetching ---

class TestNetrunnerAPI:
    """Test Netrunner API requests."""

    def test_nro_api_availability(self):
        """Test that NRO Proxy API is available and responding."""
        response = request_api("https://proxy.nro.run/api/altarts")
        assert response.status_code == 200


class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card_jinteki(self, temp_dirs):
        """Test fetching a single card using Jinteki format."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1 Hedge Fund"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.JINTEKI, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_with_quantity(self, temp_dirs):
        """Test fetching cards with quantity > 1."""
        front_dir = temp_dirs

        deck_text = "2 Hedge Fund"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.JINTEKI, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
