"""
Generate a systematic test image for --extend_corners and --extend_edges.

The test image has:
1. Concentric rectangles (2mm width/height difference, alternating black/white)
2. Circles in all 4 corners (1mm diameter difference, red/orange/yellow/green/blue)

This allows visual verification of corner and edge extension at different values.
"""

from PIL import Image, ImageDraw

# Standard card size: 63mm x 88mm at 300 PPI
PPI = 300
CARD_WIDTH_MM = 63
CARD_HEIGHT_MM = 88

# Convert mm to pixels
def mm_to_px(mm):
    return int(mm * PPI / 25.4)

width_px = mm_to_px(CARD_WIDTH_MM)
height_px = mm_to_px(CARD_HEIGHT_MM)

print(f"Creating test image: {width_px}x{height_px} pixels ({CARD_WIDTH_MM}x{CARD_HEIGHT_MM} mm)")

# Create the image
img = Image.new('RGB', (width_px, height_px), 'white')
draw = ImageDraw.Draw(img)

# Draw concentric rectangles as BANDS (not filled), alternating black/white
# Each band is 2mm wide
colors = ['black', 'white']

print(f"\nDrawing concentric rectangle bands (2mm width):")
# Start from outermost and work inward, drawing bands
i = 1
while True:
    outer_inset = mm_to_px(2 * (i - 1))  # Outer edge of this band
    inner_inset = mm_to_px(2 * i)        # Inner edge of this band
    color = colors[i % 2]  # i=1 -> black, i=2 -> white, i=3 -> black, ...

    # Check if band fits
    if inner_inset >= width_px // 2 or inner_inset >= height_px // 2:
        break

    # Draw the band as 4 rectangles (top, bottom, left, right)
    # Top band
    draw.rectangle([outer_inset, outer_inset, width_px - outer_inset, inner_inset], fill=color)
    # Bottom band
    draw.rectangle([outer_inset, height_px - inner_inset, width_px - outer_inset, height_px - outer_inset], fill=color)
    # Left band (between top and bottom)
    draw.rectangle([outer_inset, inner_inset, inner_inset, height_px - inner_inset], fill=color)
    # Right band (between top and bottom)
    draw.rectangle([width_px - inner_inset, inner_inset, width_px - outer_inset, height_px - inner_inset], fill=color)

    print(f"  Band {i}: {color} from {outer_inset}px to {inner_inset}px ({2*(i-1)}mm to {2*i}mm)")
    i += 1

# Draw circles in corners (1mm diameter difference)
# Colors: red, orange, yellow, green, blue
corner_colors = [
    (255, 0, 0),      # red (smallest)
    (255, 165, 0),    # orange
    (255, 255, 0),    # yellow
    (0, 255, 0),      # green
    (0, 0, 255),      # blue (largest)
]

print(f"\nDrawing corner circles (1mm diameter steps):")
for i, color in enumerate(corner_colors):
    diameter_mm = 1 + i  # 1mm, 2mm, 3mm, 4mm, 5mm
    radius_px = mm_to_px(diameter_mm / 2)
    diameter_px = radius_px * 2

    color_name = ['red', 'orange', 'yellow', 'green', 'blue'][i]
    print(f"  Circle {i+1}: {color_name} - {diameter_mm}mm diameter ({diameter_px}px)")

    # Top-left corner
    draw.ellipse([0, 0, diameter_px, diameter_px], fill=color)

    # Top-right corner
    draw.ellipse([width_px - diameter_px, 0, width_px, diameter_px], fill=color)

    # Bottom-left corner
    draw.ellipse([0, height_px - diameter_px, diameter_px, height_px], fill=color)

    # Bottom-right corner
    draw.ellipse([width_px - diameter_px, height_px - diameter_px, width_px, height_px], fill=color)

# Save the image
output_path = 'game/front/test_systematic.png'
img.save(output_path)
print(f"\nTest image saved to: {output_path}")

# Print expected results for different --extend_corners values
print("\n" + "="*70)
print("EXPECTED RESULTS:")
print("="*70)

print("\n--extend_corners values (corner color changes):")
for i, color_name in enumerate(['red', 'orange', 'yellow', 'green', 'blue']):
    diameter_mm = 1 + i
    radius_mm = diameter_mm / 2
    print(f"  --extend_corners {radius_mm:.1f}mm: corners should become {color_name}")

print("\n--extend_edges values (edge color changes):")
for i in range(1, 11):
    inset_mm = 2 * i
    color = 'black' if i % 2 == 1 else 'white'
    print(f"  --extend_edges {inset_mm}mm: edges should become {color}")

print("\nCombinations to test:")
print("  --extend_edges 2mm --extend_corners 0.5mm: white edges, red corners")
print("  --extend_edges 4mm --extend_corners 1.5mm: black edges, orange corners")
print("  --extend_edges 6mm --extend_corners 2.5mm: white edges, yellow corners")
print("  --extend_edges 8mm --extend_corners 3.5mm: black edges, green corners")
print("  --extend_edges 10mm --extend_corners 4.5mm: white edges, blue corners")
