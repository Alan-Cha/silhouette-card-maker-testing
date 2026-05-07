"""
Test script for --extend_corners and --extend_edges.

This script generates test PDFs with various combinations of parameters
and provides expected results for visual verification.
"""

import subprocess
import os

# Create output directory for test results
output_dir = 'test_results'
os.makedirs(output_dir, exist_ok=True)

def run_test(test_name, extend_edges, extend_corners, expected_edge_color, expected_corner_color):
    """Run a single test case and save the output."""
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    print(f"Command: --extend_edges {extend_edges} --extend_corners {extend_corners}")
    print(f"Expected edge color: {expected_edge_color}")
    print(f"Expected corner color: {expected_corner_color}")

    # Build command
    cmd = [
        'python', 'create_pdf.py',
        '--front_dir_path', 'game/front',
        '--back_dir_path', 'game/back',
        '--double_sided_dir_path', 'game/double_sided',
        '--output_path', f'{output_dir}/{test_name}.pdf',
        '--only_fronts',
    ]

    if extend_edges:
        cmd.extend(['--extend_edges', extend_edges])
    if extend_corners:
        cmd.extend(['--extend_corners', extend_corners])

    # Run command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✓ Generated: {output_dir}/{test_name}.pdf")
        else:
            print(f"✗ Failed with error:")
            print(result.stderr)
    except Exception as e:
        print(f"✗ Exception: {e}")

print("="*70)
print("SYSTEMATIC TEST SUITE FOR --extend_corners AND --extend_edges")
print("="*70)
print("\nTest image: game/front/test_systematic.png")
print("  - Concentric rectangles (2mm steps, alternating black/white)")
print("  - Corner circles (1mm diameter steps, red/orange/yellow/green/blue)")

# Test 1: Only --extend_corners (various values)
print("\n" + "="*70)
print("TEST SERIES 1: --extend_corners only")
print("="*70)

corner_tests = [
    ('01_corners_0.5mm', None, '0.5mm', 'white (original)', 'red'),
    ('02_corners_1.0mm', None, '1.0mm', 'white (original)', 'orange'),
    ('03_corners_1.5mm', None, '1.5mm', 'white (original)', 'yellow'),
    ('04_corners_2.0mm', None, '2.0mm', 'white (original)', 'green'),
    ('05_corners_2.5mm', None, '2.5mm', 'white (original)', 'blue'),
]

for test_name, extend_edges, extend_corners, expected_edge, expected_corner in corner_tests:
    run_test(test_name, extend_edges, extend_corners, expected_edge, expected_corner)

# Test 2: Only --extend_edges (various values)
print("\n" + "="*70)
print("TEST SERIES 2: --extend_edges only")
print("="*70)

edge_tests = [
    ('06_edges_2mm', '2mm', None, 'black', 'white (original)'),
    ('07_edges_4mm', '4mm', None, 'white', 'white (original)'),
    ('08_edges_6mm', '6mm', None, 'black', 'white (original)'),
    ('09_edges_8mm', '8mm', None, 'white', 'white (original)'),
    ('10_edges_10mm', '10mm', None, 'black', 'white (original)'),
]

for test_name, extend_edges, extend_corners, expected_edge, expected_corner in edge_tests:
    run_test(test_name, extend_edges, extend_corners, expected_edge, expected_corner)

# Test 3: Combinations of --extend_edges and --extend_corners
print("\n" + "="*70)
print("TEST SERIES 3: --extend_edges AND --extend_corners combined")
print("="*70)

combination_tests = [
    ('11_edges_2mm_corners_0.5mm', '2mm', '0.5mm', 'black', 'red'),
    ('12_edges_4mm_corners_1.0mm', '4mm', '1.0mm', 'white', 'orange'),
    ('13_edges_6mm_corners_1.5mm', '6mm', '1.5mm', 'black', 'yellow'),
    ('14_edges_8mm_corners_2.0mm', '8mm', '2.0mm', 'white', 'green'),
    ('15_edges_10mm_corners_2.5mm', '10mm', '2.5mm', 'black', 'blue'),
]

for test_name, extend_edges, extend_corners, expected_edge, expected_corner in combination_tests:
    run_test(test_name, extend_edges, extend_corners, expected_edge, expected_corner)

# Test 4: Edge cases
print("\n" + "="*70)
print("TEST SERIES 4: Edge cases and extremes")
print("="*70)

edge_case_tests = [
    ('16_both_0', '0', '0', 'white (original)', 'white (original)'),
    ('17_large_corners', None, '5mm', 'white (original)', 'beyond blue (white bg)'),
    ('18_large_edges', '20mm', None, 'white (outermost)', 'white (original)'),
    ('19_both_large', '10mm', '2.5mm', 'black', 'blue'),
]

for test_name, extend_edges, extend_corners, expected_edge, expected_corner in edge_case_tests:
    run_test(test_name, extend_edges, extend_corners, expected_edge, expected_corner)

print("\n" + "="*70)
print("TEST SUITE COMPLETE")
print("="*70)
print(f"\nGenerated PDFs are in: {output_dir}/")
print("\nTo review results, examine each PDF and verify:")
print("  1. Edge bleed matches the expected color")
print("  2. Corner bleed matches the expected color")
print("  3. Bleed is consistent and has no artifacts")
print("\nTip: Focus on the test_systematic.png card in each PDF to see the effects clearly.")
