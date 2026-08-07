import pytest

from src.images import (
    parse_crop_string,
    convert_inch_to_crop,
    calculate_max_print_bleed,
    crop_and_scale_image,
    MINIMUM_BLEED
)
from src.enums import FitMode

from PIL import Image


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

    # ValueError string changed. Just match to error type 
    def test_invalid_format_raises(self):
        """Invalid format should raise ValueError."""
        with pytest.raises(ValueError):
            _ = parse_crop_string("invalid", 750, 1050)

    # ValueError string changed. Just match to error type 
    def test_invalid_unit_raises(self):
        """Invalid unit should raise ValueError."""
        with pytest.raises(ValueError):
            _ = parse_crop_string("3cm", 750, 1050)

    # ValueError string changed. Just match to error type 
    def test_empty_string_raises(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError):
            _ = parse_crop_string("", 750, 1050)


class TestConvertInchToCrop:
    """Tests for convert_inch_to_crop() function."""

    def test_zero_crop(self):
        """Zero inch crop should return zero percentages."""
        assert convert_inch_to_crop(0, 750, 1050) == (0, 0)

    def test_exact_values(self):
        """Should compute correct percentages for known inputs."""
        # card_width_mm = 750/300 = 2.5in, card_height_mm = 1050/300 = 3.5in
        # crop_x = 2 * 0.125 / 2.5 * 100 = 10.0
        # crop_y = 2 * 0.125 / 3.5 * 100 ≈ 7.1429
        result = convert_inch_to_crop(0.125, 750, 1050)
        assert result[0] == pytest.approx(10.0)
        assert result[1] == pytest.approx(100 / 14)

    def test_x_y_different_for_nonsquare(self):
        """Non-square card should have different x and y crop percentages."""
        result = convert_inch_to_crop(0.1, 750, 1050)
        # Different dimensions should give different percentages
        assert result[0] != result[1]

    def test_square_card_same_crop(self):
        """Square card should have same x and y crop percentages."""
        result = convert_inch_to_crop(0.1, 750, 750)
        assert result[0] == result[1]

    def test_larger_crop_larger_percentage(self):
        """Larger inch crop should produce larger percentage."""
        result_small = convert_inch_to_crop(0.1, 750, 1050)
        result_large = convert_inch_to_crop(0.2, 750, 1050)
        assert result_large[0] > result_small[0]
        assert result_large[1] > result_small[1]


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
        assert result[1] == 0  # y bleed defaults to min_bleed (0)

    def test_two_rows(self):
        """Two rows should calculate vertical bleed; single column falls back to min_bleed."""
        x_pos = [100]
        y_pos = [100, 500]
        # Gap = 500 - 100 - 300 = 100, bleed = 100/2 = 50
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300)
        assert result[0] == 0  # x bleed defaults to min_bleed (0)
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
        result = calculate_max_print_bleed([100], [100], 200, 300, MINIMUM_BLEED)
        assert result == (15, 15)

    def test_min_bleed_single_axis(self):
        """Single-axis dimension should use min_bleed as floor."""
        x_pos = [100, 400]
        y_pos = [100]
        result = calculate_max_print_bleed(x_pos, y_pos, 200, 300, MINIMUM_BLEED)
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


class TestCropAndScaleImage:
    """Tests for crop_and_scale_image() function."""

    def test_stretch_real_bleed_both_axes(self):
        """STRETCH with enough source pixels should use real bleed on both axes."""
        # 300x420 source, 20% crop → cropped 240x336, ratio 1.2
        # unscaled bleed: 210*1.2=252 <= 300, 290*1.2=348 <= 420
        img = Image.new("RGB", (300, 420), color="red")
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
        img = Image.new("RGB", (200, 280), color="red")
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 10, 10, 200, 280, 50, 50, FitMode.STRETCH
        )
        assert result_img.size == (200, 280)
        assert off_x == 0
        assert off_y == 0
        assert synth == (50, 50)

    def test_zero_crop_zero_bleed(self):
        """Zero crop and zero bleed should resize to target dimensions."""
        img = Image.new("RGB", (500, 700), color="red")
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
        img = Image.new("RGB", (300, 420), color="red")
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
        img = Image.new("RGB", (300, 280), color="red")
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
        img = Image.new("RGB", (200, 420), color="red")
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
        img = Image.new("RGB", (200, 280), color="red")
        result_img, off_x, off_y, synth = crop_and_scale_image(
            img, 0, 0, 200, 280, 10, 10, FitMode.CROP
        )
        assert result_img.size == (200, 280)
        assert off_x == 0
        assert off_y == 0
        assert synth == (10, 10)
