"""Tests for extend_corners functionality."""
import pytest
from PIL import Image
from utilities import draw_card_layout, FitMode
from enums import Orientation


class TestExtendCorners:
    """Tests for corner-specific bleed generation."""

    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)

    def test_extend_corners_with_radius(self):
        """With extend_corners, ONLY corners get bleed, straight edges are untouched.

        Card 60x60: red corners (10px), blue center.
        Target 60x60 at (25,25), extend_corners_radius=10.

        Only the corner regions should be cropped and have bleed generated.
        The straight edges should remain untouched (blue goes all the way to the edge).
        """
        card = Image.new('RGB', (60, 60), color='blue')

        # Draw red in the corner regions (10px radius)
        pixels = card.load()
        for x in range(10):
            for y in range(10):
                # Top-left corner
                pixels[x, y] = self.RED
                # Top-right corner
                pixels[59-x, y] = self.RED
                # Bottom-left corner
                pixels[x, 59-y] = self.RED
                # Bottom-right corner
                pixels[59-x, 59-y] = self.RED

        back = Image.new('RGB', (60, 60), color='gray')
        base = Image.new('RGB', (110, 110), color='white')

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[25], y_pos=[25],
            width=60, height=60,
            print_bleed=(0, 0),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_corners_radius=10,
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # The center of the card should be blue
        assert base.getpixel((55, 55)) == self.BLUE

        # The straight edges should be blue (not affected by corner processing)
        # Top edge (not in corner region)
        assert base.getpixel((55, 25)) == self.BLUE
        # Left edge (not in corner region)
        assert base.getpixel((25, 55)) == self.BLUE

    def test_extend_corners_zero_uses_regular_bleed(self):
        """With extend_corners_radius=0, should use regular bleed without corner awareness."""
        card = Image.new('RGB', (30, 30), color='blue')
        back = Image.new('RGB', (30, 30), color='gray')
        base = Image.new('RGB', (60, 60), color='white')

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[15], y_pos=[15],
            width=30, height=30,
            print_bleed=(5, 5),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_corners_radius=0,
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # Card should be placed with regular bleed
        # Center should be blue
        assert base.getpixel((30, 30)) == self.BLUE

        # Bleed areas should extend from edges
        # Top bleed
        assert base.getpixel((30, 10)) == self.BLUE

    def test_extend_edges_and_corners_together(self):
        """Both extend_edges and extend_corners can be used together.

        extend_edges crops all edges uniformly and generates uniform bleed.
        extend_corners then handles corner-specific bleed generation.
        """
        card = Image.new('RGB', (50, 50), color='green')

        # Add a 5px red border around the card
        pixels = card.load()
        for x in range(50):
            for y in range(50):
                if x < 5 or x >= 45 or y < 5 or y >= 45:
                    pixels[x, y] = self.RED

        back = Image.new('RGB', (50, 50), color='gray')
        base = Image.new('RGB', (100, 100), color='white')

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[25], y_pos=[25],
            width=50, height=50,
            print_bleed=(0, 0),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=5,  # Crop 5px from all edges
            extend_corners_radius=3,  # Corner-specific bleed with 3px radius
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # With extend_edges=5, the red border should be cropped away
        # Center should be green
        center_pixel = base.getpixel((50, 50))
        # Check that the pixel is greenish (G channel should be significantly higher than R and B)
        assert center_pixel[1] > center_pixel[0], f"Expected green-ish pixel, got {center_pixel}"
        assert center_pixel[1] > center_pixel[2], f"Expected green-ish pixel, got {center_pixel}"
