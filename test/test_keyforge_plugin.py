"""
Tests for the KeyForge plugin.
Tests deck format parsing, Archon Arcana card resolution, and Master Vault deck loading.
"""
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from plugins.keyforge import archonarcana, deck_formats, mastervault
from plugins.keyforge.archonarcana import (API_URL, entry_to_title,
                                           get_handle_card, normalize_title,
                                           query_page_image,
                                           remove_nonalphanumeric,
                                           request_archonarcana, resolve_card,
                                           translate_special_characters)
from plugins.keyforge.deck_formats import (DeckFormat, parse_archon_arcana,
                                           parse_deck, parse_deck_url)
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

    def test_url_query_string_excluded(self):
        assert entry_to_title('https://www.archonarcana.com/wiki/Ecto-Charge?action=history') == 'Ecto-Charge'

    def test_url_fragment_excluded(self):
        assert entry_to_title('https://www.archonarcana.com/wiki/Ecto-Charge#Card') == 'Ecto-Charge'


class TestRemoveNonalphanumeric:
    """Test the filename sanitizer."""

    def test_removes_spaces_and_punctuation(self):
        assert remove_nonalphanumeric('Reassembly Required') == 'ReassemblyRequired'
        assert remove_nonalphanumeric('Shae \u201cCloudkicker\u201d') == 'ShaeCloudkicker'


# --- Unit Tests for MediaWiki API Page/Image Lookup ---

class TestQueryPageImage:
    """Test resolving a title to (canonical title, image URL) via the MediaWiki API."""

    def _fake_response(self, data: dict):
        response = MagicMock()
        response.json.return_value = data
        return response

    def test_returns_title_and_image_for_existing_page(self):
        data = {
            'query': {
                'pages': [
                    {
                        'pageid': 11067,
                        'title': 'Ecto-Charge',
                        'original': {'source': 'https://example.com/939-070.png'},
                    }
                ]
            }
        }
        with patch.object(archonarcana, 'request_archonarcana', return_value=self._fake_response(data)):
            assert query_page_image('Ecto-Charge') == ('Ecto-Charge', 'https://example.com/939-070.png')

    def test_returns_canonical_title_after_redirect(self):
        # redirects=1 makes the API resolve a redirect title to its target; the
        # page object's own title (not the query title) is the canonical one.
        data = {
            'query': {
                'redirects': [{'from': 'Ecto Charge', 'to': 'Ecto-Charge'}],
                'pages': [
                    {
                        'pageid': 11067,
                        'title': 'Ecto-Charge',
                        'original': {'source': 'https://example.com/939-070.png'},
                    }
                ]
            }
        }
        with patch.object(archonarcana, 'request_archonarcana', return_value=self._fake_response(data)):
            assert query_page_image('Ecto Charge') == ('Ecto-Charge', 'https://example.com/939-070.png')

    def test_returns_title_with_none_image_when_page_has_no_image(self):
        data = {
            'query': {
                'pages': [{'pageid': 123, 'title': 'Some Page'}]
            }
        }
        with patch.object(archonarcana, 'request_archonarcana', return_value=self._fake_response(data)):
            assert query_page_image('Some Page') == ('Some Page', None)

    def test_returns_none_for_missing_page(self):
        data = {
            'query': {
                'pages': [{'title': 'Not A Real Card', 'missing': True}]
            }
        }
        with patch.object(archonarcana, 'request_archonarcana', return_value=self._fake_response(data)):
            assert query_page_image('Not A Real Card') is None

    def test_returns_none_for_empty_pages_array(self):
        data = {'query': {'pages': []}}
        with patch.object(archonarcana, 'request_archonarcana', return_value=self._fake_response(data)):
            assert query_page_image('Anything') is None


# --- Unit Tests for Card Resolution Control Flow ---

class TestResolveCard:
    """Test resolve_card's direct-lookup/search-fallback branches without hitting the network."""

    def test_direct_hit_skips_search(self):
        with patch.object(archonarcana, 'query_page_image', return_value=('Ecto-Charge', 'https://example.com/a.png')), \
             patch.object(archonarcana, 'search_title') as mock_search:
            assert resolve_card('Ecto-Charge') == ('Ecto-Charge', 'https://example.com/a.png')
            mock_search.assert_not_called()

    def test_falls_back_to_search_when_direct_lookup_misses(self):
        with patch.object(archonarcana, 'query_page_image', side_effect=[None, ('Resolved Title', 'https://example.com/b.png')]), \
             patch.object(archonarcana, 'search_title', return_value='Resolved Title'):
            assert resolve_card('ecto charge') == ('Resolved Title', 'https://example.com/b.png')

    def test_raises_when_search_finds_nothing(self):
        with patch.object(archonarcana, 'query_page_image', return_value=None), \
             patch.object(archonarcana, 'search_title', return_value=None):
            with pytest.raises(Exception, match='card not found'):
                resolve_card('Not A Real Card')

    def test_raises_when_search_result_also_misses(self):
        with patch.object(archonarcana, 'query_page_image', return_value=None), \
             patch.object(archonarcana, 'search_title', return_value='Resolved Title'):
            with pytest.raises(Exception, match='card not found'):
                resolve_card('ecto charge')

    def test_skips_redundant_requery_when_search_resolves_to_same_title(self):
        # If search_title's exact-match branch returns the title already tried
        # directly, re-querying it would just repeat the same miss.
        with patch.object(archonarcana, 'query_page_image', return_value=None) as mock_query, \
             patch.object(archonarcana, 'search_title', return_value='Ecto-Charge'):
            with pytest.raises(Exception, match='card not found'):
                resolve_card('Ecto-Charge')

            mock_query.assert_called_once_with('Ecto-Charge')

    def test_raises_when_page_has_no_image(self):
        with patch.object(archonarcana, 'query_page_image', return_value=('Some Page', None)), \
             patch.object(archonarcana, 'search_title') as mock_search:
            with pytest.raises(Exception, match='card image not found'):
                resolve_card('Some Page')
            mock_search.assert_not_called()


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


# --- Unit Tests for Master Vault Defensive Field Access ---

class TestGetDeckCardCountsDefensive:
    """Test get_deck_card_counts against malformed/incomplete API data."""

    def _fake_response(self, data: dict):
        response = MagicMock()
        response.json.return_value = data
        return response

    def test_missing_title_fields_falls_back_to_card_id(self):
        # A card record missing both card_title_en and card_title (e.g. an
        # unannounced/non-standard card) must not raise a KeyError.
        data = {
            '_linked': {'cards': [{'id': 'card-1'}]},
            'data': {'_links': {'cards': ['card-1']}},
        }
        with patch.object(mastervault, 'request_mastervault', return_value=self._fake_response(data)):
            cards = mastervault.get_deck_card_counts('deck-1')

        assert cards == [('card-1', 1)]

    def test_missing_id_is_skipped_without_crashing(self):
        # A linked card missing 'id' must be skipped rather than raising a KeyError.
        data = {
            '_linked': {'cards': [{'card_title': 'Ecto-Charge'}]},
            'data': {'_links': {'cards': ['card-1']}},
        }
        with patch.object(mastervault, 'request_mastervault', return_value=self._fake_response(data)):
            cards = mastervault.get_deck_card_counts('deck-1')

        assert cards == []

    def test_prefers_english_title_over_localized_title(self):
        data = {
            '_linked': {'cards': [{'id': 'card-1', 'card_title': 'Titre', 'card_title_en': 'Title'}]},
            'data': {'_links': {'cards': ['card-1']}},
        }
        with patch.object(mastervault, 'request_mastervault', return_value=self._fake_response(data)):
            cards = mastervault.get_deck_card_counts('deck-1')

        assert cards == [('Title', 1)]


# --- Unit Tests for Master Vault Multi-Deck URL Batches ---

class TestParseDeckUrlResilience:
    """A bad deck URL must not drop decks already fetched earlier in the batch."""

    def test_bad_deck_does_not_drop_already_fetched_decks(self):
        def fake_extract_deck_id(line):
            if 'bad' in line:
                raise Exception(f'could not find a deck ID in "{line}"')
            return line

        def fake_get_deck_card_counts(deck_id):
            return [(f'{deck_id}-card', 1)]

        deck_text = '\n'.join(['good-deck-1', 'bad-deck', 'good-deck-2'])

        collected = []
        with patch.object(deck_formats, 'extract_deck_id', side_effect=fake_extract_deck_id), \
             patch.object(deck_formats, 'get_deck_card_counts', side_effect=fake_get_deck_card_counts):
            parse_deck_url(deck_text, lambda index, name, quantity: collected.append((index, name, quantity)))

        names = [name for _, name, _ in collected]
        assert names == ['good-deck-1-card', 'good-deck-2-card']

    def test_all_decks_bad_reports_errors_and_fetches_nothing(self):
        def fake_extract_deck_id(line):
            raise Exception(f'could not find a deck ID in "{line}"')

        collected = []
        with patch.object(deck_formats, 'extract_deck_id', side_effect=fake_extract_deck_id):
            parse_deck_url('bad-deck-1\nbad-deck-2', lambda index, name, quantity: collected.append((index, name, quantity)))

        assert collected == []


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
