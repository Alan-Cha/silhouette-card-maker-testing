"""
Tests for the Elestrals plugin.
Tests deck format parsing and image fetching from Elestrals Play Network.
"""
import os
import shutil
import tempfile
import pytest

from plugins.elestrals.deck_formats import DeckFormat, parse_deck
from plugins.elestrals.elestrals import request_elestrals, get_handle_card, DECK_ID_URL_TEMPLATE


# --- Unit Tests for Deck Format Parsing ---

class TestElestralsFormat:
    """Test Elestrals deck ID format parsing."""

    def test_deck_id_pattern(self):
        """Test that deck IDs have expected format."""
        deck_id = "6883b784bd9cf7315d565843"

        # Elestrals deck IDs are 24-character hexadecimal strings (MongoDB ObjectId)
        assert len(deck_id) == 24
        assert all(c in '0123456789abcdef' for c in deck_id)

    def test_url_template_formatting(self):
        """Test that deck URL template formats correctly."""
        deck_id = "6883b784bd9cf7315d565843"
        url = DECK_ID_URL_TEMPLATE.format(deck_id=deck_id)

        assert deck_id in url
        assert "carde.io" in url.lower()  # Elestrals uses carde.io API


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestElestralsAPI:
    """Test Elestrals API requests."""

    def test_elestrals_api_availability(self):
        """Test that Elestrals API is available and responding."""
        deck_id = "6883b784bd9cf7315d565843"
        response = request_elestrals(DECK_ID_URL_TEMPLATE.format(deck_id=deck_id))
        assert response.status_code == 200

        # Verify response contains expected deck data structure
        json_data = response.json()
        assert 'data' in json_data


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_deck_from_elestrals(self, temp_dirs):
        """Test fetching cards from an Elestrals deck ID."""
        front_dir = temp_dirs

        # Use a known deck ID
        deck_text = "6883b784bd9cf7315d565843"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.ELESTRALS, handle_card)

        # Check that images were created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image files have content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
