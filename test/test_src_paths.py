import pytest
import tempfile
import os

from pathlib import Path
from PIL import Image

from src.paths import (
    get_image_file_paths,
    check_paths_subset,
    delete_hidden_files_in_directory,
    get_directory,
    get_back_card_image_path,
    resolve_image_with_any_extension,
)


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
            img = Image.new("RGB", (100, 100), color="red")
            img_path = os.path.join(tmpdir, "test.png")
            img.save(img_path, "PNG")

            result = get_image_file_paths(tmpdir)
            assert "test.png" in result

    def test_finds_jpeg_files(self):
        """Should find JPEG files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (100, 100), color="blue")
            img_path = os.path.join(tmpdir, "test.jpg")
            img.save(img_path, "JPEG")

            result = get_image_file_paths(tmpdir)
            assert "test.jpg" in result

    def test_ignores_non_image_files(self):
        """Should ignore non-image files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a text file
            txt_path = os.path.join(tmpdir, "readme.txt")
            with open(txt_path, "w") as f:
                _ = f.write("hello")

            result = get_image_file_paths(tmpdir)
            assert "readme.txt" not in result

    def test_recursive_search(self):
        """Should find images in subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)

            img = Image.new("RGB", (100, 100), color="green")
            img_path = os.path.join(subdir, "nested.png")
            img.save(img_path, "PNG")

            result = get_image_file_paths(tmpdir)
            assert any("nested.png" in r for r in result)

    def test_returns_relative_paths(self):
        """Should return paths relative to input directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (100, 100), color="red")
            img_path = os.path.join(tmpdir, "test.png")
            img.save(img_path, "PNG")

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
        subset = {"card1.png", "card2.jpg"}
        mainset = {"card1.png", "card2.png", "card3.png"}
        result = check_paths_subset(subset, mainset)
        assert result == set()

    def test_missing_from_mainset(self):
        """Items not in mainset should be returned."""
        subset = {"card1.png", "card4.png"}
        mainset = {"card1.png", "card2.png", "card3.png"}
        result = check_paths_subset(subset, mainset)
        assert "card4.png" in result

    def test_ignores_extension(self):
        """Should match by stem, ignoring extension."""
        subset = {"card1.jpg"}
        mainset = {"card1.png"}
        result = check_paths_subset(subset, mainset)
        # card1.jpg should match card1.png by stem
        assert result == set()

    def test_different_extensions_match(self):
        """Different extensions with same stem should match."""
        subset = {"image.jpeg"}
        mainset = {"image.png", "other.png"}
        result = check_paths_subset(subset, mainset)
        assert result == set()

    def test_with_paths(self):
        """Should work with path-like strings."""
        subset = {"subdir/card1.png"}
        mainset = {"card1.png", "card2.png"}
        # stem of 'subdir/card1.png' is 'card1'
        result = check_paths_subset(subset, mainset)
        assert result == set()


class TestDeleteHiddenFilesInDirectory:
    """Tests for delete_hidden_files_in_directory() function."""

    def test_empty_path_does_nothing(self):
        """Empty path should not raise."""
        delete_hidden_files_in_directory(Path(""))

    def test_removes_ds_store(self):
        """Should remove .DS_Store files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ds_store = os.path.join(tmpdir, ".DS_Store")
            with open(ds_store, "w") as f:
                _ = f.write("junk")

            delete_hidden_files_in_directory(Path(tmpdir))
            assert not os.path.exists(ds_store)

    def test_removes_thumbs_db(self):
        """Should remove Thumbs.db files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            thumbs = os.path.join(tmpdir, "Thumbs.db")
            with open(thumbs, "w") as f:
                _ = f.write("junk")

            delete_hidden_files_in_directory(Path(tmpdir))
            assert not os.path.exists(thumbs)

    def test_removes_desktop_ini(self):
        """Should remove desktop.ini files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            desktop_ini = os.path.join(tmpdir, "desktop.ini")
            with open(desktop_ini, "w") as f:
                _ = f.write("junk")

            delete_hidden_files_in_directory(Path(tmpdir))
            assert not os.path.exists(desktop_ini)

    def test_removes_apple_double_files(self):
        """Should remove Apple double files (._prefix)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            apple_double = os.path.join(tmpdir, "._image.png")
            with open(apple_double, "w") as f:
                _ = f.write("junk")

            delete_hidden_files_in_directory(Path(tmpdir))
            assert not os.path.exists(apple_double)

    def test_preserves_normal_files(self):
        """Should not remove normal files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            normal_file = os.path.join(tmpdir, "image.png")
            with open(normal_file, "w") as f:
                _ = f.write("data")

            delete_hidden_files_in_directory(Path(tmpdir))
            assert os.path.exists(normal_file)


class TestGetDirectory:
    """Tests for get_directory() function."""

    def test_directory_path(self):
        """Directory path should return absolute directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_directory(Path(tmpdir))
            assert result == Path(tmpdir).resolve()

    def test_file_path(self):
        """File path should return absolute parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            with open(file_path, "w") as f:
                _ = f.write("test")

            result = get_directory(Path(file_path))
            assert result == Path(tmpdir).resolve()


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
            txt_path = os.path.join(tmpdir, "readme.txt")
            with open(txt_path, "w") as f:
                f.write("not an image")

            result = get_back_card_image_path(tmpdir)
            assert result is None

    def test_single_image_returns_path(self):
        """Directory with one image should return that image's path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (100, 100), color="red")
            img_path = os.path.join(tmpdir, "back.png")
            img.save(img_path, "PNG")

            result = get_back_card_image_path(tmpdir)
            assert result is not None
            assert str(result).endswith("back.png")


class TestResolveImageWithAnyExtension:
    """Tests for resolve_image_with_any_extension() function."""

    def test_exact_path_exists(self):
        """Should return exact path if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (100, 100), color="red")
            img_path = os.path.join(tmpdir, "test.png")
            img.save(img_path, "PNG")

            result = resolve_image_with_any_extension(img_path)
            assert result == img_path

    def test_finds_different_extension(self):
        """Should find file with different extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (100, 100), color="red")
            img_path = os.path.join(tmpdir, "test.jpg")
            img.save(img_path, "JPEG")

            # Request .png but .jpg exists
            query_path = os.path.join(tmpdir, "test.png")
            result = resolve_image_with_any_extension(query_path)
            assert result == img_path

    def test_missing_file_raises(self):
        """Should raise FileNotFoundError if no match found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            query_path = os.path.join(tmpdir, "nonexistent.png")
            with pytest.raises(FileNotFoundError, match="Missing image"):
                _ = resolve_image_with_any_extension(query_path)

    def test_ambiguous_match_raises(self):
        """Should raise ValueError if multiple matches found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two files with same stem but different extensions
            img = Image.new("RGB", (100, 100), color="red")
            img.save(os.path.join(tmpdir, "test.png"), "PNG")
            img.save(os.path.join(tmpdir, "test.jpg"), "JPEG")

            # Request a non-existent extension to trigger glob search
            query_path = os.path.join(tmpdir, "test.gif")
            with pytest.raises(ValueError, match="Ambiguous"):
                _ = resolve_image_with_any_extension(query_path)
