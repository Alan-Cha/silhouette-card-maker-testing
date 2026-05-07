# Testing Guide for --extend_corners and --extend_edges

## Overview

This guide explains how to systematically test the `--extend_corners` and `--extend_edges` features using the generated test image.

## Test Image Structure

The test image (`game/front/test_systematic.png`) is a 63mm x 88mm standard playing card with:

### Concentric Rectangle Bands
- **Purpose**: Test edge extension
- **Pattern**: Alternating white and black rectangular bands
- **Band width**: 2mm per band
- **Band sequence** (from outer to inner):
  - Band 1 (0-2mm): White
  - Band 2 (2-4mm): Black
  - Band 3 (4-6mm): White
  - Band 4 (6-8mm): Black
  - Band 5 (8-10mm): White
  - And so on...
- **Usage**: When `--extend_edges` crops N mm, the edge should show the color from the band at that inset

### Corner Circles
- **Purpose**: Test corner extension
- **Pattern**: Colored circles in all 4 corners
- **Colors (from smallest to largest)**:
  - Red: 1mm diameter (0.5mm radius)
  - Orange: 2mm diameter (1.0mm radius)
  - Yellow: 3mm diameter (1.5mm radius)
  - Green: 4mm diameter (2.0mm radius)
  - Blue: 5mm diameter (2.5mm radius)
- **Usage**: When `--extend_corners` uses N mm radius, the corner fill should show the color at that radius

## Running Tests

### Generate the Test Image
```bash
python create_test_image.py
```

### Run the Test Suite
```bash
python test_corner_edge_combinations.py
```

This generates 19 test PDFs in the `test_results/` directory.

## Test Series

### Series 1: --extend_corners Only (Tests 01-05)

| Test | Command | Expected Corner Color | Expected Edge Color |
|------|---------|----------------------|---------------------|
| 01 | `--extend_corners 0.5mm` | Red | White (original) |
| 02 | `--extend_corners 1.0mm` | Orange | White (original) |
| 03 | `--extend_corners 1.5mm` | Yellow | White (original) |
| 04 | `--extend_corners 2.0mm` | Green | White (original) |
| 05 | `--extend_corners 2.5mm` | Blue | White (original) |

**What to verify:**
- Corners should be filled with the specified color
- Straight edges should remain white (unchanged)
- No artifacts around corners

### Series 2: --extend_edges Only (Tests 06-10)

| Test | Command | Expected Edge Color | Expected Corner Color |
|------|---------|-------------------|---------------------|
| 06 | `--extend_edges 2mm` | Black (band 2) | White (original) |
| 07 | `--extend_edges 4mm` | White (band 3) | White (original) |
| 08 | `--extend_edges 6mm` | Black (band 4) | White (original) |
| 09 | `--extend_edges 8mm` | White (band 5) | White (original) |
| 10 | `--extend_edges 10mm` | Black (band 6) | White (original) |

**What to verify:**
- Edge bleed should match the expected color from concentric rectangles
- Corners should remain white (unchanged)
- Bleed should be uniform on all four edges

### Series 3: Combined --extend_edges and --extend_corners (Tests 11-15)

| Test | Command | Expected Edge Color | Expected Corner Color |
|------|---------|-------------------|---------------------|
| 11 | `--extend_edges 2mm --extend_corners 0.5mm` | Black (band 2) | Filled from 0.5mm arc |
| 12 | `--extend_edges 4mm --extend_corners 1.0mm` | White (band 3) | Filled from 1.0mm arc |
| 13 | `--extend_edges 6mm --extend_corners 1.5mm` | Black (band 4) | Filled from 1.5mm arc |
| 14 | `--extend_edges 8mm --extend_corners 2.0mm` | White (band 5) | Filled from 2.0mm arc |
| 15 | `--extend_edges 10mm --extend_corners 2.5mm` | Black (band 6) | Filled from 2.5mm arc |

**What to verify:**
- Both edge and corner effects should be visible
- Edge bleed should match expected edge color
- Corner fill should match expected corner color
- Transition from corner to edge should be seamless

### Series 4: Edge Cases (Tests 16-19)

| Test | Command | Expected Result |
|------|---------|----------------|
| 16 | `--extend_edges 0 --extend_corners 0` | Original image, no modifications |
| 17 | `--extend_corners 5mm` | Corners filled from 5mm arc |
| 18 | `--extend_edges 20mm` | Edge from band 11 (white) |
| 19 | `--extend_edges 10mm --extend_corners 2.5mm` | Black edges (band 6), corners filled from 2.5mm arc |

**What to verify:**
- Extreme values don't cause crashes
- Colors are correct even at boundaries
- No unexpected artifacts

## Visual Verification Checklist

For each test PDF, verify:

- [ ] **Edge Color**: Matches expected color from concentric rectangles
- [ ] **Corner Color**: Matches expected color from corner circles
- [ ] **Bleed Consistency**: Bleed is uniform and smooth
- [ ] **No Artifacts**: No visual glitches or incorrect pixel colors
- [ ] **Seamless Transition**: Corner and edge bleed blend properly
- [ ] **All Four Sides**: All edges and corners are consistent

## Common Issues to Look For

1. **Mismatched Bleed**: If corner bleed doesn't match filled corners, it means corners aren't being filled before bleed generation
2. **Missing Bleed**: If there's no bleed, check that print_bleed is calculated correctly
3. **Wrong Colors**: If colors don't match expectations, the inset/radius calculations may be off
4. **Artifacts in Corners**: May indicate issues with corner fill algorithm
5. **Inconsistent Edges**: May indicate issues with edge extension

## Interpreting Results

### Correct Behavior
- Corner fill should show the color at the specified radius
- Edge bleed should show the color at the specified inset
- Bleed should extend smoothly from the modified image

### Example Analysis

For test `13_edges_6mm_corners_1.5mm`:
1. **Edge**: 6mm inset → band 4 (6-8mm) → BLACK ✓
2. **Corner**: 1.5mm radius → corners filled from pixels at 1.5mm arc → varies by position ✓
3. **Bleed**: Should extend black from edges and filled colors from corners ✓

## Automated Verification (Future Enhancement)

Consider adding automated tests that:
1. Extract pixel colors from specific locations in generated PDFs
2. Compare against expected colors with tolerance
3. Generate pass/fail report

Example locations to sample:
- Edge bleed: midpoint of each edge
- Corner bleed: 45° diagonal from each corner
- Card content: center of card (should be unchanged)
