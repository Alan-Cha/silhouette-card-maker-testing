"""Shared test case definitions for create_pdf.py tests.

Imported by both generate_expected_images.py (to produce reference images)
and test_create_pdf.py (to run the parametrized pixel-comparison tests).
Adding a new test case here automatically covers both.
"""
import os

# Shared fixture paths
IMAGES_DIR = os.path.join('test', 'images')       # card images used as input
BACK_DIR = os.path.join('test', 'basic', 'back')  # back image for all tests
EXPECTED_DIR = os.path.join('test', 'images_expected')  # pre-generated reference PNGs

# Each entry: (name, extra_cli_args)
# - name: identifies the test and maps to a subdirectory in EXPECTED_DIR
# - extra_cli_args: additional CLI arguments passed to create_pdf
TEST_CASES = [
    ('default',        []),
    ('japanese',       ['--card_size', 'japanese']),
    ('only_fronts',    ['--only_fronts']),
    ('a4',             ['--paper_size', 'a4']),
    ('crop',           ['--crop', '3mm']),
    ('extend_corners', ['--extend_corners', '5']),
    ('fit_crop',       ['--fit', 'crop']),
    ('skip',           ['--skip', '0', '--skip', '4']),
]
