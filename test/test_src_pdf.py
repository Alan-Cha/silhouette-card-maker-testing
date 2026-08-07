import pytest

from src.pdf import (
    add_front_back_pages,
    generate_pdf,
)
from src.enums import Orientation

from PIL import Image


class TestAddFrontBackPages:
    """Tests for add_front_back_pages() function."""

    def test_appends_front_and_back(self):
        """With only_fronts=False, should append both front and back pages.

        pages[] -> [front, back]
        """
        front = Image.new("RGB", (300, 400), color="white")
        back = Image.new("RGB", (300, 400), color="white")
        pages = []

        add_front_back_pages(
            front,
            back,
            pages,
            page_width=300,
            page_height=400,
            ppi_ratio=1.0,
            template="test_v1",
            only_fronts=False,
            label=None,
            orientation=Orientation.LANDSCAPE,
            label_margin_px=10,
        )
        assert len(pages) == 2
        assert pages[0].size == front.size
        assert pages[1].size == back.size

    def test_only_fronts_appends_one(self):
        """With only_fronts=True, should append only the front page.

        pages[] -> [front]
        """
        front = Image.new("RGB", (300, 400), color="white")
        back = Image.new("RGB", (300, 400), color="white")
        pages = []

        add_front_back_pages(
            front,
            back,
            pages,
            page_width=300,
            page_height=400,
            ppi_ratio=1.0,
            template="test_v1",
            only_fronts=True,
            label=None,
            orientation=Orientation.LANDSCAPE,
            label_margin_px=10,
        )
        assert len(pages) == 1
        assert pages[0].size == front.size

    def test_sheet_numbering_increments(self):
        """Sheet number should increment based on existing pages list size.

        Call 1: pages[] -> [front1, back1]
        Call 2: pages[] -> [front1, back1, front2, back2]
        """
        front1 = Image.new("RGB", (300, 400), color="white")
        back1 = Image.new("RGB", (300, 400), color="white")
        front2 = Image.new("RGB", (300, 400), color="white")
        back2 = Image.new("RGB", (300, 400), color="white")
        pages = []

        add_front_back_pages(
            front1,
            back1,
            pages,
            page_width=300,
            page_height=400,
            ppi_ratio=1.0,
            template="test_v1",
            only_fronts=False,
            label=None,
            orientation=Orientation.PORTRAIT,
            label_margin_px=10,
        )
        add_front_back_pages(
            front2,
            back2,
            pages,
            page_width=300,
            page_height=400,
            ppi_ratio=1.0,
            template="test_v1",
            only_fronts=False,
            label=None,
            orientation=Orientation.PORTRAIT,
            label_margin_px=10,
        )
        assert len(pages) == 4

    def test_name_label(self):
        """Providing a name should not raise (label includes name).

        pages[] -> [front, back]  (with name='my_deck')
        """
        front = Image.new("RGB", (300, 400), color="white")
        back = Image.new("RGB", (300, 400), color="white")
        pages = []

        add_front_back_pages(
            front,
            back,
            pages,
            page_width=300,
            page_height=400,
            ppi_ratio=1.0,
            template="test_v1",
            only_fronts=False,
            label="my_deck",
            orientation=Orientation.PORTRAIT,
            label_margin_px=10,
        )
        assert len(pages) == 2
