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
    ('default', []),
    ('only_fronts', ['--only_fronts']),

    # Card sizes
    ('bridge', ['--card_size', 'bridge', '--only_fronts']),
    ('poker', ['--card_size', 'poker', '--only_fronts']),
    ('japanese', ['--card_size', 'japanese', '--only_fronts']),

    # Paper sizes
    ('tabloid', ['--paper_size', 'tabloid', '--only_fronts']),
    ('a4', ['--paper_size', 'a4', '--only_fronts']),
    ('a3', ['--paper_size', 'a3', '--only_fronts']),

    # Paper and card combinations
    ('tabloid-domino_square', ['--paper_size', 'tabloid', '--card_size', 'domino_square', '--only_fronts']),
    ('a4-bridge', ['--paper_size', 'a4', '--card_size', 'bridge', '--only_fronts']),

    # Other options
    ('ppi600', ['--ppi', '600']),
    ('a4-ppi600', ['--paper_size', 'a4', '--ppi', '600', '--only_fronts']),

    ('ppi600-quality100', ['--ppi', '600', '--quality', '100']),

    ('quality100', ['--quality', '100']),
    ('quality75', ['--quality', '75', '--only_fronts']),
    ('quality50', ['--quality', '50', '--only_fronts']),

    ('registration4', ['--registration', '4']),
    ('registration4-tabloid', ['--registration', '4', '--paper_size', 'tabloid']),

    ('show_outline', ['--show_outline']),
    ('show_outline-domino', ['--show_outline', '--card_size', 'domino']),

    ('label', ['--label', 'Test Label', '--only_fronts']),
    ('label-tabloid', ['--label', 'Test Label', '--paper_size', 'tabloid', '--only_fronts']),

    ('crop', ['--crop', '3mm', '--only_fronts']),
    ('extend_corners', ['--extend_corners', '10', '--only_fronts']),
    ('fit_crop', ['--card_size', 'domino', '--fit', 'crop', '--only_fronts']),
    ('skip', ['--skip', '0', '--skip', '4']),
]
