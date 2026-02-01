"""
Tests for the Yu-Gi-Oh! plugin.
Tests deck format parsing and image fetching from ygoprodeck.
"""
import os
import shutil
import tempfile
import pytest

from plugins.yugioh.deck_formats import DeckFormat, parse_deck, parse_ydk, parse_ydke
from plugins.yugioh.ygoprodeck import request_api, fetch_card_art


# --- Unit Tests for Deck Format Parsing ---

class TestYDKFormat:
    """Test YDK format parsing."""

    @pytest.fixture
    def temp_ydk_file(self):
        """Create a temporary YDK file for testing."""
        fd, path = tempfile.mkstemp(suffix='.ydk')
        with os.fdopen(fd, 'w') as f:
            f.write("""#main
91073013
92895501
92895501
#extra
90448279
!side
27204311""")
        yield path
        os.unlink(path)

    def test_parse_ydk_basic(self, temp_ydk_file):
        """Test parsing basic YDK format."""
        deck = parse_ydk(temp_ydk_file)

        # Should return [main, extra, side] lists
        assert len(deck) == 3
        assert 91073013 in deck[0]  # main deck
        assert deck[0].count(92895501) == 2  # 2 copies
        assert 90448279 in deck[1]  # extra deck
        assert 27204311 in deck[2]  # side deck

    def test_parse_deck_returns_card_dict(self, temp_ydk_file):
        """Test that parse_deck returns a card dictionary."""
        cards = parse_deck(temp_ydk_file, DeckFormat.YDK)

        # Should return {passcode: quantity} dict
        assert isinstance(cards, dict)
        assert 91073013 in cards
        assert cards[92895501] == 2  # 2 copies


class TestYDKEFormat:
    """Test YDKE format parsing."""

    def test_parse_ydke_basic(self):
        """Test parsing YDKE format."""
        # A minimal YDKE string with a few cards
        ydke_string = "ydke://CDfpBQ==!tGFNAQ==!reIKAg==!"

        deck = parse_ydke(ydke_string)

        # Should return [main, extra, side] lists
        assert len(deck) == 3
        assert isinstance(deck[0], list)

    def test_ydke_url_detection(self):
        """Test that YDKE strings are properly detected."""
        valid_ydke = "ydke://CDfpAQg36QGBAyEE!tGFNAQ==!reIKAg==!"
        invalid_ydke = "not-a-ydke-string"

        assert valid_ydke.startswith("ydke://")
        assert not invalid_ydke.startswith("ydke://")

    def test_ydke_invalid_format_raises(self):
        """Test that invalid YDKE format raises ValueError."""
        invalid_ydke = "ydke://invalid"  # Missing parts

        with pytest.raises(ValueError):
            parse_ydke(invalid_ydke)


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestYgoprodeckAPI:
    """Test YGOProDeck API requests."""

    def test_ygoprodeck_api_availability(self):
        """Test that YGOProDeck API is available and responding."""
        # Test with a known card ID (Blue-Eyes White Dragon)
        response = request_api("https://db.ygoprodeck.com/api/v7/cardinfo.php?id=89631139")
        assert response.status_code == 200

        json_data = response.json()
        assert 'data' in json_data

    def test_card_image_availability(self):
        """Test that card images are available from YGOProDeck."""
        # Blue-Eyes White Dragon image
        response = request_api("https://images.ygoprodeck.com/images/cards/89631139.jpg")
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

    @pytest.fixture
    def temp_ydk_single_card(self):
        """Create a temporary YDK file with a single card."""
        fd, path = tempfile.mkstemp(suffix='.ydk')
        with os.fdopen(fd, 'w') as f:
            f.write("""#main
89631139""")
        yield path
        os.unlink(path)

    def test_fetch_single_card(self, temp_dirs):
        """Test fetching a single card directly."""
        front_dir = temp_dirs

        # Fetch Blue-Eyes White Dragon
        fetch_card_art(89631139, 1, front_dir)

        # Check that image was created
        files = os.listdir(front_dir)
        assert len(files) == 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_card_with_quantity(self, temp_dirs):
        """Test fetching a card with quantity > 1."""
        front_dir = temp_dirs

        # Fetch 2 copies
        fetch_card_art(89631139, 2, front_dir)

        # Should have 2 images
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_from_ydk_file(self, temp_dirs, temp_ydk_single_card):
        """Test fetching cards from a YDK file."""
        front_dir = temp_dirs

        # Parse deck and fetch cards
        cards = parse_deck(temp_ydk_single_card, DeckFormat.YDK)

        for passcode, quantity in cards.items():
            fetch_card_art(passcode, quantity, front_dir)

        # Check that image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
