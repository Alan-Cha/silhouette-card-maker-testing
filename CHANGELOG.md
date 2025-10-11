# Changelog - Image Enhancements Feature Branch

All notable changes made in the `feature/image-enhancements` branch.

## Summary

This branch adds powerful AI-powered image upscaling and enhancement features to improve card print quality. Cards fetched from online sources (typically 300-600 DPI) can now be automatically upscaled to 1200 DPI using Real-ESRGAN, and enhanced with saturation and contrast adjustments for more vibrant prints.

---

## 🎨 New Features

### AI-Powered Image Upscaling (`upscale.py`)

A new standalone tool for intelligently upscaling card images using Real-ESRGAN AI technology.

**Key Features:**
- ✨ AI-powered upscaling to 1200 DPI (configurable)
- 🚀 Automatic GPU acceleration (CUDA, DirectML, MPS)
- 🧠 Smart upscaling - only processes images below target DPI
- 🖼️ Preserves PNG transparency
- 📦 Supports all card sizes (MTG, Pokémon, Yu-Gi-Oh!, etc.)
- 💾 Safe file operations with atomic replacement

**New CLI Options:**
- `--target_dpi` - Target DPI for upscaling (default: 1200)
- `--force` - Force upscale all images
- `--use_simple` - Use simple Lanczos upscaling (no AI)
- `--gpu_id` - GPU device selection (None=auto, -1=CPU)

**Usage:**
```bash
# Basic upscaling to 1200 DPI
python upscale.py

# Custom target DPI
python upscale.py --target_dpi 800

# Force upscale all images
python upscale.py --force

# Use CPU only
python upscale.py --gpu_id -1
```

---

### Image Enhancement Features

New image enhancement options in `create_pdf.py` for adjusting saturation and contrast.

**New CLI Options:**
- `--saturation` - Saturation multiplier (1.0=no change, >1.0=boost, <1.0=reduce)
- `--contrast` - Contrast multiplier (1.0=no change, >1.0=boost, <1.0=reduce)
- `--upscale` - Automatically upscale images before creating PDF
- `--upscale_target_dpi` - Target DPI when upscaling (default: 1200)

**Usage:**
```bash
# Boost saturation and contrast for vibrant cards
python create_pdf.py --saturation 1.2 --contrast 1.15

# Combine upscaling with enhancements
python create_pdf.py --upscale --saturation 1.1 --contrast 1.1

# Upscale to custom DPI
python create_pdf.py --upscale --upscale_target_dpi 1500
```

---


### GPU Support Improvements

Enhanced GPU detection and support across multiple platforms:

**Supported Acceleration:**
- ✅ **NVIDIA GPUs** - CUDA acceleration (fastest)
- ✅ **AMD/Intel GPUs on Windows** - DirectML acceleration
- ✅ **Apple Silicon** - MPS acceleration (M1/M2/M3)
- ✅ **CPU Fallback** - Works everywhere (slower but reliable)

**Automatic Detection:**
The tools automatically detect and use the best available hardware acceleration without manual configuration.

---

## 📝 Files Modified/Created

### Modified Files

#### `create_pdf.py`
- Added `--upscale` flag for automatic image upscaling
- Added `--upscale_target_dpi` option (default: 1200)
- Added `--saturation` option for color enhancement (range: 0.0-2.0)
- Added `--contrast` option for contrast adjustment (range: 0.0-2.0)
- Integrated with `upscale.py` for seamless workflow
- Graceful degradation if upscaling dependencies not installed

#### `utilities.py`
- Added `enhance_image()` function for saturation/contrast adjustments
- Integrated enhancements into PDF generation pipeline
- Applied to front and double-sided images (backs excluded when flipped)
- Uses PIL ImageEnhance for high-quality adjustments

#### `requirements.txt`
- Added PyTorch and torchvision for deep learning
- Added Real-ESRGAN and dependencies (basicsr, facexlib, gfpgan)  
- Added opencv-python for image processing
- Platform-specific PyTorch installations (DirectML on Windows, standard elsewhere)
- Comprehensive comments and installation instructions

**Note:** Real-ESRGAN/basicsr compatibility with newer torchvision versions is handled automatically by the libraries.

### New Files

#### `upscale.py`
New standalone AI-powered image upscaling tool with comprehensive CLI and documentation.

---

## 📚 Documentation Created/Updated

#### `UPSCALING_GUIDE.md`
Comprehensive guide covering:
- Why upscaling matters for print quality
- Step-by-step installation instructions
- Usage examples for different scenarios
- Performance benchmarks
- Troubleshooting common issues
- FAQ section
- Technical details about Real-ESRGAN

#### `IMPLEMENTATION_SUMMARY.md`
Technical implementation details including:
- Architecture overview
- DPI calculation logic
- GPU detection strategy
- Real-ESRGAN configuration
- Testing results
- Performance characteristics

#### Enhanced `README.md`
- New upscale.py section with full documentation
- Updated create_pdf.py CLI options
- Integration examples and workflows
- Performance notes
- GPU support information

---

## 🔧 Technical Details

### DPI Calculation
```
DPI = (image_pixels / card_dimension_mm) × 25.4
```

For standard MTG cards (63×88mm):
- 1200 DPI ≈ 2976 × 4157 pixels
- 800 DPI ≈ 1984 × 2771 pixels
- 300 DPI ≈ 744 × 1039 pixels

### Smart Upscaling Logic
```python
if current_dpi >= target_dpi:
    skip_upscaling()  # Already high resolution
else:
    scale_factor = target_dpi / current_dpi
    upscale_image(scale_factor)
```

### Real-ESRGAN Model
- **Model:** RealESRGAN_x4plus
- **Architecture:** RRDB (Residual in Residual Dense Block)
- **Native Scale:** 4x upscaling
- **Tile Size:** 400x400 (adjustable for memory)
- **FP16:** Enabled on CUDA for performance

---

## ⚡ Performance

### Processing Speed (per image)
- **GPU (CUDA/MPS):** 1-3 seconds
- **GPU (DirectML):** 2-5 seconds
- **CPU:** 10-30 seconds
- **Simple mode:** 0.5-2 seconds

### Memory Requirements
- **GPU:** 2-4GB VRAM
- **CPU:** 4-8GB RAM

### Quality
- **Real-ESRGAN:** Superior detail enhancement, reduces artifacts
- **Simple Lanczos:** Good for geometric upscaling, faster fallback

---

## 🐛 Bug Fixes

- Improved error handling for corrupted images
- Added atomic file operations to prevent data loss  
- Enhanced GPU detection for AMD/Intel GPUs on Windows via DirectML

---

## 🔄 Workflow Integration

### Recommended Workflow
```bash
# 1. Fetch card images (e.g., MTG plugin)
python plugins/mtg/fetch.py my_deck.txt mtga

# 2. Upscale to 1200 DPI
python upscale.py

# 3. Create PDF with enhancements
python create_pdf.py --saturation 1.1 --contrast 1.1 --load_offset

# Alternative: Combine steps 2-3
python create_pdf.py --upscale --saturation 1.1 --contrast 1.1 --load_offset
```

---

## 📦 Dependencies Added

### Core AI Libraries
- `torch` 2.4.1 - PyTorch deep learning framework
- `torchvision` 0.19.1 - Vision utilities
- `torch-directml` 0.2.5 - DirectML support (Windows)

### Image Processing
- `basicsr` 1.4.2 - Basic super-resolution framework
- `facexlib` 0.3.0 - Face detection and enhancement
- `gfpgan` 1.3.8 - Image restoration algorithms
- `realesrgan` 0.3.0 - Real-ESRGAN implementation
- `opencv-python` 4.9.0.80 - Computer vision library

---

## 🚀 Getting Started

### Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) For NVIDIA GPUs, install CUDA version:
pip uninstall torch torchvision torch-directml -y
pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cu118
```

### Quick Start
```bash
# Test upscaling
python upscale.py --help

# Upscale your cards
python upscale.py

# Create enhanced PDF
python create_pdf.py --upscale --saturation 1.2 --contrast 1.15
```

---

## 📌 Notes

- Upscaling is **optional** - all existing functionality works without it
- CPU processing works everywhere but is slower than GPU
- The `fix_realesrgan.py` script must be run after installing dependencies
- Transparency is preserved for PNG images
- Images already at or above target DPI are automatically skipped

---

## 🙏 Credits

- **Real-ESRGAN:** [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- **PyTorch:** [pytorch.org](https://pytorch.org/)
- **DirectML:** Microsoft's DirectML for AMD/Intel GPU support

---

## 📄 License

All new features maintain compatibility with the project's existing license (see LICENSE.md).

