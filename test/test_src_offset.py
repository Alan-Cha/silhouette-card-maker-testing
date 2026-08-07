import tempfile
import os

from src.offset import save_offset, load_saved_offset, offset_images, OffsetData

from PIL import Image
from pathlib import Path
from unittest.mock import patch


class TestOffsetImages:
    """Tests for offset_images() function."""

    def test_empty_list(self):
        """Empty list should return empty list."""
        result = offset_images([], 10, 10, 300)
        assert result == []

    def test_single_image_no_offset(self):
        """Single image (front page) should not be offset."""
        img = Image.new("RGB", (100, 100), color="red")
        result = offset_images([img], 10, 10, 300)
        assert len(result) == 1
        assert result[0] is img  # Same object, not modified

    def test_alternating_offset(self):
        """Should offset every other image (back pages)."""
        img1 = Image.new("RGB", (100, 100), color="red")
        img3 = Image.new("RGB", (100, 100), color="green")

        # img2 has a white marker pixel at (0, 0) on a black background
        img2 = Image.new("RGB", (100, 100), color="black")
        img2.putpixel((0, 0), (255, 255, 255))

        result = offset_images([img1, img2, img3], 10, 10, 300)
        assert len(result) == 3
        assert result[0] is img1  # Front page unchanged
        assert result[2] is img3  # Front page unchanged
        # Back page: x_offset is negated to compensate for 180° flip, y_offset is unchanged.
        # floor(-10 * 300/300) = -10, floor(10 * 300/300) = 10
        # White pixel moves (0,0) -> (-10, 10) which wraps to (90, 10) in a 100x100 image.
        assert result[1].getpixel((90, 10)) == (255, 255, 255)
        assert result[1].getpixel((0, 0)) == (0, 0, 0)

    def test_ppi_scaling(self):
        """Offset should scale with PPI."""
        img_front = Image.new("RGB", (100, 100), color="red")

        # White marker pixel at (0, 0) on a black background
        img_back_a = Image.new("RGB", (100, 100), color="black")
        img_back_a.putpixel((0, 0), (255, 255, 255))
        img_back_b = Image.new("RGB", (100, 100), color="black")
        img_back_b.putpixel((0, 0), (255, 255, 255))

        # x_offset is negated: floor(-30 * 300/300) = -30 pixels → wraps to 70 in 100px image
        result_300 = offset_images([img_front.copy(), img_back_a], 30, 0, 300)
        # x_offset is negated: floor(-30 * 600/300) = -60 pixels → wraps to 40 in 100px image
        result_600 = offset_images([img_front.copy(), img_back_b], 30, 0, 600)

        assert result_300[1].getpixel((70, 0)) == (255, 255, 255)
        assert result_600[1].getpixel((40, 0)) == (255, 255, 255)


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
    
    # Test changed: Import path is now absolute derived from __file__
    def test_load_nonexistent_returns_none(self):
        """Loading non-existent offset file should return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "offset_data.json"

            with patch("src.offset.OFFSET_DATA_PATH", missing_path):
                result = load_saved_offset()

            assert result is None

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
