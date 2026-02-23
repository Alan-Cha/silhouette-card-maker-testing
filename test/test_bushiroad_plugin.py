"""
Tests for the Bushiroad plugin (Cardfight Vanguard, Weiss Schwarz, etc.).
Tests deck URL pattern matching and image fetching from Bushiroad CDNs.
"""
import os
import shutil
import tempfile
import pytest

from plugins.bushiroad.bushiroad import request_bushiroad, GameTitle, resolve_image_url, get_handle_card
from plugins.bushiroad.deck_formats import DeckFormat, parse_deck


# --- Unit Tests ---

class TestBushiroadURLFormat:
    """Test Bushiroad Decklog URL format parsing."""

    def test_decklog_en_url_pattern_matches(self):
        """Test that valid English Decklog URLs are detected."""
        import re
        pattern = re.compile(r'https?://decklog(?:-en)?\.bushiroad\.com/view/(\w+)\s*')

        assert pattern.match("https://decklog-en.bushiroad.com/view/ABCDEF")
        assert pattern.match("https://decklog-en.bushiroad.com/view/12345")

    def test_decklog_jp_url_pattern_matches(self):
        """Test that valid Japanese Decklog URLs are detected."""
        import re
        pattern = re.compile(r'https?://decklog(?:-en)?\.bushiroad\.com/view/(\w+)\s*')

        assert pattern.match("https://decklog.bushiroad.com/view/ABCDEF")

    def test_decklog_url_pattern_rejects_invalid(self):
        """Test that invalid lines are rejected."""
        import re
        pattern = re.compile(r'https?://decklog(?:-en)?\.bushiroad\.com/view/(\w+)\s*')

        assert not pattern.match("")
        assert not pattern.match("https://example.com/view/ABCDEF")
        assert not pattern.match("ABCDEF")

    def test_decklog_url_extracts_deck_code(self):
        """Test that the deck code is correctly extracted from a URL."""
        import re
        pattern = re.compile(r'https?://decklog(?:-en)?\.bushiroad\.com/view/(\w+)\s*')

        match = pattern.match("https://decklog-en.bushiroad.com/view/ABCDEF123")
        assert match is not None
        assert match.group(1) == "ABCDEF123"

    def test_resolve_image_url_vanguard(self):
        """Test that Cardfight Vanguard image URLs are resolved correctly."""
        url = resolve_image_url(GameTitle.CARDFIGHT_VANGUARD, "V-BT01/en_V-BT01-001EN.png")
        assert "en.cf-vanguard.com" in url
        assert "V-BT01/en_V-BT01-001EN.png" in url

    def test_resolve_image_url_weiss_schwarz(self):
        """Test that Weiss Schwarz image URLs are resolved correctly."""
        url = resolve_image_url(GameTitle.WEISS_SCHWARZ, "SAO/EN-W02-E001.jpg")
        assert "en.ws-tcg.com" in url
        assert "SAO/EN-W02-E001.jpg" in url

    def test_resolve_image_url_unsupported_raises(self):
        """Test that unsupported game title raises ValueError."""
        with pytest.raises(ValueError):
            resolve_image_url("Unsupported Game", "some_image.png")


# --- Integration Tests ---

@pytest.mark.integration
class TestBushiroadAPI:
    """Test Bushiroad Decklog API requests."""

    def test_decklog_server_availability(self):
        """Test that the Decklog server is available."""
        response = request_bushiroad("https://decklog-en.bushiroad.com/")
        assert response.status_code == 200


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        back_dir = tempfile.mkdtemp()
        yield front_dir, back_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(back_dir)

    def test_fetch_deck_from_decklog(self, temp_dirs):
        """Test fetching cards from a Bushiroad Decklog deck URL."""
        front_dir, back_dir = temp_dirs

        deck_text = "https://decklog-en.bushiroad.com/view/1HF6L"

        handle_card = get_handle_card(front_dir, back_dir)
        parse_deck(deck_text, DeckFormat.BUSHIROAD_URL, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
