"""
Tests for the Sorcery: Contested Realm plugin.
Tests API integration with curiosa.io.
"""
import os
import shutil
import tempfile
import pytest

from plugins.sorcery_contested_realm.curiosa import get_curiosa_decklist, get_handle_card, CURIOSA_API_BASE, DECK_ENDPOINTS
from plugins.sorcery_contested_realm.deck_formats import DeckFormat, parse_deck


# --- Unit Tests ---

class TestDeckFormatEnum:
    """Test the DeckFormat enum values."""

    def test_curiosa_format_value(self):
        """Test that the CURIOSA format has the expected value."""
        assert DeckFormat.CURIOSA.value == 'curiosa'


# --- Integration Tests ---

@pytest.mark.integration
class TestCuriosaTRPCAPI:
    """Test Curiosa TRPC API requests."""

    def test_curiosa_api_availability(self):
        """Test that the Curiosa TRPC API server is reachable."""
        # Call with an invalid deck ID - TRPC returns 200 with error data in body
        # rather than an HTTP error for individual query failures
        decklist = get_curiosa_decklist('invalid-deck-id-for-availability-test')
        # Returns an empty list for non-existent decks
        assert isinstance(decklist, list)

    def test_curiosa_api_base_url(self):
        """Test that the Curiosa API base URL is configured correctly."""
        assert CURIOSA_API_BASE == 'https://curiosa.io/api/trpc/'

    def test_curiosa_deck_endpoints(self):
        """Test that the expected deck endpoints are configured."""
        assert 'deck.getDecklistById' in DECK_ENDPOINTS
        assert 'deck.getAvatarById' in DECK_ENDPOINTS


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_deck_from_curiosa(self, temp_dirs):
        """Test fetching cards from a Curiosa deck ID."""
        front_dir = temp_dirs

        deck_id = "cme5x329q00k9jo04ouuycsek"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_id, DeckFormat.CURIOSA, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
