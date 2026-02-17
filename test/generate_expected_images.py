"""Generate expected output images for create_pdf.py integration tests.

Run this script to regenerate the expected images in test/images_expected/
after intentional changes to the layout logic.

Usage:
    python test/generate_expected_images.py
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from click.testing import CliRunner
from create_pdf import cli

IMAGES_DIR = os.path.join('test', 'images')
BACK_DIR = os.path.join('test', 'basic', 'back')
EXPECTED_DIR = os.path.join('test', 'images_expected')

# Each test case: (name, extra_cli_args)
TEST_CASES = [
    ('default', []),
    ('japanese', ['--card_size', 'japanese']),
    ('only_fronts', ['--only_fronts']),
    ('a4', ['--paper_size', 'a4']),
    ('crop', ['--crop', '3mm']),
    ('extend_corners', ['--extend_corners', '5']),
    ('fit_crop', ['--fit', 'crop']),
    ('skip', ['--skip', '0', '--skip', '4']),
]


def generate_expected_images():
    runner = CliRunner()

    for name, extra_args in TEST_CASES:
        output_dir = os.path.join(EXPECTED_DIR, name)

        # Clean and recreate
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        # Build CLI args
        args = [
            '--front_dir_path', IMAGES_DIR,
            '--back_dir_path', BACK_DIR,
            '--double_sided_dir_path', IMAGES_DIR,  # no matching fronts, so ignored
            '--output_path', os.path.join(output_dir, 'output.pdf'),
            '--output_images',
        ] + extra_args

        # The double_sided_dir_path needs to be a directory with no matching
        # images to the front dir. Use an empty temp dir instead.
        import tempfile
        with tempfile.TemporaryDirectory() as empty_ds_dir:
            args = [
                '--front_dir_path', IMAGES_DIR,
                '--back_dir_path', BACK_DIR,
                '--double_sided_dir_path', empty_ds_dir,
                '--output_path', os.path.join(output_dir, 'output.pdf'),
                '--output_images',
            ] + extra_args

            print(f'Generating: {name}...')
            result = runner.invoke(cli, args)
            if result.exit_code != 0:
                print(f'  FAILED (exit code {result.exit_code})')
                if result.output:
                    print(f'  Output: {result.output}')
                if result.exception:
                    import traceback
                    traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
                continue

            files = sorted(os.listdir(output_dir))
            print(f'  Generated {len(files)} file(s): {files}')

    print('\nDone. Expected images saved to:', EXPECTED_DIR)


if __name__ == '__main__':
    generate_expected_images()
