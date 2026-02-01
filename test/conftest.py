"""
Pytest configuration and shared fixtures for plugin tests.
"""
import os
import shutil
import tempfile
import pytest


@pytest.fixture
def temp_front_dir():
    """Create a temporary directory for front card images."""
    front_dir = tempfile.mkdtemp()
    yield front_dir
    shutil.rmtree(front_dir)


@pytest.fixture
def temp_double_sided_dir():
    """Create a temporary directory for double-sided card images."""
    double_sided_dir = tempfile.mkdtemp()
    yield double_sided_dir
    shutil.rmtree(double_sided_dir)


@pytest.fixture
def temp_output_dirs():
    """Create temporary directories for both front and double-sided images."""
    front_dir = tempfile.mkdtemp()
    double_sided_dir = tempfile.mkdtemp()
    yield front_dir, double_sided_dir
    shutil.rmtree(front_dir)
    shutil.rmtree(double_sided_dir)


def verify_images_exist_and_have_content(directory: str, min_count: int = 1) -> bool:
    """
    Verify that images exist in a directory and have content.

    Args:
        directory: Path to directory containing images
        min_count: Minimum number of images expected

    Returns:
        True if verification passes
    """
    files = os.listdir(directory)
    assert len(files) >= min_count, f"Expected at least {min_count} files, found {len(files)}"

    for f in files:
        file_path = os.path.join(directory, f)
        file_size = os.path.getsize(file_path)
        assert file_size > 0, f"File {f} has 0 bytes"

    return True
