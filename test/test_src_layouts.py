import pytest
import tempfile

import os
import json

from src import layouts # Allows assingment of EXTRA_LAYOUTS_PATH
from src.layouts import (
    EXTRA_LAYOUTS_ENV,
    extra_layout_paths,
    find_extra_layout_owner,
    merge_extra_layouts,
)

from pathlib import Path



class TestExtraLayoutPaths:
    """Tests for extra_layout_paths()."""

    def write_json(self, tmpdir: str, name: str, data=None):
        path = Path(tmpdir) / name
        with open(path, "w") as f:
            json.dump(data or {}, f)
        return path

    def test_empty_when_nothing_configured(self):
        os.environ.pop(EXTRA_LAYOUTS_ENV, None)
        original_dir = layouts.EXTRA_LAYOUTS_PATH
        layouts.EXTRA_LAYOUTS_PATH = Path(tempfile.gettempdir()) / "scm-test-nonexistent-dir"
        try:
            assert extra_layout_paths() == []
        finally:
            layouts.EXTRA_LAYOUTS_PATH = original_dir

    def test_dir_files_sorted_before_env_files(self):
        with (
            tempfile.TemporaryDirectory() as dir_tmpdir,
            tempfile.TemporaryDirectory() as env_tmpdir,
        ):
            b_path = self.write_json(dir_tmpdir, "b.json")
            a_path = self.write_json(dir_tmpdir, "a.json")
            env_path = self.write_json(env_tmpdir, "c.json")

            original_dir = layouts.EXTRA_LAYOUTS_PATH
            layouts.EXTRA_LAYOUTS_PATH = Path(dir_tmpdir)
            os.environ[EXTRA_LAYOUTS_ENV] = str(env_path)
            try:
                assert extra_layout_paths() == [a_path, b_path, env_path]
            finally:
                layouts.EXTRA_LAYOUTS_PATH = original_dir
                del os.environ[EXTRA_LAYOUTS_ENV]


class TestFindExtraLayoutOwner:
    """Tests for find_extra_layout_owner()."""

    def write_json(self, tmpdir, name, data):
        path = Path(tmpdir) / name
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def test_finds_defining_file_among_several(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mtg_path = self.write_json(
                tmpdir,
                "a-mtg.json",
                {
                    "card_sizes": {"mtg": {"width": "2.5in", "height": "3.5in"}},
                },
            )
            sorcery_path = self.write_json(
                tmpdir,
                "b-sorcery.json",
                {
                    "card_sizes": {"sorcery": {"width": "2.61in", "height": "3.74in"}},
                },
            )
            original_dir = layouts.EXTRA_LAYOUTS_PATH
            layouts.EXTRA_LAYOUTS_PATH = Path(tmpdir)
            try:
                assert find_extra_layout_owner("card_sizes", "sorcery") == sorcery_path
                assert find_extra_layout_owner("card_sizes", "mtg") == mtg_path
            finally:
                layouts.EXTRA_LAYOUTS_PATH = original_dir

    def test_returns_none_when_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json(
                tmpdir,
                "a.json",
                {
                    "card_sizes": {"mtg": {"width": "2.5in", "height": "3.5in"}},
                },
            )
            original_dir = layouts.EXTRA_LAYOUTS_PATH
            layouts.EXTRA_LAYOUTS_PATH = Path(tmpdir)
            try:
                assert find_extra_layout_owner("card_sizes", "nonexistent") is None
            finally:
                layouts.EXTRA_LAYOUTS_PATH = original_dir


class TestMergeExtraLayouts:
    """Tests for merge_extra_layouts()."""

    def base_config(self):
        return {
            "card_sizes": {"poker": {"width": "2.5in", "height": "3.5in"}},
            "paper_sizes": {"letter": {"width": "11in", "height": "8.5in"}},
            "layouts": {
                "letter": {
                    "poker": {"default": {"orientation": "landscape", "version": 1}}
                }
            },
        }

    def write_extra_file(self, tmpdir, name, data):
        path = Path(tmpdir) / name
        with open(path, "w") as f:
            json.dump(data, f)
        return str(path)

    def test_no_env_var_is_noop(self):
        os.environ.pop(EXTRA_LAYOUTS_ENV, None)
        config = self.base_config()
        result = merge_extra_layouts(config)
        assert result == self.base_config()

    def test_merges_new_card_size(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extra_path = self.write_extra_file(
                tmpdir,
                "extra.json",
                {
                    "card_sizes": {"mtg": {"width": "2.5in", "height": "3.5in"}},
                },
            )
            os.environ[EXTRA_LAYOUTS_ENV] = extra_path
            try:
                config = merge_extra_layouts(self.base_config())
                assert config["card_sizes"]["mtg"] == {
                    "width": "2.5in",
                    "height": "3.5in",
                }
                assert config["card_sizes"]["poker"] == {
                    "width": "2.5in",
                    "height": "3.5in",
                }
            finally:
                del os.environ[EXTRA_LAYOUTS_ENV]

    def test_merges_new_layout_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extra_path = self.write_extra_file(
                tmpdir,
                "extra.json",
                {
                    "layouts": {
                        "letter": {
                            "mtg": {
                                "default": {"orientation": "portrait", "version": 1}
                            }
                        }
                    },
                },
            )
            os.environ[EXTRA_LAYOUTS_ENV] = extra_path
            try:
                config = merge_extra_layouts(self.base_config())
                assert (
                    config["layouts"]["letter"]["mtg"]["default"]["orientation"]
                    == "portrait"
                )
                # Existing entry untouched
                assert (
                    config["layouts"]["letter"]["poker"]["default"]["orientation"]
                    == "landscape"
                )
            finally:
                del os.environ[EXTRA_LAYOUTS_ENV]

    def test_card_size_collision_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extra_path = self.write_extra_file(
                tmpdir,
                "extra.json",
                {
                    "card_sizes": {"poker": {"width": "1in", "height": "1in"}},
                },
            )
            os.environ[EXTRA_LAYOUTS_ENV] = extra_path
            try:
                with pytest.raises(ValueError):
                    merge_extra_layouts(self.base_config())
            finally:
                del os.environ[EXTRA_LAYOUTS_ENV]

    def test_layout_collision_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extra_path = self.write_extra_file(
                tmpdir,
                "extra.json",
                {
                    "layouts": {
                        "letter": {
                            "poker": {
                                "default": {"orientation": "portrait", "version": 1}
                            }
                        }
                    },
                },
            )
            os.environ[EXTRA_LAYOUTS_ENV] = extra_path
            try:
                with pytest.raises(ValueError):
                    merge_extra_layouts(self.base_config())
            finally:
                del os.environ[EXTRA_LAYOUTS_ENV]

    def test_multiple_files_merge_in_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path_a = self.write_extra_file(
                tmpdir,
                "a.json",
                {
                    "card_sizes": {"mtg": {"width": "2.5in", "height": "3.5in"}},
                },
            )
            path_b = self.write_extra_file(
                tmpdir,
                "b.json",
                {
                    "card_sizes": {"sorcery": {"width": "2.61in", "height": "3.74in"}},
                },
            )
            os.environ[EXTRA_LAYOUTS_ENV] = os.pathsep.join([path_a, path_b])
            try:
                config = merge_extra_layouts(self.base_config())
                assert "mtg" in config["card_sizes"]
                assert "sorcery" in config["card_sizes"]
            finally:
                del os.environ[EXTRA_LAYOUTS_ENV]

    def test_scans_extra_layouts_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_extra_file(
                tmpdir,
                "a.json",
                {
                    "card_sizes": {"mtg": {"width": "2.5in", "height": "3.5in"}},
                },
            )
            original_dir = layouts.EXTRA_LAYOUTS_PATH
            layouts.EXTRA_LAYOUTS_PATH = Path(tmpdir)
            try:
                config = merge_extra_layouts(self.base_config())
                assert config["card_sizes"]["mtg"] == {
                    "width": "2.5in",
                    "height": "3.5in",
                }
            finally:
                layouts.EXTRA_LAYOUTS_PATH = original_dir

    def test_missing_extra_layouts_dir_is_noop(self):
        os.environ.pop(EXTRA_LAYOUTS_ENV, None)
        original_dir = layouts.EXTRA_LAYOUTS_PATH
        layouts.EXTRA_LAYOUTS_PATH = Path(tempfile.gettempdir()) / "scm-test-nonexistent-dir"
        try:
            config = merge_extra_layouts(self.base_config())
            assert config == self.base_config()
        finally:
            layouts.EXTRA_LAYOUTS_PATH = original_dir

    def test_dir_file_collision_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_extra_file(
                tmpdir,
                "a.json",
                {
                    "card_sizes": {"poker": {"width": "1in", "height": "1in"}},
                },
            )
            original_dir = layouts.EXTRA_LAYOUTS_PATH
            layouts.EXTRA_LAYOUTS_PATH = Path(tmpdir)
            try:
                with pytest.raises(ValueError):
                    merge_extra_layouts(self.base_config())
            finally:
                layouts.EXTRA_LAYOUTS_PATH = original_dir

    def test_dir_files_merge_before_env_var_files(self):
        with (
            tempfile.TemporaryDirectory() as dir_tmpdir,
            tempfile.TemporaryDirectory() as env_tmpdir,
        ):
            self.write_extra_file(
                dir_tmpdir,
                "a.json",
                {
                    "card_sizes": {"mtg": {"width": "2.5in", "height": "3.5in"}},
                },
            )
            env_path = self.write_extra_file(
                env_tmpdir,
                "b.json",
                {
                    "card_sizes": {"sorcery": {"width": "2.61in", "height": "3.74in"}},
                },
            )
            original_dir = layouts.EXTRA_LAYOUTS_PATH
            layouts.EXTRA_LAYOUTS_PATH = Path(dir_tmpdir)
            os.environ[EXTRA_LAYOUTS_ENV] = env_path
            try:
                config = merge_extra_layouts(self.base_config())
                assert "mtg" in config["card_sizes"]
                assert "sorcery" in config["card_sizes"]
            finally:
                layouts.EXTRA_LAYOUTS_PATH = original_dir
                del os.environ[EXTRA_LAYOUTS_ENV]
