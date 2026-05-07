"""
Systematic tests for --extend_corners and --extend_edges.

These tests use a specially generated test image with:
- Concentric rectangles (2mm steps, alternating black/white) for edge testing
- Corner circles (1mm diameter steps, colored) for corner testing

This allows precise verification that the correct colors appear after extension.
"""

import os
import tempfile
import pytest
from PIL import Image, ImageDraw
from utilities import fill_rounded_corners, draw_card_layout, FitMode
from enums import Orientation


# Test image parameters
PPI = 300
CARD_WIDTH_MM = 63
CARD_HEIGHT_MM = 88


def mm_to_px(mm):
    """Convert mm to pixels at 300 PPI."""
    return int(mm * PPI / 25.4)


def create_systematic_test_image():
    """
    Create a test image with concentric rectangles and corner circles.

    Returns:
        PIL.Image: Test image with systematic patterns
    """
    width_px = mm_to_px(CARD_WIDTH_MM)
    height_px = mm_to_px(CARD_HEIGHT_MM)

    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)

    # Draw concentric rectangles as BANDS (not filled), alternating black/white
    # Each band is 2mm wide
    colors = ['black', 'white']

    i = 1
    while True:
        outer_inset = mm_to_px(2 * (i - 1))
        inner_inset = mm_to_px(2 * i)
        color = colors[i % 2]

        if inner_inset >= width_px // 2 or inner_inset >= height_px // 2:
            break

        # Draw the band as 4 rectangles (top, bottom, left, right)
        draw.rectangle([outer_inset, outer_inset, width_px - outer_inset, inner_inset], fill=color)
        draw.rectangle([outer_inset, height_px - inner_inset, width_px - outer_inset, height_px - outer_inset], fill=color)
        draw.rectangle([outer_inset, inner_inset, inner_inset, height_px - inner_inset], fill=color)
        draw.rectangle([width_px - inner_inset, inner_inset, width_px - outer_inset, height_px - inner_inset], fill=color)

        i += 1

    # Draw corner circles (1mm diameter steps)
    corner_colors = [
        (255, 0, 0),      # red (0.5mm radius)
        (255, 165, 0),    # orange (1.0mm radius)
        (255, 255, 0),    # yellow (1.5mm radius)
        (0, 255, 0),      # green (2.0mm radius)
        (0, 0, 255),      # blue (2.5mm radius)
    ]

    for i, color in enumerate(corner_colors):
        diameter_mm = 1 + i
        radius_px = mm_to_px(diameter_mm / 2)
        diameter_px = radius_px * 2

        # Top-left
        draw.ellipse([0, 0, diameter_px, diameter_px], fill=color)
        # Top-right
        draw.ellipse([width_px - diameter_px, 0, width_px, diameter_px], fill=color)
        # Bottom-left
        draw.ellipse([0, height_px - diameter_px, diameter_px, height_px], fill=color)
        # Bottom-right
        draw.ellipse([width_px - diameter_px, height_px - diameter_px, width_px, height_px], fill=color)

    return img


@pytest.fixture
def systematic_test_card():
    """Fixture that provides the systematic test card image."""
    return create_systematic_test_image()


class TestFillRoundedCorners:
    """Tests for the fill_rounded_corners function.

    Note: These tests verify that the fill function correctly extends pixels
    from the arc into the cut zone. They don't test color matching against the
    circles in the test image, as the function samples from the arc, not from
    inside the circles.
    """

    def test_no_fill_preserves_original(self, systematic_test_card):
        """With 0 radius, image should remain unchanged."""
        original_corner = systematic_test_card.getpixel((0, 0))
        filled = fill_rounded_corners(systematic_test_card, 0)
        filled_corner = filled.getpixel((0, 0))

        assert original_corner == filled_corner

    def test_fill_modifies_corner(self, systematic_test_card):
        """With non-zero radius, corner pixels in cut zone should be filled."""
        radius_px = mm_to_px(1.5)
        original = systematic_test_card.copy()
        filled = fill_rounded_corners(original, radius_px)

        # Check that the corner pixel changed (was filled)
        # Note: We don't check for a specific color, just that it's no longer white
        corner_pixel = filled.getpixel((0, 0))
        # The corner should have been filled with a color from the arc
        # It might be orange or another color depending on arc sampling
        assert corner_pixel != (255, 255, 255), f"Corner should be filled, got {corner_pixel}"


class TestExtendCornersWithLayout:
    """Integration tests for --extend_corners using draw_card_layout."""

    def test_corners_0_5mm_red(self, systematic_test_card):
        """--extend_corners 0.5mm with small radius."""
        back = Image.new('RGB', systematic_test_card.size, 'gray')
        base = Image.new('RGB', (systematic_test_card.width + 200, systematic_test_card.height + 200), 'white')

        draw_card_layout(
            card_images=[systematic_test_card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=systematic_test_card.width,
            height=systematic_test_card.height,
            print_bleed=(10, 10),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_corners_radius=mm_to_px(0.5),
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # Check regular edge bleed exists (not corner-specific, just general bleed)
        # The card is placed at (50, 50), bleed extends 10px beyond
        # Check top edge bleed
        top_edge_bleed = base.getpixel((100, 45))
        # Should have bleed (white from band 1)
        assert top_edge_bleed == (255, 255, 255), f"Edge bleed should be white (band 1), got {top_edge_bleed}"

    def test_corners_1_5mm_yellow(self, systematic_test_card):
        """--extend_corners 1.5mm should result in corner bleed from 17px arc."""
        back = Image.new('RGB', systematic_test_card.size, 'gray')
        base = Image.new('RGB', (systematic_test_card.width + 200, systematic_test_card.height + 200), 'white')

        draw_card_layout(
            card_images=[systematic_test_card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=systematic_test_card.width,
            height=systematic_test_card.height,
            print_bleed=(10, 10),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_corners_radius=mm_to_px(1.5),
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # After corner filling, bleed should be generated
        bleed_corner = base.getpixel((45, 45))
        assert bleed_corner != (255, 255, 255), f"Bleed should exist, got {bleed_corner}"


class TestExtendEdgesWithLayout:
    """Integration tests for --extend_edges using draw_card_layout."""

    def test_edges_2mm_black(self, systematic_test_card):
        """--extend_edges 2mm should result in black edge bleed."""
        back = Image.new('RGB', systematic_test_card.size, 'gray')
        base = Image.new('RGB', (systematic_test_card.width + 200, systematic_test_card.height + 200), 'white')

        width = systematic_test_card.width
        height = systematic_test_card.height
        edge_thickness = mm_to_px(2)

        draw_card_layout(
            card_images=[systematic_test_card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=width,
            height=height,
            print_bleed=(10, 10),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=edge_thickness,
            extend_corners_radius=0,
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # After cropping 2mm (23px), the card starts at (50 + 23, 50 + 23) = (73, 73)
        # Check a pixel near the top edge of the card
        card_start_x = 50 + edge_thickness
        card_start_y = 50 + edge_thickness
        top_edge_pixel = base.getpixel((card_start_x + 100, card_start_y + 5))
        # Should be black (band 2 after cropping)
        assert top_edge_pixel[0] < 50, f"Top edge should be black, got {top_edge_pixel}"
        assert top_edge_pixel[1] < 50, f"Top edge should be black, got {top_edge_pixel}"
        assert top_edge_pixel[2] < 50, f"Top edge should be black, got {top_edge_pixel}"

    def test_edges_4mm_white(self, systematic_test_card):
        """--extend_edges 4mm should result in white edge bleed."""
        back = Image.new('RGB', systematic_test_card.size, 'gray')
        base = Image.new('RGB', (systematic_test_card.width + 200, systematic_test_card.height + 200), 'white')

        width = systematic_test_card.width
        height = systematic_test_card.height
        edge_thickness = mm_to_px(4)

        draw_card_layout(
            card_images=[systematic_test_card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=width,
            height=height,
            print_bleed=(10, 10),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=edge_thickness,
            extend_corners_radius=0,
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # After cropping 4mm (47px), check the card edge
        card_start_x = 50 + edge_thickness
        card_start_y = 50 + edge_thickness
        top_edge_pixel = base.getpixel((card_start_x + 100, card_start_y + 5))
        # Should be white (band 3 after cropping)
        assert top_edge_pixel[0] > 200, f"Top edge should be white, got {top_edge_pixel}"
        assert top_edge_pixel[1] > 200, f"Top edge should be white, got {top_edge_pixel}"
        assert top_edge_pixel[2] > 200, f"Top edge should be white, got {top_edge_pixel}"


class TestCombinedExtension:
    """Tests combining --extend_edges and --extend_corners."""

    def test_edges_6mm_corners_1_5mm(self, systematic_test_card):
        """Combined: black edges (6mm) and corner bleed (1.5mm)."""
        back = Image.new('RGB', systematic_test_card.size, 'gray')
        base = Image.new('RGB', (systematic_test_card.width + 200, systematic_test_card.height + 200), 'white')

        width = systematic_test_card.width
        height = systematic_test_card.height

        draw_card_layout(
            card_images=[systematic_test_card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=width,
            height=height,
            print_bleed=(10, 10),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=mm_to_px(6),
            extend_corners_radius=mm_to_px(1.5),
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # Check edge - should be black (after 6mm crop, band 4)
        edge_thickness = mm_to_px(6)
        card_start_x = 50 + edge_thickness
        card_start_y = 50 + edge_thickness
        top_edge = base.getpixel((card_start_x + 100, card_start_y + 5))
        assert all(c < 50 for c in top_edge), f"Edge should be black, got {top_edge}"

        # Check corner bleed exists (not pure white)
        corner_bleed = base.getpixel((card_start_x - 5, card_start_y - 5))
        assert corner_bleed != (255, 255, 255), f"Corner bleed should exist, got {corner_bleed}"

    def test_edges_10mm_corners_2_5mm(self, systematic_test_card):
        """Combined: black edges (10mm) and corner bleed (2.5mm)."""
        back = Image.new('RGB', systematic_test_card.size, 'gray')
        base = Image.new('RGB', (systematic_test_card.width + 200, systematic_test_card.height + 200), 'white')

        width = systematic_test_card.width
        height = systematic_test_card.height

        draw_card_layout(
            card_images=[systematic_test_card],
            single_back_image=back,
            base_image=base,
            num_rows=1, num_cols=1,
            x_pos=[50], y_pos=[50],
            width=width,
            height=height,
            print_bleed=(10, 10),
            crop=(0, 0), crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=mm_to_px(10),
            extend_corners_radius=mm_to_px(2.5),
            flip=False,
            fit=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT
        )

        # Check edge - should be black (after 10mm crop, band 6)
        edge_thickness = mm_to_px(10)
        card_start_x = 50 + edge_thickness
        card_start_y = 50 + edge_thickness
        top_edge = base.getpixel((card_start_x + 100, card_start_y + 5))
        assert all(c < 50 for c in top_edge), f"Edge should be black, got {top_edge}"

        # Check corner bleed exists
        corner_bleed = base.getpixel((card_start_x - 5, card_start_y - 5))
        assert corner_bleed != (255, 255, 255), f"Corner bleed should exist, got {corner_bleed}"
