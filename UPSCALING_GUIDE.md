# 🎨 Image Upscaling Guide

Welcome to the Silhouette Card Maker upscaling guide! This guide will help you improve the quality of your printed cards by upscaling low-resolution images using AI technology.

---

## 📖 Table of Contents

1. [Why Upscale?](#why-upscale)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [Performance](#performance)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)
8. [Technical Details](#technical-details)

---

## 💡 Why Upscale?

Card images from online sources (like Scryfall for MTG) typically come at **300-600 DPI**. While this is okay for viewing on screens, it's not ideal for printing:

- **Low DPI (300):** Edges may look jagged when cut
- **Medium DPI (600):** Acceptable but can still show artifacts  
- **High DPI (1200):** Crisp, professional-looking cards with clean edges

**The upscaling tool uses AI-powered Real-ESRGAN** to intelligently enhance image quality while increasing resolution. This means better-looking cards with sharper text and clearer artwork!

### Benefits of Upscaling
- ✅ Sharper card edges after cutting
- ✅ Clearer text and symbols
- ✅ Enhanced artwork details
- ✅ Professional print quality
- ✅ Better color accuracy

---

## 🚀 Quick Start

Get upscaling in 3 easy steps:

### Step 1: Install Dependencies (One-time setup)

**Option A: Automatic Installation (Recommended)**
```bash
# Install all dependencies
pip install -r requirements.txt
```

**Option B: NVIDIA GPU Users (For Best Performance)**
```bash
# Uninstall default packages
pip uninstall torch torchvision torch-directml -y

# Install CUDA-enabled PyTorch
pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cu118

# Install Real-ESRGAN dependencies
pip install basicsr facexlib gfpgan realesrgan opencv-python
```

> **💡 Tip:** The default installation automatically supports AMD/Intel GPUs on Windows via DirectML, and Apple Silicon (M1/M2/M3) on macOS!

### Step 2: Fetch Your Card Images

Use any plugin to fetch your card images. For example, with Magic: The Gathering:
```bash
python plugins/mtg/fetch.py my_deck.txt mtga
```

### Step 3: Upscale!

**Method A: Standalone Upscaling**
```bash
python upscale.py
```

**Method B: Upscale During PDF Creation**
```bash
python create_pdf.py --upscale
```

That's it! Your cards will be upscaled to 1200 DPI for beautiful prints. 🎉

---

## 📋 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM (8GB recommended)
- Optional: GPU with 2GB+ VRAM for faster processing

### Detailed Installation Steps

1. **Activate your Python virtual environment** (if you haven't already):
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation (optional):**
   ```bash
   python upscale.py --help
   ```

That's it! You're ready to upscale. 🎉

---

## 📚 Usage Examples

### Example 1: Basic Upscaling
Upscale all images in the default game directories to 1200 DPI:
```bash
python upscale.py
```

**What happens:**
- Scans `game/front/`, `game/back/`, and `game/double_sided/` directories
- Calculates current DPI for each image
- Upscales only images below 1200 DPI
- Skips images already at target DPI

---

### Example 2: Different Card Sizes

**For Poker-sized cards:**
```bash
python upscale.py --card_size poker
```

**For Yu-Gi-Oh! (Japanese-sized cards):**
```bash
python upscale.py --card_size japanese
```

**Supported card sizes:** `standard`, `poker`, `japanese`, `bridge`, `tarot`, and more!

---

### Example 3: Custom Target DPI

Want a different resolution? Set your own target DPI:
```bash
# Upscale to 800 DPI (faster, smaller files)
python upscale.py --target_dpi 800

# Upscale to 1500 DPI (highest quality)
python upscale.py --target_dpi 1500
```

**Recommended DPI values:**
- 600 DPI: Good for casual play
- 1200 DPI: Recommended for best results
- 1500+ DPI: Overkill for most printers

---

### Example 4: Force Upscaling

Already upscaled but want to process again?
```bash
python upscale.py --force
```

This will upscale **all** images, even those already at or above target DPI.

---

### Example 5: CPU-Only Mode

Having GPU issues or want to test without GPU?
```bash
python upscale.py --gpu_id -1
```

**Note:** CPU processing is 10-30x slower than GPU but produces the same quality.

---

### Example 6: Simple Upscaling (No AI)

Need fast upscaling without AI? Use traditional Lanczos method:
```bash
python upscale.py --use_simple
```

**Pros:** Much faster (0.5-2 seconds per image)  
**Cons:** Lower quality than AI upscaling

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

---

## 🔧 Troubleshooting

Having issues? Here are solutions to common problems:

### Problem: "Real-ESRGAN dependencies not installed"

**Solution:**
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

---

### Problem: GPU Memory Errors

**Symptoms:** `RuntimeError: CUDA out of memory` or similar GPU errors

**Solutions (try in order):**

1. **Close other GPU-intensive programs** (games, video editors, browsers with hardware acceleration)

2. **Use CPU mode instead:**
   ```bash
   python upscale.py --gpu_id -1
   ```

3. **Use simple upscaling (no AI):**
   ```bash
   python upscale.py --use_simple
   ```

4. **Reduce target DPI:**
   ```bash
   python upscale.py --target_dpi 800
   ```

---

### Problem: Slow Processing on CPU

**Symptoms:** Taking 10-30 seconds per image

**This is normal!** CPU processing is much slower than GPU. Options:

1. **Be patient** - CPU processing works, it just takes longer
2. **Process overnight** for large decks
3. **Use simple upscaling** for faster results:
   ```bash
   python upscale.py --use_simple
   ```
4. **Lower target DPI** to reduce processing time:
   ```bash
   python upscale.py --target_dpi 600
   ```

---

### Problem: "ModuleNotFoundError: No module named 'click'"

**Solution:** Activate your virtual environment first:
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Then install dependencies
pip install -r requirements.txt
```

---

### Problem: Images look worse after upscaling

**Possible causes:**

1. **Source images are very low quality** - AI can't create details that don't exist
2. **Wrong card size selected** - Make sure you're using the correct `--card_size`
3. **Try AI upscaling** instead of simple mode:
   ```bash
   python upscale.py  # (without --use_simple)
   ```

---

### Problem: "Permission denied" when saving files

**Solution:** Make sure the image files aren't open in another program (image viewer, editor, etc.)

---

### Problem: Upscaling stops or crashes

**Solutions:**

1. **Check available disk space** - Upscaled images are larger
2. **Check available RAM** - Need 4-8GB free
3. **Try processing fewer images at once** - Move some images to a different folder temporarily
4. **Use CPU mode** if GPU is unstable:
   ```bash
   python upscale.py --gpu_id -1
   ```

---

### Still having problems?

1. Check the error message carefully
2. Make sure your Python version is 3.8 or higher: `python --version`
3. Try reinstalling dependencies:
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```
4. Ask for help on the [Discord server](https://discord.gg/jhsKmAgbXc)

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

---

## ❓ FAQ

### Q: Do I need a GPU to use upscaling?

**A:** No! The upscaling works on any computer with or without a GPU.
- **With GPU:** Fast (1-3 seconds per image) ⚡
- **Without GPU (CPU):** Slower (10-30 seconds per image) but same quality 🐢

The tool automatically detects your hardware and uses the best available option.

---

### Q: Does upscaling work with transparent PNG images?

**A:** Yes! PNG transparency is fully preserved during upscaling. Perfect for cards with transparent backgrounds or special effects.

---

### Q: How long does it take to upscale a full deck?

**A:** For a typical 60-100 card deck:
- **GPU:** 2-5 minutes
- **CPU:** 20-50 minutes

**Tip:** Run it while you're doing something else! The tool will keep working in the background.

---

### Q: What if my images are already high-resolution?

**A:** The tool is smart! It automatically:
- Checks the DPI of each image
- Only upscales images below the target DPI
- Skips images that are already high-res

This saves time and prevents unnecessary processing.

---

### Q: Can I upscale to more than 1200 DPI?

**A:** Yes! Use `--target_dpi` with any value:
```bash
python upscale.py --target_dpi 1500
```

**However:** 1200 DPI is usually more than enough for printing. Going higher:
- Increases processing time
- Creates larger files
- May not improve visible quality
- Can exceed printer capabilities

---

### Q: Will upscaling fix blurry or pixelated images?

**A:** Partially. Real-ESRGAN can:
- ✅ Enhance existing details
- ✅ Reduce some blur and artifacts
- ✅ Make edges sharper
- ❌ Cannot recreate missing details
- ❌ Won't fix severely damaged images

**Best results** come from reasonably clear source images (300+ DPI).

---

### Q: Is upscaling safe? Will it damage my original images?

**A:** Yes, it's safe! The tool uses atomic file operations:
1. Upscales image to a temporary file
2. Verifies the upscaled image is valid
3. Only then replaces the original

If anything goes wrong, your original image is preserved.

---

### Q: Can I stop upscaling and resume later?

**A:** Yes! If you stop the process (Ctrl+C):
- Already upscaled images remain upscaled
- Not-yet-processed images remain unchanged
- Just run the command again to continue

The tool automatically skips images that are already at target DPI.

---

### Q: How much disk space do upscaled images take?

**A:** Upscaled images are typically 2-4x larger than originals.

**Example:** A 60-card deck:
- Original (300 DPI): ~15-30 MB
- Upscaled (1200 DPI): ~60-120 MB

Make sure you have sufficient disk space before upscaling large collections.

---

### Q: Which GPU brands are supported?

**A:** All major GPU brands:
- ✅ **NVIDIA:** Full CUDA support (fastest)
- ✅ **AMD:** DirectML support on Windows
- ✅ **Intel:** DirectML support on Windows  
- ✅ **Apple Silicon:** MPS support (M1/M2/M3)
- ✅ **No GPU:** CPU fallback (works everywhere)

---

### Q: Does this work offline?

**A:** Mostly yes!
- ✅ Upscaling works completely offline after initial model download
- 🌐 First run downloads the AI model (~67MB) from the internet
- ✅ After that, everything works offline

---

### Q: Can I upscale other types of images (not cards)?

**A:** The tool is optimized for card-sized images, but you can technically use it for any images by specifying dimensions. However, for best results with non-card images, consider using Real-ESRGAN directly.

---

### Q: Why does my GPU show 0% usage?

**A:** Possible reasons:
1. The tool is using CPU instead (check the startup message)
2. Images are very small and process quickly
3. Using `--use_simple` mode (doesn't use GPU)
4. GPU drivers need updating

**Check:** Look for `"Using CUDA"` or `"Using DirectML"` message at startup.

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

