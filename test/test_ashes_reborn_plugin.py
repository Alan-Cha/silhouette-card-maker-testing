"""
Tests for the Ashes Reborn plugin.
Tests deck format parsing and image fetching from Ashes.live and AshesDB.
"""
import os
import shutil
import tempfile
import pytest

from plugins.ashes_reborn.deck_formats import DeckFormat, parse_deck
from plugins.ashes_reborn.ashes import request_ashes, get_handle_card, fetch_deck_data, ImageServer


# --- Unit Tests for Deck Format Parsing ---

class TestAshesShareUrlFormat:
    """Test Ashes share URL format parsing."""

    def test_deck_url_parsing(self):
        """Test that ashes.live deck URLs are recognized."""
        # Note: This format requires network access to parse the deck
        # We test the URL pattern recognition
        import re
        pattern = re.compile(r'https\:\/\/ashes.live\/decks\/share\/([^/]+)')

        url = "https://ashes.live/decks/share/57be4c41-6b6f-4770-8e30-b2fe9b9a6c72/"
        match = pattern.match(url)

        assert match is not None
        assert match.group(1) == "57be4c41-6b6f-4770-8e30-b2fe9b9a6c72"


class TestAshesDBShareUrlFormat:
    """Test AshesDB share URL format parsing."""

    def test_ashesdb_url_parsing(self):
        """Test that ashesdb.plaidhatgames.com deck URLs are recognized."""
        import re
        pattern = re.compile(r'https\:\/\/ashesdb.plaidhatgames.com\/decks\/share\/([^/]+)')

        url = "https://ashesdb.plaidhatgames.com/decks/share/0f8855d9-3c02-45e8-8458-366cbd755a04/"
        match = pattern.match(url)

        assert match is not None
        assert match.group(1) == "0f8855d9-3c02-45e8-8458-366cbd755a04"


# --- Integration Tests for API and Image Fetching ---

class TestAshesAPI:
    """Test Ashes API requests."""

    def test_ashes_api_availability(self):
        """Test that Ashes.live API is available and responding."""
        response = request_ashes("https://api.ashes.live/v2/cards")
        assert response.status_code == 200

    def test_fetch_deck_data(self):
        """Test fetching deck data from Ashes.live API."""
        deck_api_url = "https://api.ashes.live/v2/decks/shared/57be4c41-6b6f-4770-8e30-b2fe9b9a6c72"
        deck_data = fetch_deck_data(deck_api_url)

        # Should return a list of card entries
        assert isinstance(deck_data, list)
        assert len(deck_data) > 0


class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_deck_from_ashes_live(self, temp_dirs):
        """Test fetching cards from an Ashes.live deck URL."""
        front_dir = temp_dirs

        # Use a deck URL
        deck_text = "https://ashes.live/decks/share/57be4c41-6b6f-4770-8e30-b2fe9b9a6c72/"

        handle_card = get_handle_card(ImageServer.ASHES, front_dir)
        parse_deck(deck_text, DeckFormat.ASHES_SHARE_URL, handle_card)

        # Check that images were created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image files have content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
