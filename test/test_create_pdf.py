import os
import pytest
import tempfile
from click.testing import CliRunner
from PIL import Image, ImageChops
from create_pdf import cli

IMAGES_DIR = os.path.join('test', 'images')
BACK_DIR = os.path.join('test', 'basic', 'back')
EXPECTED_DIR = os.path.join('test', 'images_expected')


def assert_images_match(actual_dir, expected_dir):
    """Compare all PNG files in actual_dir against expected_dir pixel-by-pixel."""
    actual_files = sorted(f for f in os.listdir(actual_dir) if f.endswith('.png'))
    expected_files = sorted(f for f in os.listdir(expected_dir) if f.endswith('.png'))

    assert actual_files == expected_files, (
        f"File mismatch.\n  Actual: {actual_files}\n  Expected: {expected_files}"
    )

    for filename in actual_files:
        actual_img = Image.open(os.path.join(actual_dir, filename))
        expected_img = Image.open(os.path.join(expected_dir, filename))

        assert actual_img.size == expected_img.size, (
            f"{filename}: size mismatch {actual_img.size} != {expected_img.size}"
        )

        # Convert both to same mode for comparison
        actual_rgb = actual_img.convert('RGB')
        expected_rgb = expected_img.convert('RGB')

        diff = ImageChops.difference(actual_rgb, expected_rgb)
        if diff.getbbox() is not None:
            # Calculate how many pixels differ
            diff_pixels = sum(1 for px in diff.getdata() if px != (0, 0, 0))
            total_pixels = actual_rgb.size[0] * actual_rgb.size[1]
            raise AssertionError(
                f"{filename}: images differ. "
                f"{diff_pixels}/{total_pixels} pixels differ."
            )


def run_output_images_test(test_name, extra_args=None):
    """Helper to run a create_pdf --output_images test case."""
    runner = CliRunner()
    expected_dir = os.path.join(EXPECTED_DIR, test_name)

    assert os.path.isdir(expected_dir), (
        f"Expected images directory not found: {expected_dir}. "
        f"Run 'python test/generate_expected_images.py' first."
    )

    with tempfile.TemporaryDirectory() as output_dir:
        with tempfile.TemporaryDirectory() as empty_ds_dir:
            args = [
                '--front_dir_path', IMAGES_DIR,
                '--back_dir_path', BACK_DIR,
                '--double_sided_dir_path', empty_ds_dir,
                '--output_path', os.path.join(output_dir, 'output.pdf'),
                '--output_images',
            ]
            if extra_args:
                args += extra_args

            result = runner.invoke(cli, args)
            assert result.exit_code == 0, (
                f"CLI failed with exit code {result.exit_code}.\n"
                f"Output: {result.output}\n"
                f"Exception: {result.exception}"
            )

            assert_images_match(output_dir, expected_dir)


def test_basic_create_pdf():
    runner = CliRunner()
    result = runner.invoke(cli, "--front_dir_path test/basic/front --back_dir_path test/basic/back --output_path test/basic/output/game.pdf")
    assert result.exit_code == 0
    assert os.path.exists("test/basic/output/game.pdf")


def test_output_images_default():
    run_output_images_test('default')


def test_output_images_japanese():
    run_output_images_test('japanese', ['--card_size', 'japanese'])


def test_output_images_only_fronts():
    run_output_images_test('only_fronts', ['--only_fronts'])


def test_output_images_a4():
    run_output_images_test('a4', ['--paper_size', 'a4'])


def test_output_images_crop():
    run_output_images_test('crop', ['--crop', '3mm'])


def test_output_images_extend_corners():
    run_output_images_test('extend_corners', ['--extend_corners', '5'])


def test_output_images_fit_crop():
    run_output_images_test('fit_crop', ['--fit', 'crop'])


def test_output_images_skip():
    run_output_images_test('skip', ['--skip', '0', '--skip', '4'])
