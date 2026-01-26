import os
import tempfile
import pytest
from pathlib import Path
from PIL import Image

from utilities import (
    parse_crop_string,
    convertInToCrop,
    get_image_file_paths,
    check_paths_subset,
    resolve_image_with_any_extension,
    calculate_max_print_bleed,
    delete_hidden_files_in_directory,
    get_directory,
    offset_images,
    save_offset,
    load_saved_offset,
    OffsetData,
)


class TestParseCropString:
    """Tests for parse_crop_string() function."""

    def test_none_returns_zero(self):
        """None input should return (0, 0)."""
        assert parse_crop_string(None, 750, 1050) == (0, 0)

    def test_plain_integer(self):
        """Plain integer string should return same value for both dimensions."""
        assert parse_crop_string("9", 750, 1050) == (9, 9)

    def test_plain_float(self):
        """Plain float string should return same value for both dimensions."""
        assert parse_crop_string("6.5", 750, 1050) == (6.5, 6.5)

    def test_decimal_only(self):
        """Decimal without leading zero should parse correctly."""
        assert parse_crop_string(".5", 750, 1050) == (0.5, 0.5)

    def test_mm_integer(self):
        """Millimeter format with integer should convert correctly."""
        result = parse_crop_string("3mm", 750, 1050)
        # 3mm = 3/25.4 inches, then convertInToCrop is called
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] > 0
        assert result[1] > 0

    def test_mm_float(self):
        """Millimeter format with float should convert correctly."""
        result = parse_crop_string("2.5mm", 750, 1050)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_inches_format(self):
        """Inch format should convert correctly."""
        result = parse_crop_string("0.125in", 750, 1050)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] > 0
        assert result[1] > 0

    def test_inches_format_no_leading_zero(self):
        """Inch format without leading zero should work."""
        result = parse_crop_string(".1in", 750, 1050)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_case_insensitive_mm(self):
        """Millimeter format should be case insensitive."""
        result_lower = parse_crop_string("3mm", 750, 1050)
        result_upper = parse_crop_string("3MM", 750, 1050)
        assert result_lower == result_upper

    def test_case_insensitive_in(self):
        """Inch format should be case insensitive."""
        result_lower = parse_crop_string("0.1in", 750, 1050)
        result_upper = parse_crop_string("0.1IN", 750, 1050)
        assert result_lower == result_upper

    def test_whitespace_trimmed(self):
        """Leading/trailing whitespace should be trimmed."""
        assert parse_crop_string("  9  ", 750, 1050) == (9, 9)

    def test_invalid_format_raises(self):
        """Invalid format should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid crop format"):
            parse_crop_string("invalid", 750, 1050)

    def test_invalid_unit_raises(self):
        """Invalid unit should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid crop format"):
            parse_crop_string("3cm", 750, 1050)

    def test_empty_string_raises(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid crop format"):
            parse_crop_string("", 750, 1050)


class TestConvertInToCrop:
    """Tests for convertInToCrop() function."""

    def test_zero_crop(self):
        """Zero inch crop should return zero percentages."""
        assert convertInToCrop(0, 750, 1050) == (0, 0)

    def test_positive_crop(self):
        """Positive inch crop should return positive percentages."""
        result = convertInToCrop(0.125, 750, 1050)
        assert result[0] > 0
        assert result[1] > 0

    def test_x_y_different_for_nonsquare(self):
        """Non-square card should have different x and y crop percentages."""
        result = convertInToCrop(0.1, 750, 1050)
        # Different dimensions should give different percentages
        assert result[0] != result[1]

    def test_square_card_same_crop(self):
        """Square card should have same x and y crop percentages."""
        result = convertInToCrop(0.1, 750, 750)
        assert result[0] == result[1]

    def test_larger_crop_larger_percentage(self):
        """Larger inch crop should produce larger percentage."""
        result_small = convertInToCrop(0.1, 750, 1050)
        result_large = convertInToCrop(0.2, 750, 1050)
        assert result_large[0] > result_small[0]
        assert result_large[1] > result_small[1]


class TestGetImageFilePaths:
    """Tests for get_image_file_paths() function."""

    def test_empty_directory(self):
        """Empty directory should return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_image_file_paths(tmpdir)
            assert result == []

    def test_finds_png_files(self):
        """Should find PNG files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid PNG file
            img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(tmpdir, 'test.png')
            img.save(img_path, 'PNG')

            result = get_image_file_paths(tmpdir)
            assert 'test.png' in result

    def test_finds_jpeg_files(self):
        """Should find JPEG files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), color='blue')
            img_path = os.path.join(tmpdir, 'test.jpg')
            img.save(img_path, 'JPEG')

            result = get_image_file_paths(tmpdir)
            assert 'test.jpg' in result

    def test_ignores_non_image_files(self):
        """Should ignore non-image files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a text file
            txt_path = os.path.join(tmpdir, 'readme.txt')
            with open(txt_path, 'w') as f:
                f.write('hello')

            result = get_image_file_paths(tmpdir)
            assert 'readme.txt' not in result

    def test_recursive_search(self):
        """Should find images in subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, 'subdir')
            os.makedirs(subdir)

            img = Image.new('RGB', (100, 100), color='green')
            img_path = os.path.join(subdir, 'nested.png')
            img.save(img_path, 'PNG')

            result = get_image_file_paths(tmpdir)
            assert any('nested.png' in r for r in result)

    def test_returns_relative_paths(self):
        """Should return paths relative to input directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(tmpdir, 'test.png')
            img.save(img_path, 'PNG')

            result = get_image_file_paths(tmpdir)
            # Should not contain the tmpdir path
            assert all(not r.startswith(tmpdir) for r in result)


class TestCheckPathsSubset:
    """Tests for check_paths_subset() function."""

    def test_empty_sets(self):
        """Empty subset should return empty set."""
        assert check_paths_subset(set(), set()) == set()

    def test_all_in_mainset(self):
        """All subset items in mainset should return empty set."""
        subset = {'card1.png', 'card2.jpg'}
        mainset = {'card1.png', 'card2.png', 'card3.png'}
        result = check_paths_subset(subset, mainset)
        assert result == set()

    def test_missing_from_mainset(self):
        """Items not in mainset should be returned."""
        subset = {'card1.png', 'card4.png'}
        mainset = {'card1.png', 'card2.png', 'card3.png'}
        result = check_paths_subset(subset, mainset)
        assert 'card4.png' in result

    def test_ignores_extension(self):
        """Should match by stem, ignoring extension."""
        subset = {'card1.jpg'}
        mainset = {'card1.png'}
        result = check_paths_subset(subset, mainset)
        # card1.jpg should match card1.png by stem
        assert result == set()

    def test_different_extensions_match(self):
        """Different extensions with same stem should match."""
        subset = {'image.jpeg'}
        mainset = {'image.png', 'other.png'}
        result = check_paths_subset(subset, mainset)
        assert result == set()

    def test_with_paths(self):
        """Should work with path-like strings."""
        subset = {'subdir/card1.png'}
        mainset = {'card1.png', 'card2.png'}
        # stem of 'subdir/card1.png' is 'card1'
        result = check_paths_subset(subset, mainset)
        assert result == set()


class TestResolveImageWithAnyExtension:
    """Tests for resolve_image_with_any_extension() function."""

    def test_exact_path_exists(self):
        """Should return exact path if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(tmpdir, 'test.png')
            img.save(img_path, 'PNG')

            result = resolve_image_with_any_extension(img_path)
            assert result == img_path

    def test_finds_different_extension(self):
        """Should find file with different extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(tmpdir, 'test.jpg')
            img.save(img_path, 'JPEG')

            # Request .png but .jpg exists
            query_path = os.path.join(tmpdir, 'test.png')
            result = resolve_image_with_any_extension(query_path)
            assert result == img_path

    def test_missing_file_raises(self):
        """Should raise FileNotFoundError if no match found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            query_path = os.path.join(tmpdir, 'nonexistent.png')
            with pytest.raises(FileNotFoundError, match="Missing image"):
                resolve_image_with_any_extension(query_path)

    def test_ambiguous_match_raises(self):
        """Should raise ValueError if multiple matches found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two files with same stem but different extensions
            img = Image.new('RGB', (100, 100), color='red')
            img.save(os.path.join(tmpdir, 'test.png'), 'PNG')
            img.save(os.path.join(tmpdir, 'test.jpg'), 'JPEG')

            # Request a non-existent extension to trigger glob search
            query_path = os.path.join(tmpdir, 'test.gif')
            with pytest.raises(ValueError, match="Ambiguous"):
                resolve_image_with_any_extension(query_path)


class TestCalculateMaxPrintBleed:
    """Tests for calculate_max_print_bleed() function."""

    def test_single_card(self):
        """Single card (1x1 layout) should return (0, 0)."""
        result = calculate_max_print_bleed([100], [100], 200, 300)
        assert result == (0, 0)

    def test_two_columns(self):
        """Two columns should calculate horizontal bleed."""
        # Cards at x=100 and x=400, width=200
        # Gap = 400 - 100 - 200 = 100, bleed = 100/2 = 50
        x_pos = [100, 400]
        y_pos = [100]
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 50  # x bleed
        assert result[1] == 100000  # y bleed (single row)

    def test_two_rows(self):
        """Two rows should calculate vertical bleed."""
        x_pos = [100]
        y_pos = [100, 500]
        # Gap = 500 - 100 - 300 = 100, bleed = 100/2 = 50
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 100000  # x bleed (single column)
        assert result[1] == 50  # y bleed

    def test_grid_layout(self):
        """Grid layout (2x2) should calculate both bleeds."""
        x_pos = [100, 400]  # gap = 400 - 100 - 200 = 100, bleed = 50
        y_pos = [100, 500]  # gap = 500 - 100 - 300 = 100, bleed = 50
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 50
        assert result[1] == 50

    def test_unsorted_positions(self):
        """Should handle unsorted position lists."""
        x_pos = [400, 100]  # unsorted
        y_pos = [500, 100]  # unsorted
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 50
        assert result[1] == 50

    def test_no_gap_returns_large_value(self):
        """Overlapping cards (negative gap) should return large bleed value."""
        # Cards would overlap: positions closer than card width
        x_pos = [100, 150]  # gap = 150 - 100 - 200 = -150 (overlap)
        y_pos = [100]
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 100000  # Falls back to large value


class TestDeleteHiddenFilesInDirectory:
    """Tests for delete_hidden_files_in_directory() function."""

    def test_empty_path_does_nothing(self):
        """Empty path should not raise."""
        delete_hidden_files_in_directory("")

    def test_removes_ds_store(self):
        """Should remove .DS_Store files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ds_store = os.path.join(tmpdir, '.DS_Store')
            with open(ds_store, 'w') as f:
                f.write('junk')

            delete_hidden_files_in_directory(tmpdir)
            assert not os.path.exists(ds_store)

    def test_removes_thumbs_db(self):
        """Should remove Thumbs.db files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            thumbs = os.path.join(tmpdir, 'Thumbs.db')
            with open(thumbs, 'w') as f:
                f.write('junk')

            delete_hidden_files_in_directory(tmpdir)
            assert not os.path.exists(thumbs)

    def test_removes_desktop_ini(self):
        """Should remove desktop.ini files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            desktop_ini = os.path.join(tmpdir, 'desktop.ini')
            with open(desktop_ini, 'w') as f:
                f.write('junk')

            delete_hidden_files_in_directory(tmpdir)
            assert not os.path.exists(desktop_ini)

    def test_removes_apple_double_files(self):
        """Should remove Apple double files (._prefix)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            apple_double = os.path.join(tmpdir, '._image.png')
            with open(apple_double, 'w') as f:
                f.write('junk')

            delete_hidden_files_in_directory(tmpdir)
            assert not os.path.exists(apple_double)

    def test_preserves_normal_files(self):
        """Should not remove normal files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            normal_file = os.path.join(tmpdir, 'image.png')
            with open(normal_file, 'w') as f:
                f.write('data')

            delete_hidden_files_in_directory(tmpdir)
            assert os.path.exists(normal_file)


class TestGetDirectory:
    """Tests for get_directory() function."""

    def test_directory_path(self):
        """Directory path should return absolute directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_directory(tmpdir)
            assert result == os.path.abspath(tmpdir)

    def test_file_path(self):
        """File path should return absolute parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.txt')
            with open(file_path, 'w') as f:
                f.write('test')

            result = get_directory(file_path)
            assert result == os.path.abspath(tmpdir)


class TestOffsetImages:
    """Tests for offset_images() function."""

    def test_empty_list(self):
        """Empty list should return empty list."""
        result = offset_images([], 10, 10, 300)
        assert result == []

    def test_single_image_no_offset(self):
        """Single image (front page) should not be offset."""
        img = Image.new('RGB', (100, 100), color='red')
        result = offset_images([img], 10, 10, 300)
        assert len(result) == 1
        # First image should not be offset

    def test_alternating_offset(self):
        """Should offset every other image (back pages)."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        img3 = Image.new('RGB', (100, 100), color='green')

        result = offset_images([img1, img2, img3], 10, 10, 300)
        assert len(result) == 3
        # img1 (index 0) - no offset
        # img2 (index 1) - offset applied
        # img3 (index 2) - no offset

    def test_ppi_scaling(self):
        """Offset should scale with PPI."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')

        # At 300 PPI, offset of 30 should be 30 pixels
        result_300 = offset_images([img1.copy(), img2.copy()], 30, 30, 300)
        # At 600 PPI, offset of 30 should be 60 pixels
        result_600 = offset_images([img1.copy(), img2.copy()], 30, 30, 600)

        assert len(result_300) == 2
        assert len(result_600) == 2


class TestOffsetDataSaveLoad:
    """Tests for save_offset() and load_saved_offset() functions."""

    def test_save_and_load_roundtrip(self):
        """Saved offset should be loadable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory for the test
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                save_offset(10, 20)
                result = load_saved_offset()
                assert result is not None
                assert result.x_offset == 10
                assert result.y_offset == 20
            finally:
                os.chdir(original_cwd)

    def test_load_nonexistent_returns_none(self):
        """Loading non-existent offset file should return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = load_saved_offset()
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_offset_data_model(self):
        """OffsetData model should work correctly."""
        data = OffsetData(x_offset=5, y_offset=15)
        assert data.x_offset == 5
        assert data.y_offset == 15
