# Image Upscaling Guide

This guide explains how to use the image upscaling feature to improve the quality of your card images before creating PDFs.

## Why Upscale?

Card images from online sources (like Scryfall for MTG) typically come at 300-600 DPI. For optimal print quality and precise cutting, higher resolution images (1200 DPI) are recommended. The upscaling tool uses AI-powered Real-ESRGAN to intelligently enhance image quality while increasing resolution.

## Quick Start

### 1. Install Dependencies (One-time setup)

For basic upscaling without GPU acceleration:
```bash
pip install -r requirements.txt
```

For GPU acceleration (NVIDIA CUDA):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install basicsr facexlib gfpgan realesrgan opencv-python
```

### 2. Fetch Card Images

Use any plugin to fetch your card images, for example:
```bash
python plugins/mtg/fetch.py my_deck.txt mtga
```

### 3. Upscale Images

#### Standalone Upscaling
```bash
python upscale.py
```

#### Integrated with PDF Creation
```bash
python create_pdf.py --upscale
```

## Usage Examples

### Basic Upscaling
Upscale all images in the game directories to 1200 DPI:
```bash
python upscale.py
```

### Different Card Sizes
For poker-sized cards:
```bash
python upscale.py --card_size poker
```

For Japanese-sized cards (Yu-Gi-Oh!):
```bash
python upscale.py --card_size japanese
```

### Custom Target DPI
Set a different target DPI:
```bash
python upscale.py --target_dpi 600
```

### Force Upscaling
Force upscale even if images are already at target DPI:
```bash
python upscale.py --force
```

### CPU-Only Mode
Use CPU instead of GPU (useful for troubleshooting):
```bash
python upscale.py --gpu_id -1
```

### Simple Upscaling (No AI)
Use traditional Lanczos upscaling without Real-ESRGAN:
```bash
python upscale.py --use_simple
```

## How It Works

1. **DPI Calculation**: The script calculates the current DPI of each image based on:
   - Image dimensions (width × height in pixels)
   - Card physical dimensions (e.g., 63mm × 88mm for standard cards)

2. **Smart Upscaling**: Images are only upscaled if their current DPI is below the target DPI

3. **Scale Factor**: The tool automatically calculates the required scale factor:
   ```
   Scale Factor = Target DPI / Current DPI
   ```

4. **AI Enhancement**: Real-ESRGAN uses deep learning to:
   - Upscale images up to 4x their original size
   - Enhance details and reduce artifacts
   - Preserve image quality better than traditional methods

5. **Format Preservation**: 
   - PNG images maintain transparency
   - JPEG images are saved with 95% quality
   - Original file formats are preserved

## Performance

### GPU Acceleration
- **CUDA (NVIDIA)**: 10-50x faster than CPU
- **MPS (Apple Silicon)**: 5-20x faster than CPU
- **Processing Time**: 1-3 seconds per image on GPU

### CPU Processing
- **Processing Time**: 10-30 seconds per image
- **No special hardware required**
- **Automatic fallback** if GPU is unavailable

### Memory Requirements
- **GPU**: 2-4GB VRAM recommended
- **CPU**: 4-8GB RAM recommended
- Images are processed one at a time to manage memory

## Troubleshooting

### "Real-ESRGAN dependencies not installed"
Install the required packages:
```bash
pip install -r requirements.txt
```

Then run the compatibility fix:
```bash
python fix_realesrgan.py
```

This patches basicsr to work with torchvision 0.17.0+.

### GPU Memory Errors
Try these solutions:
1. Use CPU mode: `--gpu_id -1`
2. Use simple upscaling: `--use_simple`
3. Reduce target DPI: `--target_dpi 800`

### Slow Processing on CPU
This is normal. Options:
1. Use GPU if available
2. Use simple upscaling for faster (but lower quality) results
3. Reduce target DPI to minimize processing time

## Integration with Workflow

### Recommended Workflow
1. Fetch card images using a plugin
2. Upscale images to 1200 DPI
3. Create PDF with high-quality images
4. Print and cut with precision

### Example: MTG Proxy Creation
```bash
# Step 1: Fetch cards from Scryfall
python plugins/mtg/fetch.py my_commander_deck.txt mtga

# Step 2: Upscale to 1200 DPI
python upscale.py

# Step 3: Create PDF (with optional offset)
python create_pdf.py --load_offset

# Alternative: Combine steps 2-3
python create_pdf.py --upscale --load_offset
```

## FAQ

**Q: Will this work without a GPU?**  
A: Yes! The script automatically detects GPU availability and falls back to CPU if needed. CPU processing is slower but produces the same quality.

**Q: Does upscaling work with transparent images?**  
A: Yes, PNG transparency is preserved during upscaling.

**Q: How long does upscaling take?**  
A: On GPU: 1-3 seconds per image. On CPU: 10-30 seconds per image.

**Q: What if I already have high-resolution images?**  
A: The script automatically detects and skips images that are already at or above the target DPI (smart upscaling).

**Q: Can I upscale to more than 1200 DPI?**  
A: Yes, use `--target_dpi` with any value (minimum 300). However, 1200 DPI is typically sufficient for printing.

**Q: Will this improve blurry images?**  
A: Real-ESRGAN can enhance details and reduce some blur, but it cannot fully recover information that wasn't in the original image. Results are best with reasonably clear source images.

## Technical Details

### Supported Card Sizes
- `standard` (63×88mm) - MTG, Pokémon, Lorcana, etc.
- `japanese` (59×86mm) - Yu-Gi-Oh!
- `poker` (63.5×88.9mm)
- `bridge` (57.15×88.9mm)
- `tarot` (69.85×120.65mm)
- And more...

### Real-ESRGAN Model
- Model: RealESRGAN_x4plus
- Architecture: RRDB (Residual in Residual Dense Block)
- Scale: 4x upscaling
- Optimized for: General photos and artwork

### Image Formats
Supported input formats:
- PNG (with transparency support)
- JPEG/JPG
- BMP
- TIFF
- WebP

## Credits

Upscaling powered by [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - a practical image restoration algorithm for anime images and real-world photos.

