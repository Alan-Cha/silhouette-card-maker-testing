"""
Tests for the KeyForge plugin.
Tests deck format parsing, Archon Arcana card resolution, and Master Vault deck loading.
"""
import os
import shutil
import tempfile

import pytest

from plugins.keyforge.archonarcana import (API_URL, entry_to_title,
                                           extract_image_url, get_handle_card,
                                           normalize_title,
                                           remove_nonalphanumeric,
                                           request_archonarcana, resolve_card,
                                           translate_special_characters)
from plugins.keyforge.deck_formats import (DeckFormat, parse_archon_arcana,
                                           parse_deck)
from plugins.keyforge.mastervault import extract_deck_id, get_deck_card_counts

# A stable, public deck used for Master Vault integration tests.
# It contains 36 deck cards + 4 Prophecy (non-deck) cards = 40 total,
# and 3 copies of "Gracchan Reform".
SAMPLE_DECK_ID = '4b86855f-71e5-4f54-a20d-2a58ec973f9c'
MASTER_VAULT_URL = f'https://www.keyforgegame.com/deck-details/{SAMPLE_DECK_ID}'
DECKS_OF_KEYFORGE_URL = f'https://decksofkeyforge.com/decks/{SAMPLE_DECK_ID}'


# --- Unit Tests for Deck Format Enum ---

class TestDeckFormatEnum:
    """Test the DeckFormat enum values."""

    def test_format_values(self):
        assert DeckFormat.ARCHON_ARCANA.value == 'archon_arcana'
        assert DeckFormat.MASTER_VAULT.value == 'master_vault'

    def test_no_separate_decks_of_keyforge_format(self):
        # Decks of KeyForge URLs are handled by the master_vault format.
        assert not hasattr(DeckFormat, 'DECKS_OF_KEYFORGE')


# --- Unit Tests for Special Character Translation ---

class TestTranslateSpecialCharacters:
    """Test ASCII-to-typographic translation used for Archon Arcana titles."""

    def test_ae_ligature(self):
        assert translate_special_characters('AEmber Imp') == '\u00c6mber Imp'

    def test_lowercase_ae_not_translated(self):
        # Only uppercase "AE" is folded to "Æ"; lowercase "ae" is left alone.
        assert translate_special_characters('aember imp') == 'aember imp'
        assert translate_special_characters('Praetor') == 'Praetor'

    def test_apostrophe(self):
        assert translate_special_characters("Nature's Call") == 'Nature\u2019s Call'

    def test_double_quotes(self):
        assert translate_special_characters('Shae "Cloudkicker"') == 'Shae \u201cCloudkicker\u201d'

    def test_plain_name_unchanged(self):
        assert translate_special_characters('Gracchan Reform') == 'Gracchan Reform'


# --- Unit Tests for Title Normalization ---

class TestNormalizeTitle:
    """Test the normalization used for matching and de-duplication."""

    def test_case_space_and_underscore_equivalent(self):
        assert normalize_title('Gracchan_Reform') == normalize_title('gracchan reform')

    def test_accents_folded(self):
        assert normalize_title('G\u0115zdruty\u014f the Arcane') == 'gezdrutyo the arcane'

    def test_ae_ligature_folded_to_ae(self):
        assert normalize_title('\u00c6mber Imp') == normalize_title('AEmber Imp') == 'aember imp'

    def test_apostrophe_variants_equal(self):
        assert normalize_title("Nature's Call") == normalize_title('Nature\u2019s Call')

    def test_quote_variants_equal(self):
        assert normalize_title('Shae "Cloudkicker"') == normalize_title('Shae \u201cCloudkicker\u201d')


# --- Unit Tests for Entry Parsing ---

class TestEntryToTitle:
    """Test extracting a wiki title from an input line."""

    def test_name_passthrough(self):
        assert entry_to_title('Ecto-Charge') == 'Ecto-Charge'

    def test_url_extraction(self):
        assert entry_to_title('https://www.archonarcana.com/wiki/Gracchan_Reform') == 'Gracchan Reform'

    def test_url_percent_decoding(self):
        # L%C3%A6rie -> Lærie
        assert entry_to_title('https://www.archonarcana.com/wiki/L%C3%A6rie_of_the_Lake') == 'L\u00e6rie of the Lake'


class TestRemoveNonalphanumeric:
    """Test the filename sanitizer."""

    def test_removes_spaces_and_punctuation(self):
        assert remove_nonalphanumeric('Reassembly Required') == 'ReassemblyRequired'
        assert remove_nonalphanumeric('Shae \u201cCloudkicker\u201d') == 'ShaeCloudkicker'


# --- Unit Tests for Image URL Extraction ---

class TestExtractImageUrl:
    """Test deriving the full-resolution image URL from page HTML."""

    def test_derives_original_from_thumbnail(self):
        html = (
            '<a href="/wiki/File:939-070.png" class="image">'
            '<img alt="Ecto-Charge" '
            'src="https://mywikis-wiki-media.s3.us-central-1.wasabisys.com/archonarcana/thumb/939-070.png/300px-939-070.png" '
            'width="300" height="420">'
        )
        assert extract_image_url(html) == (
            'https://mywikis-wiki-media.s3.us-central-1.wasabisys.com/archonarcana/939-070.png'
        )

    def test_returns_none_without_image(self):
        assert extract_image_url('<p>This page has no card image.</p>') is None


# --- Unit Tests for Master Vault Deck ID Extraction ---

class TestMasterVaultDeckId:
    """Test extracting the deck ID from Master Vault and Decks of KeyForge URLs."""

    def test_extract_from_master_vault_url(self):
        assert extract_deck_id(MASTER_VAULT_URL) == SAMPLE_DECK_ID

    def test_extract_from_decks_of_keyforge_url(self):
        assert extract_deck_id(DECKS_OF_KEYFORGE_URL) == SAMPLE_DECK_ID

    def test_raises_without_uuid(self):
        with pytest.raises(Exception):
            extract_deck_id('https://decksofkeyforge.com/decks/not-a-real-id')


# --- Unit Tests for Archon Arcana List Format ---

class TestArchonArcanaFormat:
    """Test the archon_arcana list format parsing and aggregation."""

    def test_aggregates_duplicates(self):
        deck_text = '\n'.join([
            'Gracchan_Reform',
            'gracchan reform',
            'Gracchan Reform',
            'Ecto-Charge',
        ])

        collected = []
        parse_archon_arcana(deck_text, lambda index, name, quantity: collected.append((index, name, quantity)))

        assert len(collected) == 2
        # All three Gracchan Reform spellings aggregate to a single card with quantity 3.
        assert collected[0][1] == 'Gracchan_Reform'
        assert collected[0][2] == 3
        assert collected[1][1] == 'Ecto-Charge'
        assert collected[1][2] == 1

    def test_skips_blank_and_comment_lines(self):
        deck_text = '# a comment\n\n// another comment\nEcto-Charge\n'

        collected = []
        parse_archon_arcana(deck_text, lambda index, name, quantity: collected.append((index, name, quantity)))

        assert len(collected) == 1
        assert collected[0][1] == 'Ecto-Charge'


# --- Integration Tests for Archon Arcana ---

@pytest.mark.integration
class TestArchonArcanaResolution:
    """Test live card resolution against Archon Arcana."""

    def test_api_availability(self):
        response = request_archonarcana(API_URL, params={
            'action': 'opensearch',
            'search': 'Ecto-Charge',
            'limit': '1',
            'namespace': '0',
            'format': 'json',
        })
        assert response.status_code == 200

    def test_resolve_basic_card(self):
        title, image_url = resolve_card('Ecto-Charge')
        assert title == 'Ecto-Charge'
        assert 'wasabisys' in image_url
        assert image_url.endswith('.png')
        assert '/thumb/' not in image_url

    def test_resolve_url_input(self):
        title, _ = resolve_card('https://www.archonarcana.com/wiki/Ecto-Charge')
        assert title == 'Ecto-Charge'

    def test_resolve_ae_ligature(self):
        assert resolve_card('AEmber Imp')[0] == '\u00c6mber Imp'

    def test_resolve_apostrophe_and_case(self):
        assert resolve_card("nature's call")[0] == 'Nature\u2019s Call'

    def test_resolve_accented_card(self):
        # "Gezdrutyo the Arcane" resolves to the accented "Gĕzdrutyŏ the Arcane".
        title, _ = resolve_card('Gezdrutyo the Arcane')
        assert title.endswith('the Arcane')

    def test_resolve_unknown_card_raises(self):
        with pytest.raises(Exception):
            resolve_card('Not-A-Real-Card-Zzz-Nonexistent')


# --- Integration Tests for Master Vault ---

@pytest.mark.integration
class TestMasterVaultAPI:
    """Test loading a deck's card list from Master Vault."""

    def test_get_deck_card_counts(self):
        cards = get_deck_card_counts(SAMPLE_DECK_ID)
        counts = dict(cards)

        # The deck contains three copies of Gracchan Reform.
        assert counts.get('Gracchan Reform') == 3

    def test_includes_non_deck_cards(self):
        cards = get_deck_card_counts(SAMPLE_DECK_ID)
        total = sum(quantity for _, quantity in cards)

        # 36 deck cards + 4 Prophecy (non-deck) cards. A total of 40 confirms
        # the non-deck cards are included.
        assert total == 40


# --- Integration Tests for the Full Fetch Workflow ---

@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dir(self):
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_archon_arcana_list(self, temp_dir):
        # Ecto-Charge x1 + Gracchan Reform x2 -> 3 image files.
        deck_text = 'Ecto-Charge\nGracchan Reform\ngracchan_reform'

        parse_deck(deck_text, DeckFormat.ARCHON_ARCANA, get_handle_card(temp_dir))

        files = os.listdir(temp_dir)
        assert len(files) == 3
        for f in files:
            assert os.path.getsize(os.path.join(temp_dir, f)) > 0

    @pytest.mark.slow
    def test_fetch_master_vault_deck(self, temp_dir):
        parse_deck(MASTER_VAULT_URL, DeckFormat.MASTER_VAULT, get_handle_card(temp_dir))

        files = os.listdir(temp_dir)
        assert len(files) >= 1
        for f in files:
            assert os.path.getsize(os.path.join(temp_dir, f)) > 0
