import math
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
    get_back_card_image_path,
    crop_and_scale_image,
    draw_card_with_bleed,
    draw_card_layout,
    add_front_back_pages,
    FitMode,
    asset_directory,
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
        # 3mm = 3/25.4 inches; card is 2.5in x 3.5in at 300ppi
        # crop_x = 2 * (3/25.4) / 2.5 * 100, crop_y = 2 * (3/25.4) / 3.5 * 100
        assert result[0] == pytest.approx(600 / 63.5)
        assert result[1] == pytest.approx(600 / 88.9)

    def test_mm_float(self):
        """Millimeter format with float should convert correctly."""
        result = parse_crop_string("2.5mm", 750, 1050)
        # 2.5mm = 2.5/25.4 inches
        assert result[0] == pytest.approx(500 / 63.5)
        assert result[1] == pytest.approx(500 / 88.9)

    def test_inches_format(self):
        """Inch format should convert correctly."""
        result = parse_crop_string("0.125in", 750, 1050)
        # crop_x = 2 * 0.125 / 2.5 * 100 = 10.0
        # crop_y = 2 * 0.125 / 3.5 * 100 = 100/14
        assert result[0] == pytest.approx(10.0)
        assert result[1] == pytest.approx(100 / 14)

    def test_inches_format_no_leading_zero(self):
        """Inch format without leading zero should work."""
        result = parse_crop_string(".1in", 750, 1050)
        # crop_x = 2 * 0.1 / 2.5 * 100 = 8.0
        # crop_y = 2 * 0.1 / 3.5 * 100 = 40/7
        assert result[0] == pytest.approx(8.0)
        assert result[1] == pytest.approx(40 / 7)

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

    def test_exact_values(self):
        """Should compute correct percentages for known inputs."""
        # card_width_mm = 750/300 = 2.5in, card_height_mm = 1050/300 = 3.5in
        # crop_x = 2 * 0.125 / 2.5 * 100 = 10.0
        # crop_y = 2 * 0.125 / 3.5 * 100 ≈ 7.1429
        result = convertInToCrop(0.125, 750, 1050)
        assert result[0] == pytest.approx(10.0)
        assert result[1] == pytest.approx(100 / 14)

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
        """Two columns should calculate horizontal bleed; single row falls back to min_bleed."""
        # Cards at x=100 and x=400, width=200
        # Gap = 400 - 100 - 200 = 100, bleed = 100/2 = 50
        x_pos = [100, 400]
        y_pos = [100]
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 50  # x bleed
        assert result[1] == 0   # y bleed defaults to min_bleed (0)

    def test_two_rows(self):
        """Two rows should calculate vertical bleed; single column falls back to min_bleed."""
        x_pos = [100]
        y_pos = [100, 500]
        # Gap = 500 - 100 - 300 = 100, bleed = 100/2 = 50
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 0   # x bleed defaults to min_bleed (0)
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

    def test_min_bleed_single_card(self):
        """Single card with min_bleed should return (min_bleed, min_bleed)."""
        result = calculate_max_print_bleed([100], [100], 200, 300, min_bleed=15)
        assert result == (15, 15)

    def test_min_bleed_single_axis(self):
        """Single-axis dimension should use min_bleed as floor."""
        x_pos = [100, 400]
        y_pos = [100]
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300, min_bleed=15)
        assert result[0] == 50  # computed from gap
        assert result[1] == 15  # single row uses min_bleed

    def test_negative_gap_clamped_to_zero(self):
        """Overlapping cards (negative gap) should clamp bleed to zero."""
        # Cards would overlap: positions closer than card width
        x_pos = [100, 150]  # gap = 150 - 100 - 200 = -150, max(0, -75) = 0
        y_pos = [100]
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 0  # Negative gap clamped to 0
        assert result[1] == 0  # Single row defaults to min_bleed (0)


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
        assert result[0] is img  # Same object, not modified

    def test_alternating_offset(self):
        """Should offset every other image (back pages)."""
        img1 = Image.new('RGB', (100, 100), color='red')
        img3 = Image.new('RGB', (100, 100), color='green')

        # img2 has a white marker pixel at (0, 0) on a black background
        img2 = Image.new('RGB', (100, 100), color='black')
        img2.putpixel((0, 0), (255, 255, 255))

        result = offset_images([img1, img2, img3], 10, 10, 300)
        assert len(result) == 3
        assert result[0] is img1  # Front page unchanged
        assert result[2] is img3  # Front page unchanged
        # Back page offset by 10px at 300 PPI: white pixel moves (0,0) -> (10,10)
        assert result[1].getpixel((10, 10)) == (255, 255, 255)
        assert result[1].getpixel((0, 0)) == (0, 0, 0)

    def test_ppi_scaling(self):
        """Offset should scale with PPI."""
        img_front = Image.new('RGB', (100, 100), color='red')

        # White marker pixel at (0, 0) on a black background
        img_back_a = Image.new('RGB', (100, 100), color='black')
        img_back_a.putpixel((0, 0), (255, 255, 255))
        img_back_b = Image.new('RGB', (100, 100), color='black')
        img_back_b.putpixel((0, 0), (255, 255, 255))

        # At 300 PPI, offset of 30 = floor(30 * 300/300) = 30 pixels
        result_300 = offset_images([img_front.copy(), img_back_a], 30, 0, 300)
        # At 600 PPI, offset of 30 = floor(30 * 600/300) = 60 pixels
        result_600 = offset_images([img_front.copy(), img_back_b], 30, 0, 600)

        assert result_300[1].getpixel((30, 0)) == (255, 255, 255)
        assert result_600[1].getpixel((60, 0)) == (255, 255, 255)


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

    def test_save_and_load_with_angle(self):
        """Saved offset with angle should roundtrip correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                save_offset(10, 20, angle_offset=1.5)
                result = load_saved_offset()
                assert result is not None
                assert result.x_offset == 10
                assert result.y_offset == 20
                assert result.angle_offset == 1.5
            finally:
                os.chdir(original_cwd)

    def test_offset_data_model(self):
        """OffsetData model should work correctly."""
        data = OffsetData(x_offset=5, y_offset=15)
        assert data.x_offset == 5
        assert data.y_offset == 15

    def test_offset_data_default_angle(self):
        """OffsetData should default angle_offset to 0.0."""
        data = OffsetData(x_offset=5, y_offset=15)
        assert data.angle_offset == 0.0

    def test_offset_data_with_angle(self):
        """OffsetData should store angle_offset."""
        data = OffsetData(x_offset=5, y_offset=15, angle_offset=2.5)
        assert data.angle_offset == 2.5


class TestGetBackCardImagePath:
    """Tests for get_back_card_image_path() function."""

    def test_empty_directory_returns_none(self):
        """Directory with no images should return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_back_card_image_path(tmpdir)
            assert result is None

    def test_non_image_files_returns_none(self):
        """Directory with only non-image files should return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = os.path.join(tmpdir, 'readme.txt')
            with open(txt_path, 'w') as f:
                f.write('not an image')

            result = get_back_card_image_path(tmpdir)
            assert result is None

    def test_single_image_returns_path(self):
        """Directory with one image should return that image's path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(tmpdir, 'back.png')
            img.save(img_path, 'PNG')

            result = get_back_card_image_path(tmpdir)
            assert result is not None
            assert str(result).endswith('back.png')


class TestCropAndScaleImage:
    """Tests for crop_and_scale_image() function."""

    def test_stretch_real_bleed_both_axes(self):
        """STRETCH with enough source pixels should use real bleed on both axes."""
        # 300x420 source, 20% crop → cropped 240x336, ratio 1.2
        # unscaled bleed: 210*1.2=252 <= 300, 290*1.2=348 <= 420
        img = Image.new('RGB', (300, 420), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 20, 20, 200, 280, 5, 5, FitMode.STRETCH
        )
        assert result_img.size == (210, 290)
        assert off_x == -5
        assert off_y == -5
        assert synth == (0, 0)

    def test_stretch_no_room_for_bleed(self):
        """STRETCH without room for bleed should fall back to synthetic bleed."""
        # 200x280 source, 10% crop → cropped 180x252, ratio 0.9
        # unscaled bleed: 300*0.9=270 > 200
        img = Image.new('RGB', (200, 280), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 10, 10, 200, 280, 50, 50, FitMode.STRETCH
        )
        assert result_img.size == (200, 280)
        assert off_x == 0
        assert off_y == 0
        assert synth == (50, 50)

    def test_zero_crop_zero_bleed(self):
        """Zero crop and zero bleed should resize to target dimensions."""
        img = Image.new('RGB', (500, 700), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 0, 0, 200, 280, 0, 0, FitMode.STRETCH
        )
        assert result_img.size == (200, 280)
        assert off_x == 0
        assert off_y == 0
        assert synth == (0, 0)

    def test_crop_mode_real_bleed_both(self):
        """CROP mode with room on both axes should use real bleed."""
        # 300x420 source, 20% crop, uniform ratio = min(240/200, 336/280) = 1.2
        # unscaled bleed: 210*1.2=252 <= 300, 290*1.2=348 <= 420
        img = Image.new('RGB', (300, 420), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 20, 20, 200, 280, 5, 5, FitMode.CROP
        )
        assert result_img.size == (210, 290)
        assert off_x == -5
        assert off_y == -5
        assert synth == (0, 0)

    def test_crop_mode_real_bleed_x_only(self):
        """CROP mode with wide source should have real X bleed, synthetic Y."""
        # 300x280 source, 0% crop, uniform ratio = min(1.5, 1.0) = 1.0
        # unscaled X: 220*1.0=220 <= 300, unscaled Y: 300*1.0=300 > 280
        img = Image.new('RGB', (300, 280), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 0, 0, 200, 280, 10, 10, FitMode.CROP
        )
        assert result_img.size == (220, 280)
        assert off_x == -10
        assert off_y == 0
        assert synth == (0, 10)

    def test_crop_mode_real_bleed_y_only(self):
        """CROP mode with tall source should have synthetic X, real Y bleed."""
        # 200x420 source, 0% crop, uniform ratio = min(1.0, 1.5) = 1.0
        # unscaled X: 220*1.0=220 > 200, unscaled Y: 300*1.0=300 <= 420
        img = Image.new('RGB', (200, 420), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 0, 0, 200, 280, 10, 10, FitMode.CROP
        )
        assert result_img.size == (200, 300)
        assert off_x == 0
        assert off_y == -10
        assert synth == (10, 0)

    def test_crop_mode_neither_axis_bleeds(self):
        """CROP mode with tight source should use synthetic bleed on both axes."""
        # 200x280 source, 0% crop, uniform ratio = 1.0
        # unscaled X: 220 > 200, unscaled Y: 300 > 280
        img = Image.new('RGB', (200, 280), color='red')
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 0, 0, 200, 280, 10, 10, FitMode.CROP
        )
        assert result_img.size == (200, 280)
        assert off_x == 0
        assert off_y == 0
        assert synth == (10, 10)


class TestDrawCardWithBleed:
    """Tests for draw_card_with_bleed() function."""

    def test_card_placed_at_position(self):
        """Card should be pasted at the specified position."""
        card = Image.new('RGB', (10, 10), color='red')
        base = Image.new('RGB', (40, 40), color='white')
        draw_card_with_bleed(card, base, 15, 15, (5, 5))
        assert base.getpixel((15, 15)) == (255, 0, 0)
        assert base.getpixel((0, 0)) == (255, 255, 255)

    def test_edge_bleed_extends(self):
        """Edge bleed should extend the card's border pixels outward."""
        card = Image.new('RGB', (10, 10), color='red')
        base = Image.new('RGB', (40, 40), color='white')
        draw_card_with_bleed(card, base, 15, 15, (5, 5))
        # Top bleed: top row extended upward
        assert base.getpixel((15, 14)) == (255, 0, 0)
        assert base.getpixel((15, 10)) == (255, 0, 0)
        # Left bleed: left column extended leftward
        assert base.getpixel((14, 15)) == (255, 0, 0)
        assert base.getpixel((10, 15)) == (255, 0, 0)
        # Bottom bleed
        assert base.getpixel((15, 25)) == (255, 0, 0)
        # Right bleed
        assert base.getpixel((25, 15)) == (255, 0, 0)

    def test_corner_bleed_fills(self):
        """Corner bleed regions should be filled with corner pixel color."""
        card = Image.new('RGB', (10, 10), color='red')
        base = Image.new('RGB', (40, 40), color='white')
        draw_card_with_bleed(card, base, 15, 15, (5, 5))
        # Top-left corner bleed region
        assert base.getpixel((10, 10)) == (255, 0, 0)
        assert base.getpixel((14, 14)) == (255, 0, 0)
        # Bottom-right corner bleed region
        assert base.getpixel((25, 25)) == (255, 0, 0)
        assert base.getpixel((29, 29)) == (255, 0, 0)

    def test_zero_bleed(self):
        """Zero bleed should just place the card with no bleed extension."""
        card = Image.new('RGB', (10, 10), color='red')
        base = Image.new('RGB', (40, 40), color='white')
        draw_card_with_bleed(card, base, 15, 15, (0, 0))
        assert base.getpixel((15, 15)) == (255, 0, 0)
        assert base.getpixel((24, 24)) == (255, 0, 0)
        # Adjacent pixels outside card should remain white
        assert base.getpixel((14, 15)) == (255, 255, 255)
        assert base.getpixel((15, 14)) == (255, 255, 255)


class TestDrawCardLayout:
    """Tests for draw_card_layout() function."""

    def test_single_card_placed(self):
        """Single card in 1x1 layout should be placed at the layout position."""
        card = Image.new('RGB', (100, 140), color='red')
        back = Image.new('RGB', (100, 140), color='blue')
        base = Image.new('RGB', (300, 400), color='white')

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=100, height=140,
            print_bleed=(0, 0),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0, extend_corners=0,
            flip=False, fit=FitMode.STRETCH
        )
        assert base.getpixel((50, 50)) == (255, 0, 0)
        assert base.getpixel((100, 100)) == (255, 0, 0)
        # Outside card area should remain white
        assert base.getpixel((0, 0)) == (255, 255, 255)

    def test_none_card_skipped(self):
        """None entries in card list should leave base image unchanged."""
        back = Image.new('RGB', (100, 140), color='blue')
        base = Image.new('RGB', (300, 400), color='white')
        original_data = list(base.tobytes())

        draw_card_layout(
            card_images=[None],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=100, height=140,
            print_bleed=(0, 0),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0, extend_corners=0,
            flip=False, fit=FitMode.STRETCH
        )
        assert list(base.tobytes()) == original_data

    def test_flip_reverses_row_order(self):
        """Flip should place first card at bottom row and second at top."""
        red_card = Image.new('RGB', (100, 140), color='red')
        blue_card = Image.new('RGB', (100, 140), color='blue')
        back = Image.new('RGB', (100, 140), color='green')
        base = Image.new('RGB', (300, 500), color='white')

        draw_card_layout(
            card_images=[red_card, blue_card],
            single_back_image=back,
            base_image=base,
            num_rows=2, num_cols=1,
            x_pos=[50], y_pos=[50, 250],
            width=100, height=140,
            print_bleed=(0, 0),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0, extend_corners=0,
            flip=True, fit=FitMode.STRETCH
        )
        # With flip: card 0 (red) goes to row 1 (y=250), card 1 (blue) to row 0 (y=50)
        # Images are rotated 180 degrees, but still the same color
        assert base.getpixel((50, 250)) == (255, 0, 0)
        assert base.getpixel((50, 50)) == (0, 0, 255)


class TestAddFrontBackPages:
    """Tests for add_front_back_pages() function."""

    def test_appends_front_and_back(self):
        """With only_fronts=False, should append both front and back pages."""
        front = Image.new('RGB', (300, 400), color='white')
        back = Image.new('RGB', (300, 400), color='white')
        pages = []

        add_front_back_pages(
            front, back, pages,
            page_width=300, page_height=400,
            ppi_ratio=1.0, template='test_v1',
            only_fronts=False, name=None
        )
        assert len(pages) == 2
        assert pages[0] is front
        assert pages[1] is back

    def test_only_fronts_appends_one(self):
        """With only_fronts=True, should append only the front page."""
        front = Image.new('RGB', (300, 400), color='white')
        back = Image.new('RGB', (300, 400), color='white')
        pages = []

        add_front_back_pages(
            front, back, pages,
            page_width=300, page_height=400,
            ppi_ratio=1.0, template='test_v1',
            only_fronts=True, name=None
        )
        assert len(pages) == 1
        assert pages[0] is front

    def test_sheet_numbering_increments(self):
        """Sheet number should increment based on existing pages list size."""
        front1 = Image.new('RGB', (300, 400), color='white')
        back1 = Image.new('RGB', (300, 400), color='white')
        front2 = Image.new('RGB', (300, 400), color='white')
        back2 = Image.new('RGB', (300, 400), color='white')
        pages = []

        add_front_back_pages(
            front1, back1, pages,
            page_width=300, page_height=400,
            ppi_ratio=1.0, template='test_v1',
            only_fronts=False, name=None
        )
        add_front_back_pages(
            front2, back2, pages,
            page_width=300, page_height=400,
            ppi_ratio=1.0, template='test_v1',
            only_fronts=False, name=None
        )
        assert len(pages) == 4

    def test_name_label(self):
        """Providing a name should not raise (label includes name)."""
        front = Image.new('RGB', (300, 400), color='white')
        back = Image.new('RGB', (300, 400), color='white')
        pages = []

        add_front_back_pages(
            front, back, pages,
            page_width=300, page_height=400,
            ppi_ratio=1.0, template='test_v1',
            only_fronts=False, name='my_deck'
        )
        assert len(pages) == 2
