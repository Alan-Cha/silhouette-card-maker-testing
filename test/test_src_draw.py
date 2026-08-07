from src.draw import (
    draw_card_layout,
    draw_card_with_bleed,
)
from src.enums import Orientation, FitMode
from PIL import Image


class TestDrawCardWithBleed:
    """Tests for draw_card_with_bleed() function."""

    RED: tuple[int, int, int] = (255, 0, 0)
    WHITE: tuple[int, int, int] = (255, 255, 255)

    def test_card_placed_at_position(self):
        """Card should be pasted at the specified position.

            10        15        24       29
        10  +-------- +-------- +--------+
            | corner  | top     | corner |
        15  +-------- CCCCCCCCCC --------+
            | left    | card    | right  |
        24  +-------- CCCCCCCCCC --------+
            | corner  | bottom  | corner |
        29  +-------- +-------- +--------+

        C = card area, surrounding = bleed, outside = empty
        """
        card = Image.new("RGB", (10, 10), color="red")
        base = Image.new("RGB", (40, 40), color="white")
        _ = draw_card_with_bleed(card, base, 15, 15, (5, 5))
        # Card area
        assert base.getpixel((15, 15)) == self.RED
        assert base.getpixel((24, 24)) == self.RED
        # Empty space (outside card and bleed)
        assert base.getpixel((0, 0)) == self.WHITE
        assert base.getpixel((39, 39)) == self.WHITE

    def test_edge_bleed_extends(self):
        """Edge bleed should extend the card's border pixels outward.

            10        15        24       29
        10  +-------- +-------- +--------+
            | corner  |*top*    | corner |
        15  +-------- CCCCCCCCCC --------+
            |*left*   | card    |*right* |
        24  +-------- CCCCCCCCCC --------+
            | corner  |*bottom* | corner |
        29  +-------- +-------- +--------+

        *edge* = edge bleed regions checked in this test
        Pixels at x/y = 9 and 30 (just outside) should be empty.
        """
        card = Image.new("RGB", (10, 10), color="red")
        base = Image.new("RGB", (40, 40), color="white")
        _ = draw_card_with_bleed(card, base, 15, 15, (5, 5))
        # Top bleed: top row extended upward
        assert base.getpixel((15, 14)) == self.RED
        assert base.getpixel((15, 10)) == self.RED
        # Left bleed: left column extended leftward
        assert base.getpixel((14, 15)) == self.RED
        assert base.getpixel((10, 15)) == self.RED
        # Bottom bleed
        assert base.getpixel((15, 25)) == self.RED
        assert base.getpixel((15, 29)) == self.RED
        # Right bleed
        assert base.getpixel((25, 15)) == self.RED
        assert base.getpixel((29, 15)) == self.RED
        # Beyond bleed should remain empty
        assert base.getpixel((15, 9)) == self.WHITE
        assert base.getpixel((9, 15)) == self.WHITE
        assert base.getpixel((15, 30)) == self.WHITE
        assert base.getpixel((30, 15)) == self.WHITE

    def test_corner_bleed_fills(self):
        """Corner bleed regions should be filled with corner pixel color.

            10        15        24       29
        10  *TL*      +-------- +      *TR*
            |         | top     |        |
        15  +-------- CCCCCCCCCC --------+
            | left    | card    | right  |
        24  +-------- CCCCCCCCCC --------+
            |         | bottom  |        |
        29  *BL*      +-------- +      *BR*

        *XX* = corner bleed regions checked in this test
        Pixels at x/y = 9 and 30 (just outside) should be empty.
        """
        card = Image.new("RGB", (10, 10), color="red")
        base = Image.new("RGB", (40, 40), color="white")
        _ = draw_card_with_bleed(card, base, 15, 15, (5, 5))
        # Top-left corner bleed region
        assert base.getpixel((10, 10)) == self.RED
        assert base.getpixel((14, 14)) == self.RED
        # Top-right corner bleed region
        assert base.getpixel((25, 10)) == self.RED
        assert base.getpixel((29, 14)) == self.RED
        # Bottom-left corner bleed region
        assert base.getpixel((10, 25)) == self.RED
        assert base.getpixel((14, 29)) == self.RED
        # Bottom-right corner bleed region
        assert base.getpixel((25, 25)) == self.RED
        assert base.getpixel((29, 29)) == self.RED
        # Outside corner bleed should remain empty
        assert base.getpixel((9, 9)) == self.WHITE
        assert base.getpixel((30, 9)) == self.WHITE
        assert base.getpixel((9, 30)) == self.WHITE
        assert base.getpixel((30, 30)) == self.WHITE

    def test_zero_bleed(self):
        """Zero bleed should just place the card with no bleed extension.

        15       24
        CCCCCCCCCC
        C  card  C
        CCCCCCCCCC

        No bleed regions — pixels at x=14, x=25, y=14, y=25
        should all be empty.
        """
        card = Image.new("RGB", (10, 10), color="red")
        base = Image.new("RGB", (40, 40), color="white")
        _ = draw_card_with_bleed(card, base, 15, 15, (0, 0))
        # Card area
        assert base.getpixel((15, 15)) == self.RED
        assert base.getpixel((24, 24)) == self.RED
        # Adjacent pixels outside card should remain empty (no bleed)
        assert base.getpixel((14, 15)) == self.WHITE
        assert base.getpixel((15, 14)) == self.WHITE
        assert base.getpixel((25, 15)) == self.WHITE
        assert base.getpixel((15, 25)) == self.WHITE


class TestDrawCardLayout:
    """Tests for draw_card_layout() function."""

    RED: tuple[int, int, int] = (255, 0, 0)
    BLUE: tuple[int, int, int] = (0, 0, 255)
    GREEN: tuple[int, int, int] = (0, 128, 0)
    YELLOW: tuple[int, int, int] = (255, 255, 0)
    WHITE: tuple[int, int, int] = (255, 255, 255)

    def test_single_card_placed(self):
        """Single card in 1x1 layout should be placed at the layout position.

         Base 300x400, card 100x140 at (50,50):

            0    50       149         299
         0  +----+--------+-----------+
            |    |        |           |
         50 | .. RRRRRRRRRR ......... |
            |    R  card  R   empty   |
        189 | .. RRRRRRRRRR ......... |
            |    |        |           |
        399 +----+--------+-----------+

         R = red card, . = empty (white)
        """
        card = Image.new("RGB", (100, 140), color="red")
        back = Image.new("RGB", (100, 140), color="blue")
        base = Image.new("RGB", (300, 400), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=140,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        assert base.getpixel((50, 50)) == self.RED
        assert base.getpixel((100, 100)) == self.RED
        # Outside card area should remain white
        assert base.getpixel((0, 0)) == (255, 255, 255)

    def test_none_card_skipped(self):
        """None entries in card list should leave base image unchanged.

        Base 300x400, card_images=[None]:

        0                          299
        +==========================+
        |                          |
        |    entirely empty        |
        |    (no card drawn)       |
        |                          |
        +==========================+
        """
        back = Image.new("RGB", (100, 140), color="blue")
        base = Image.new("RGB", (300, 400), color="white")
        original_data = list(base.tobytes())

        draw_card_layout(
            card_images=[None],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=140,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        assert list(base.tobytes()) == original_data

    def test_flip_reverses_row_order(self):
        """Flip should place first card at bottom row and second at top.

        Base 300x500, 2 rows x 1 col, flip=True:

        Normal order:        Flipped order:

          50  +--------+       50  +--------+
              | red    |           | blue   |
         189  +--------+      189  +--------+
              |        |           |        |
         250  +--------+      250  +--------+
              | blue   |           | red    |
         389  +--------+      389  +--------+
        """
        red_card = Image.new("RGB", (100, 140), color="red")
        blue_card = Image.new("RGB", (100, 140), color="blue")
        back = Image.new("RGB", (100, 140), color="green")
        base = Image.new("RGB", (300, 500), color="white")

        draw_card_layout(
            card_images=[red_card, blue_card],
            single_back_image=back,
            base_image=base,
            num_rows=2,
            num_cols=1,
            x_pos=[50],
            y_pos=[50, 250],
            width=100,
            height=140,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=True,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.LANDSCAPE,
        )
        # With flip: card 0 (red) goes to row 1 (y=250), card 1 (blue) to row 0 (y=50)
        # Images are rotated 180 degrees, but still the same color
        assert base.getpixel((50, 250)) == self.RED
        assert base.getpixel((50, 50)) == self.BLUE

    def test_multi_card_grid(self):
        """2x2 grid should place 4 cards at the correct positions.

         Base 300x400, 2x2 grid:

            10       109  150      249
         10 RRRRRRRRRR    BBBBBBBBBB
            R card0  R    B card1  B
        149 RRRRRRRRRR    BBBBBBBBBB

        200 GGGGGGGGGG    YYYYYYYYYY
            G card2  G    Y card3  Y
        339 GGGGGGGGGG    YYYYYYYYYY

         R=red, B=blue, G=green, Y=yellow
        """
        cards = [
            Image.new("RGB", (100, 140), color="red"),
            Image.new("RGB", (100, 140), color="blue"),
            Image.new("RGB", (100, 140), color="green"),
            Image.new("RGB", (100, 140), color="yellow"),
        ]
        back = Image.new("RGB", (100, 140), color="gray")
        base = Image.new("RGB", (300, 400), color="white")

        draw_card_layout(
            card_images=cards,
            single_back_image=back,
            base_image=base,
            num_rows=2,
            num_cols=2,
            x_pos=[10, 150],
            y_pos=[10, 200],
            width=100,
            height=140,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Card 0 (red) at top-left
        assert base.getpixel((10, 10)) == self.RED
        assert base.getpixel((109, 149)) == self.RED
        # Card 1 (blue) at top-right
        assert base.getpixel((150, 10)) == self.BLUE
        assert base.getpixel((249, 149)) == self.BLUE
        # Card 2 (green) at bottom-left
        assert base.getpixel((10, 200)) == self.GREEN
        assert base.getpixel((109, 339)) == self.GREEN
        # Card 3 (yellow) at bottom-right
        assert base.getpixel((150, 200)) == self.YELLOW
        assert base.getpixel((249, 339)) == self.YELLOW
        # Empty space between cards
        assert base.getpixel((130, 10)) == self.WHITE
        assert base.getpixel((10, 170)) == self.WHITE

    def test_print_bleed_extends_around_card(self):
        """Print bleed should add colored border around the card.

        Card 10x10 at (15,15), bleed 5px:

            10        15        24       29
        10  +-------- +-------- +--------+
            | corner  | top     | corner |
        15  +-------- CCCCCCCCCC --------+
            | left    | card    | right  |
        24  +-------- CCCCCCCCCC --------+
            | corner  | bottom  | corner |
        29  +-------- +-------- +--------+

        C = card, surrounding = bleed, outside = empty
        """
        card = Image.new("RGB", (10, 10), color="red")
        back = Image.new("RGB", (10, 10), color="blue")
        base = Image.new("RGB", (40, 40), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[15],
            y_pos=[15],
            width=10,
            height=10,
            print_bleed=(5, 5),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Card area
        assert base.getpixel((15, 15)) == self.RED
        assert base.getpixel((24, 24)) == self.RED
        # Bleed area
        assert base.getpixel((15, 10)) == self.RED
        assert base.getpixel((10, 15)) == self.RED
        assert base.getpixel((15, 29)) == self.RED
        assert base.getpixel((29, 15)) == self.RED
        # Corner bleed
        assert base.getpixel((10, 10)) == self.RED
        assert base.getpixel((29, 29)) == self.RED
        # Empty space beyond bleed
        assert base.getpixel((9, 15)) == self.WHITE
        assert base.getpixel((15, 9)) == self.WHITE
        assert base.getpixel((30, 15)) == self.WHITE
        assert base.getpixel((15, 30)) == self.WHITE

    def test_ppi_ratio_scales_positions_and_size(self):
        """ppi_ratio=2.0 should double all positions and sizes.

        Card 10x10 at pos (10,10), ppi_ratio=2.0:
        Scaled position = (20,20), scaled size = 20x20.

           20       39
        20 CCCCCCCCCC
           C  card  C
        39 CCCCCCCCCC

        Everything is doubled from the unscaled values.
        """
        card = Image.new("RGB", (10, 10), color="red")
        back = Image.new("RGB", (10, 10), color="blue")
        base = Image.new("RGB", (80, 80), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[10],
            y_pos=[10],
            width=10,
            height=10,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=2.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Card at scaled position (20,20) with scaled size 20x20
        assert base.getpixel((20, 20)) == self.RED
        assert base.getpixel((39, 39)) == self.RED
        # Just outside the card should be empty
        assert base.getpixel((19, 20)) == self.WHITE
        assert base.getpixel((20, 19)) == self.WHITE
        assert base.getpixel((40, 20)) == self.WHITE
        assert base.getpixel((20, 40)) == self.WHITE

    def test_crop_trims_front_card_edges(self):
        """crop=(50, 50) should crop 50% off the card before scaling.

        Card 200x200 with blue 50px border, red 100x100 center:

        BBBBBBBBBBBBBBBBBBBB        After 50% crop,
        BB                BB        only center red
        BB   RRRRRRRRRR   BB   ->   region remains,
        BB   R center R   BB        stretched to fit.
        BB   RRRRRRRRRR   BB
        BB                BB
        BBBBBBBBBBBBBBBBBBBB

        Result: card area should be red (center survived crop).
        """
        card = Image.new("RGB", (200, 200), color="blue")
        # Paint red center (50,50)-(149,149)
        for x in range(50, 150):
            for y in range(50, 150):
                card.putpixel((x, y), (255, 0, 0))
        back = Image.new("RGB", (200, 200), color="gray")
        base = Image.new("RGB", (200, 200), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=100,
            print_bleed=(0, 0),
            crop=(50, 50),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Card area should be red (cropped to center, then stretched)
        assert base.getpixel((50, 50)) == self.RED
        assert base.getpixel((100, 100)) == self.RED
        assert base.getpixel((149, 149)) == self.RED
        # Outside card should be empty
        assert base.getpixel((49, 50)) == self.WHITE
        assert base.getpixel((150, 50)) == self.WHITE

    def test_crop_backs_applies_to_back_image(self):
        """crop_backs should be used instead of crop when card is the back.

        Back 200x200 with green 50px border, red 100x100 center.
        crop=(0,0), crop_backs=(50,50).

        Since card `is` single_back_image, crop_backs is used.
        Result: card area should be red (center survived crop).
        """
        back = Image.new("RGB", (200, 200), color="green")
        for x in range(50, 150):
            for y in range(50, 150):
                back.putpixel((x, y), self.RED)
        base = Image.new("RGB", (200, 200), color="white")

        draw_card_layout(
            card_images=[back],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=100,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(50, 50),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Card area should be red (crop_backs applied to center)
        assert base.getpixel((50, 50)) == self.RED
        assert base.getpixel((100, 100)) == self.RED
        assert base.getpixel((149, 149)) == self.RED
        # Outside card should be empty
        assert base.getpixel((49, 50)) == self.WHITE

    def test_fit_stretch_keeps_wide_card_edges(self):
        """STRETCH squishes a wide card, keeping left/right edge colors.

        Card 200x100: blue 20px left, green 20px right, red center.
        Target 100x100. STRETCH compresses full width into target.

        Resized: 10px blue | 80px red | 10px green

          50  59 60           139 140 149
          BBBBBBBBRRRRRRRRRRRRRGGGGGGGG
          B blue B     red    G green G
          BBBBBBBBRRRRRRRRRRRRRGGGGGGGG
        """
        card = Image.new("RGB", (200, 100), color="red")
        for x in range(20):
            for y in range(100):
                card.putpixel((x, y), self.BLUE)
        for x in range(180, 200):
            for y in range(100):
                card.putpixel((x, y), self.GREEN)
        back = Image.new("RGB", (200, 100), color="gray")
        base = Image.new("RGB", (200, 200), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=100,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Left edge should be blue (stretched but preserved)
        assert base.getpixel((50, 80)) == self.BLUE
        # Right edge should be green
        assert base.getpixel((149, 80)) == self.GREEN
        # Center should be red
        assert base.getpixel((100, 80)) == self.RED

    def test_fit_crop_removes_wide_card_edges(self):
        """CROP on a wide card center-crops, removing left/right edges.

        Card 200x100: blue 20px left, green 20px right, red center.
        Target 100x100. CROP center-crops 50px from each side.

        Cropped region is x=50..149 of original, all red.

          50       149
          RRRRRRRRRR
          R   red  R
          RRRRRRRRRR
        """
        card = Image.new("RGB", (200, 100), color="red")
        for x in range(20):
            for y in range(100):
                card.putpixel((x, y), self.BLUE)
        for x in range(180, 200):
            for y in range(100):
                card.putpixel((x, y), (0, 128, 0))
        back = Image.new("RGB", (200, 100), color="gray")
        base = Image.new("RGB", (200, 200), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=100,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.CROP,
            fit_backs=FitMode.CROP,
            orientation=Orientation.PORTRAIT,
        )
        # All edges should be red (blue/green sides were cropped off)
        assert base.getpixel((50, 80)) == self.RED
        assert base.getpixel((149, 80)) == self.RED
        assert base.getpixel((100, 80)) == self.RED
        # Outside card should be empty
        assert base.getpixel((49, 80)) == self.WHITE

    def test_fit_stretch_keeps_tall_card_edges(self):
        """STRETCH squishes a tall card, keeping top/bottom edge colors.

         Card 100x200: blue 20px top, green 20px bottom, red center.
         Target 100x100. STRETCH compresses full height into target.

         Resized: 10px blue / 80px red / 10px green

           50         149
         50 BBBBBBBBBBB
         59 BBBBBBBBBBB
         60 RRRRRRRRRRR
            R   red   R
        139 RRRRRRRRRRR
        140 GGGGGGGGGGG
        149 GGGGGGGGGGG
        """
        card = Image.new("RGB", (100, 200), color="red")
        for x in range(100):
            for y in range(20):
                card.putpixel((x, y), self.BLUE)
        for x in range(100):
            for y in range(180, 200):
                card.putpixel((x, y), self.GREEN)
        back = Image.new("RGB", (100, 200), color="gray")
        base = Image.new("RGB", (200, 200), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=100,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Top edge should be blue (stretched but preserved)
        assert base.getpixel((80, 50)) == self.BLUE
        # Bottom edge should be green
        assert base.getpixel((80, 149)) == self.GREEN
        # Center should be red
        assert base.getpixel((80, 100)) == self.RED

    def test_fit_crop_removes_tall_card_edges(self):
        """CROP on a tall card center-crops, removing top/bottom edges.

         Card 100x200: blue 20px top, green 20px bottom, red center.
         Target 100x100. CROP center-crops 50px from top and bottom.

         Cropped region is y=50..149 of original, all red.

           50         149
         50 RRRRRRRRRRR
            R   red   R
        149 RRRRRRRRRRR
        """
        card = Image.new("RGB", (100, 200), color="red")
        for x in range(100):
            for y in range(20):
                card.putpixel((x, y), self.BLUE)
        for x in range(100):
            for y in range(180, 200):
                card.putpixel((x, y), self.GREEN)
        back = Image.new("RGB", (100, 200), color="gray")
        base = Image.new("RGB", (200, 200), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=100,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.CROP,
            fit_backs=FitMode.CROP,
            orientation=Orientation.PORTRAIT,
        )
        # All edges should be red (blue/green sides were cropped off)
        assert base.getpixel((80, 50)) == self.RED
        assert base.getpixel((80, 149)) == self.RED
        assert base.getpixel((80, 100)) == self.RED
        # Outside card should be empty
        assert base.getpixel((80, 49)) == self.WHITE

    def test_extend_edges_zero_keeps_border(self):
        """Without extend_edges, the card's blue border is visible.

        Card 30x30: blue 10px border, red 10x10 center.
        Target 30x30 at (15,15), extend_edges=0.

        15                44
        BBBBBBBBBBBBBBBBBBBB
        BB                BB
        BB  RRRRRRRRRRRR  BB
        BB  R  center  R  BB
        BB  RRRRRRRRRRRR  BB
        BB                BB
        BBBBBBBBBBBBBBBBBBBB

        Edges of placed card should be blue.
        """
        card = Image.new("RGB", (30, 30), color="blue")
        for x in range(10, 20):
            for y in range(10, 20):
                card.putpixel((x, y), (255, 0, 0))
        back = Image.new("RGB", (30, 30), color="gray")
        base = Image.new("RGB", (60, 60), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[15],
            y_pos=[15],
            width=30,
            height=30,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Edges of card should be blue (border preserved)
        assert base.getpixel((15, 15)) == self.BLUE
        assert base.getpixel((44, 15)) == self.BLUE
        assert base.getpixel((15, 44)) == self.BLUE
        assert base.getpixel((44, 44)) == self.BLUE
        # Center should be red
        assert base.getpixel((25, 25)) == self.RED

    def test_extend_edges_removes_border(self):
        """With extend_edges, the card's blue border is trimmed away.

        Card 30x30: blue 10px border, red 10x10 center.
        Target 30x30 at (15,15), extend_edges=10.
        Crops 10px from each edge -> 10x10 red card remains.
        Placed at (25,25) with 10px bleed of red around it.

            15        25      34       44
        15  +-------- +------ +--------+
            | bleed   | bleed | bleed  |
        25  +--------- RRRRRRR --------+
            | bleed   | card  | bleed  |
        34  +--------- RRRRRRR --------+
            | bleed   | bleed | bleed  |
        44  +-------- +------ +--------+

        Edges should now be red (blue border was trimmed).
        """
        card = Image.new("RGB", (30, 30), color="blue")
        for x in range(10, 20):
            for y in range(10, 20):
                card.putpixel((x, y), (255, 0, 0))
        back = Image.new("RGB", (30, 30), color="gray")
        base = Image.new("RGB", (60, 60), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[15],
            y_pos=[15],
            width=30,
            height=30,
            print_bleed=(0, 0),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=10,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )
        # Card area (25,25)-(34,34) should be red (border trimmed)
        assert base.getpixel((25, 25)) == self.RED
        assert base.getpixel((34, 34)) == self.RED
        # Bleed area should also be red (extended from red edges)
        assert base.getpixel((15, 25)) == self.RED
        assert base.getpixel((25, 15)) == self.RED
        assert base.getpixel((44, 25)) == self.RED
        assert base.getpixel((25, 44)) == self.RED
        # No blue should be visible anywhere in the card+bleed area
        assert base.getpixel((15, 15)) == self.RED
        assert base.getpixel((44, 44)) == self.RED
        # Outside bleed should be empty
        assert base.getpixel((14, 25)) == self.WHITE
        assert base.getpixel((25, 14)) == self.WHITE

    def test_extend_bleed_outer_edges_extended(self):
        """Outer edges of cards in a 2x2 grid should get extended bleed.

        Normal bleed: 5px, extended: 10px, total outer bleed: 15px
        - Top row: extended top edge (y=5 to y=19)
        - Bottom row: extended bottom edge (y=340 to y=354)
        - Left column: extended left edge (x=0 to x=9, clamped from x=-5)
        - Right column: extended right edge (x=250 to x=264)
        """
        red_card = Image.new("RGB", (100, 140), color="red")
        blue_card = Image.new("RGB", (100, 140), color="blue")
        green_card = Image.new("RGB", (100, 140), color="green")
        yellow_card = Image.new("RGB", (100, 140), color="yellow")
        back = Image.new("RGB", (100, 140), color="gray")
        base = Image.new("RGB", (300, 400), color="white")

        draw_card_layout(
            card_images=[red_card, blue_card, green_card, yellow_card],
            single_back_image=back,
            base_image=base,
            num_rows=2,
            num_cols=2,
            x_pos=[10, 150],
            y_pos=[20, 200],
            width=100,
            height=140,
            print_bleed=(5, 5),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=10,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )

        # Top-left card (red): extended top and left
        assert base.getpixel((10, 5)) == self.RED  # Extended top bleed start
        assert base.getpixel((10, 19)) == self.RED  # Extended top bleed end
        assert (
            base.getpixel((0, 20)) == self.RED
        )  # Extended left bleed (clamped from x=-5)

        # Top-right card (blue): extended top and right
        assert base.getpixel((150, 5)) == self.BLUE  # Extended top bleed start
        assert base.getpixel((150, 19)) == self.BLUE  # Extended top bleed end
        assert (
            base.getpixel((264, 20)) == self.BLUE
        )  # Extended right bleed end (x=250+14)

        # Bottom-left card (green): extended bottom and left
        assert (
            base.getpixel((10, 354)) == self.GREEN
        )  # Extended bottom bleed end (y=340+14)
        assert base.getpixel((10, 355)) == self.WHITE  # Outside extended bleed
        assert base.getpixel((0, 200)) == self.GREEN  # Extended left bleed (clamped)

        # Bottom-right card (yellow): extended bottom and right
        assert base.getpixel((150, 354)) == self.YELLOW  # Extended bottom bleed end
        assert base.getpixel((150, 355)) == self.WHITE  # Outside extended bleed
        assert base.getpixel((264, 200)) == self.YELLOW  # Extended right bleed end

    def test_extend_bleed_zero_no_extra_bleed(self):
        """extend_bleed=0 should behave the same as not having the feature."""
        card = Image.new("RGB", (100, 140), color="red")
        back = Image.new("RGB", (100, 140), color="blue")
        base = Image.new("RGB", (300, 400), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=140,
            print_bleed=(10, 10),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=0,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )

        # Card at (50, 50), size 100x140, normal bleed 10px
        # Top bleed: 10 pixels from y=(50-10)=40 to y=49
        assert base.getpixel((50, 40)) == self.RED  # Normal top bleed
        assert base.getpixel((50, 39)) == self.WHITE  # Outside bleed

        # Bottom bleed: card ends at y=190, 10 pixels from y=190 to y=199
        assert base.getpixel((50, 199)) == self.RED  # Normal bottom bleed
        assert base.getpixel((50, 200)) == self.WHITE  # Outside bleed

    def test_extend_bleed_center_cards_no_extra(self):
        """Center cards in a 3x3 grid should not get extended bleed."""
        cards = [Image.new("RGB", (50, 70), color="red") for _ in range(9)]
        cards[4] = Image.new("RGB", (50, 70), color="blue")  # Center card
        back = Image.new("RGB", (50, 70), color="gray")
        base = Image.new("RGB", (300, 400), color="white")

        draw_card_layout(
            card_images=cards,
            single_back_image=back,
            base_image=base,
            num_rows=3,
            num_cols=3,
            x_pos=[10, 80, 150],
            y_pos=[10, 100, 190],
            width=50,
            height=70,
            print_bleed=(5, 5),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=10,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )

        # Center card (blue) is at row=1, col=1, position (80, 100)
        # Should only have normal 5px bleed on all sides (no extended bleed)
        # Top bleed: 5 pixels from y=(100-5)=95 to y=99
        assert base.getpixel((80, 95)) == self.BLUE  # Normal top bleed
        assert base.getpixel((80, 94)) == self.WHITE  # No extended bleed

        # Bottom bleed: card ends at y=170, 5 pixels from y=170 to y=174
        assert base.getpixel((80, 174)) == self.BLUE  # Normal bottom bleed
        assert base.getpixel((80, 175)) == self.WHITE  # No extended bleed

    def test_extend_bleed_single_card_all_edges_extended(self):
        """A single card (1x1 grid) should get extended bleed on all four edges."""
        card = Image.new("RGB", (100, 140), color="red")
        back = Image.new("RGB", (100, 140), color="blue")
        base = Image.new("RGB", (300, 400), color="white")

        draw_card_layout(
            card_images=[card],
            single_back_image=back,
            base_image=base,
            num_rows=1,
            num_cols=1,
            x_pos=[50],
            y_pos=[50],
            width=100,
            height=140,
            print_bleed=(5, 5),
            crop=(0, 0),
            crop_backs=(0, 0),
            ppi_ratio=1.0,
            extend_edges=0,
            extend_edges_backs=0,
            extend_corners_radius=0,
            extend_corners_backs_radius=0,
            extend_bleed=10,
            flip=False,
            fit=FitMode.STRETCH,
            fit_backs=FitMode.STRETCH,
            orientation=Orientation.PORTRAIT,
        )

        # Single card is both first and last row/col, so all edges extended
        # Card at (50, 50), size 100x140
        # Normal bleed: 5px, extended: 10px, total: 15px

        # Top: extends 15 pixels from y=(50-15)=35 to y=49 (range 0-14)
        assert base.getpixel((50, 35)) == self.RED
        assert base.getpixel((50, 34)) == self.WHITE

        # Bottom: card ends at y=190, extends 15 pixels from y=190 to y=204
        assert base.getpixel((50, 204)) == self.RED
        assert base.getpixel((50, 205)) == self.WHITE

        # Left: extends 15 pixels from x=(50-15)=35 to x=49
        assert base.getpixel((35, 50)) == self.RED
        assert base.getpixel((34, 50)) == self.WHITE

        # Right: card ends at x=150, extends 15 pixels from x=150 to x=164
        assert base.getpixel((164, 50)) == self.RED
        assert base.getpixel((165, 50)) == self.WHITE
