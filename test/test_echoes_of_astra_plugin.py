"""
Tests for the Echoes of Astra plugin.
Tests deck URL pattern matching and Supabase API access.
"""
import os
import shutil
import tempfile
import pytest

from plugins.echoes_of_astra.api import request_astra, get_handle_card, ASTRA_ANON_KEY, ASTRA_DECK_URL_TEMPLATE
from plugins.echoes_of_astra.deck_formats import DeckFormat, parse_deck


# --- Unit Tests ---

class TestAstraURLFormat:
    """Test Astra Builder share URL format parsing."""

    def test_share_url_pattern_matches(self):
        """Test that valid Astra Builder share URLs are detected."""
        import re
        pattern = re.compile(r'https\:\/\/www\.astra-builder\.com\/\w+\/create\?deck=(\d+)')

        assert pattern.match("https://www.astra-builder.com/user123/create?deck=456")
        assert pattern.match("https://www.astra-builder.com/abc/create?deck=1")

    def test_share_url_pattern_rejects_invalid(self):
        """Test that invalid lines are rejected."""
        import re
        pattern = re.compile(r'https\:\/\/www\.astra-builder\.com\/\w+\/create\?deck=(\d+)')

        assert not pattern.match("")
        assert not pattern.match("https://www.astra-builder.com/create?deck=456")  # Missing username
        assert not pattern.match("https://example.com/user/create?deck=456")

    def test_share_url_extracts_deck_id(self):
        """Test that the deck ID is correctly extracted from a URL."""
        import re
        pattern = re.compile(r'https\:\/\/www\.astra-builder\.com\/\w+\/create\?deck=(\d+)')

        match = pattern.match("https://www.astra-builder.com/user123/create?deck=789")
        assert match is not None
        assert match.group(1) == "789"


# --- Integration Tests ---

@pytest.mark.integration
class TestEchoesOfAstraAPI:
    """Test Echoes of Astra API (Supabase) requests."""

    def test_supabase_api_availability(self):
        """Test that the Supabase API is available with the anon key."""
        from requests import get

        # Supabase returns 200 with an empty array for a non-existent deck ID
        url = ASTRA_DECK_URL_TEMPLATE.format(deck_id='0')
        response = get(url, headers={
            'user-agent': 'silhouette-card-maker/0.1',
            'accept': '*/*',
            'ApiKey': ASTRA_ANON_KEY
        })
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_deck_from_astra_builder(self, temp_dirs):
        """Test fetching cards from an Astra Builder deck URL."""
        front_dir = temp_dirs

        deck_text = "https://www.astra-builder.com/en/create?deck=122"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.ASTRA_URL, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
