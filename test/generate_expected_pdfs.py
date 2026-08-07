"""Generate expected output images for create_pdf.py integration tests.

Run this script to regenerate the expected images in test/expected_pdfs/
after intentional changes to the layout logic.

Usage:
    python test/generate_expected_images.py
"""

import os
import shutil
import sys

import click

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from click.testing import CliRunner
from create_pdf import cli
from test.pdf_cases import IMAGES_DIR, BACK_DIR, DS_DIR, EXPECTED_DIR, TEST_CASES


def generate_expected_images(generate_new: bool = False):
    runner = CliRunner()

    for name, extra_args in TEST_CASES:
        output_dir = os.path.join(EXPECTED_DIR, name)

        if generate_new and os.path.exists(output_dir):
            print(f"Skipping: {name} (already exists)")
            continue

        # Clean and recreate
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        args = [
            "--front_dir_path",
            IMAGES_DIR,
            "--back_dir_path",
            BACK_DIR,
            "--double_sided_dir_path",
            DS_DIR,
            "--output_path",
            os.path.join(output_dir, "output.pdf"),
            "--output_images",
        ] + extra_args

        print(f"Generating: {name}...")
        result = runner.invoke(cli, args)
        if result.exit_code != 0:
            print(f"  FAILED (exit code {result.exit_code})")
            if result.output:
                print(f"  Output: {result.output}")
            if result.exception:
                import traceback

                traceback.print_exception(
                    type(result.exception),
                    result.exception,
                    result.exception.__traceback__,
                )
            continue

        files = sorted(os.listdir(output_dir))
        print(f"  Generated {len(files)} file(s): {files}")

    print("\nDone. Expected images saved to:", EXPECTED_DIR)


@click.command()
@click.option(
    "--new",
    "generate_new",
    is_flag=True,
    help="Only generate expected images for test cases whose output directory is missing.",
)
def main(generate_new: bool):
    generate_expected_images(generate_new)


if __name__ == "__main__":
    main()
