import os
import sys
from pathlib import Path
from typing import List, Tuple
import json
import tempfile
import shutil

import click
from PIL import Image
import numpy as np

# Card size dimensions in millimeters
CARD_DIMENSIONS_MM = {
    'standard': (63, 88),
    'standard_double': (126, 88),
    'japanese': (59, 86),
    'poker': (63.5, 88.9),
    'poker_half': (44.45, 62.23),
    'bridge': (57.15, 88.9),
    'bridge_square': (57.15, 57.15),
    'tarot': (69.85, 120.65),
    'domino': (44.45, 88.9),
    'domino_square': (44.45, 44.45)
}

def setup_realesrgan_model(gpu_id=None):
    """
    Initialize the Real-ESRGAN model with GPU support if available.
    
    Args:
        gpu_id: GPU device ID (None for auto-detect, -1 for CPU)
    
    Returns:
        RealESRGANer instance
    """
    try:
        import torch
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
        from realesrgan.archs.srvgg_arch import SRVGGNetCompact
    except ImportError as e:
        print("Error: Real-ESRGAN dependencies not installed.")
        print("Please install with: pip install realesrgan basicsr facexlib gfpgan")
        print(f"Missing module: {e}")
        sys.exit(1)
    
    # Determine device
    if gpu_id is None:
        if torch.cuda.is_available():
            device = 'cuda'
            gpu_id = 0
            print(f"GPU detected: Using CUDA (NVIDIA)")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = 'mps'
            gpu_id = 0
            print(f"GPU detected: Using Apple MPS")
        else:
            # Check for DirectML (AMD/Intel on Windows)
            try:
                import torch_directml
                if torch_directml.is_available():
                    device = torch_directml.device()
                    gpu_id = 0
                    print(f"GPU detected: Using DirectML (AMD/Intel)")
                else:
                    device = 'cpu'
                    gpu_id = None
                    print("No GPU detected: Using CPU (this will be slower)")
            except ImportError:
                device = 'cpu'
                gpu_id = None
                print("No GPU detected: Using CPU (this will be slower)")
    elif gpu_id == -1:
        device = 'cpu'
        gpu_id = None
        print("Using CPU as requested")
    else:
        device = 'cuda'
        print(f"Using CUDA GPU {gpu_id}")
    
    # Use RealESRGAN_x4plus model (good for general photos/images)
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    
    # Determine model path (download if needed)
    model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
    
    # For DirectML, we need to handle device differently
    if isinstance(device, str) and device not in ['cuda', 'cpu', 'mps']:
        # DirectML or other custom device
        # Move model to DirectML device
        model = model.to(device)
        # Initialize upsampler with cpu as device (model is already on correct device)
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=400,
            tile_pad=10,
            pre_pad=0,
            half=False,  # DirectML doesn't support FP16 the same way
            device=device  # Pass device directly instead of gpu_id
        )
    else:
        # Initialize upsampler normally for CUDA/MPS/CPU
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=400,  # Tile size for processing (adjust based on GPU memory)
            tile_pad=10,
            pre_pad=0,
            half=True if device == 'cuda' else False,  # FP16 for CUDA
            gpu_id=gpu_id
        )
    
    return upsampler

def calculate_current_dpi(image_width: int, image_height: int, card_size: str) -> Tuple[float, float]:
    """
    Calculate the current DPI of an image based on card dimensions.
    
    Args:
        image_width: Width of image in pixels
        image_height: Height of image in pixels
        card_size: Card size type (e.g., 'standard', 'poker')
    
    Returns:
        Tuple of (dpi_width, dpi_height)
    """
    if card_size not in CARD_DIMENSIONS_MM:
        raise ValueError(f"Unknown card size: {card_size}")
    
    card_width_mm, card_height_mm = CARD_DIMENSIONS_MM[card_size]
    
    # Convert mm to inches (1 inch = 25.4 mm)
    card_width_in = card_width_mm / 25.4
    card_height_in = card_height_mm / 25.4
    
    # Calculate DPI
    dpi_width = image_width / card_width_in
    dpi_height = image_height / card_height_in
    
    return dpi_width, dpi_height

def determine_scale_factor(current_dpi: float, target_dpi: int = 1200) -> float:
    """
    Determine the scale factor needed to reach target DPI.
    
    Args:
        current_dpi: Current DPI of the image
        target_dpi: Target DPI (default: 1200)
    
    Returns:
        Scale factor (returns 1.0 if already at or above target)
    """
    if current_dpi >= target_dpi:
        return 1.0
    
    scale_factor = target_dpi / current_dpi
    return scale_factor

def upscale_image_simple(image_path: str, scale_factor: float) -> Image.Image:
    """
    Upscale image using simple Lanczos resampling (fallback method).
    
    Args:
        image_path: Path to the image
        scale_factor: Scale factor for upscaling
    
    Returns:
        Upscaled PIL Image
    """
    img = Image.open(image_path)
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    upscaled = img.resize(new_size, Image.Resampling.LANCZOS)
    return upscaled

def upscale_image(image_path: str, scale_factor: float, upsampler) -> Image.Image:
    """
    Upscale an image using Real-ESRGAN.
    
    Args:
        image_path: Path to the image
        scale_factor: Scale factor for upscaling
        upsampler: RealESRGANer instance
    
    Returns:
        Upscaled PIL Image
    """
    # Load image
    img = Image.open(image_path)
    
    # Convert to numpy array
    img_np = np.array(img)
    
    # Handle images with alpha channel
    has_alpha = False
    if img_np.shape[2] == 4:
        has_alpha = True
        alpha_channel = img_np[:, :, 3]
        img_np = img_np[:, :, :3]  # Remove alpha for processing
    
    # Real-ESRGAN expects BGR format
    img_np = img_np[:, :, ::-1]
    
    try:
        # Upscale using Real-ESRGAN (4x by default)
        output, _ = upsampler.enhance(img_np, outscale=scale_factor/4 if scale_factor >= 4 else 1.0)
        
        # Convert back to RGB
        output = output[:, :, ::-1]
        
        # If we need additional scaling beyond 4x
        upscaled_img = Image.fromarray(output)
        if scale_factor > 4:
            additional_scale = scale_factor / 4
            new_size = (int(upscaled_img.width * additional_scale), int(upscaled_img.height * additional_scale))
            upscaled_img = upscaled_img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Re-add alpha channel if it existed
        if has_alpha:
            # Scale alpha channel to match new size
            alpha_img = Image.fromarray(alpha_channel, mode='L')
            alpha_img = alpha_img.resize(upscaled_img.size, Image.Resampling.LANCZOS)
            upscaled_img.putalpha(alpha_img)
        
        return upscaled_img
        
    except Exception as e:
        print(f"Error during Real-ESRGAN upscaling: {e}")
        print("Falling back to simple Lanczos upscaling...")
        return upscale_image_simple(image_path, scale_factor)

def process_directory(
    dir_path: str,
    card_size: str,
    target_dpi: int = 1200,
    force: bool = False,
    upsampler = None,
    use_simple: bool = False
) -> Tuple[int, int]:
    """
    Process all images in a directory, upscaling as needed.
    
    Args:
        dir_path: Path to the directory
        card_size: Card size type for DPI calculation
        target_dpi: Target DPI (default: 1200)
        force: Force upscale even if already high-res
        upsampler: RealESRGANer instance (None for simple upscaling)
        use_simple: Use simple Lanczos upscaling instead of Real-ESRGAN
    
    Returns:
        Tuple of (processed_count, skipped_count)
    """
    if not os.path.exists(dir_path):
        return 0, 0
    
    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in image_extensions:
                image_files.append(file_path)
    
    if not image_files:
        return 0, 0
    
    processed = 0
    skipped = 0
    
    for image_path in image_files:
        try:
            # Load image to check dimensions
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Calculate current DPI
            dpi_w, dpi_h = calculate_current_dpi(width, height, card_size)
            avg_dpi = (dpi_w + dpi_h) / 2
            
            # Determine if upscaling is needed
            if not force and avg_dpi >= target_dpi:
                print(f"  Skipping {os.path.basename(image_path)}: Already {avg_dpi:.0f} DPI")
                skipped += 1
                continue
            
            # Calculate scale factor
            scale_factor = determine_scale_factor(avg_dpi, target_dpi)
            
            if scale_factor <= 1.0:
                print(f"  Skipping {os.path.basename(image_path)}: Already at target DPI")
                skipped += 1
                continue
            
            print(f"  Upscaling {os.path.basename(image_path)}: {avg_dpi:.0f} DPI -> {target_dpi} DPI (scale: {scale_factor:.2f}x)")
            
            # Upscale the image
            if use_simple or upsampler is None:
                upscaled = upscale_image_simple(image_path, scale_factor)
            else:
                upscaled = upscale_image(image_path, scale_factor, upsampler)
            
            # Save to temporary file first to avoid corrupting original on error
            temp_fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(image_path)[1])
            os.close(temp_fd)  # Close file descriptor, we'll use PIL to write
            
            try:
                # Preserve the original format
                file_format = os.path.splitext(image_path)[1].lower()
                if file_format == '.jpg' or file_format == '.jpeg':
                    upscaled.save(temp_path, 'JPEG', quality=95)
                else:
                    upscaled.save(temp_path)
                
                # Verify the saved file can be opened
                with Image.open(temp_path) as verify_img:
                    verify_img.load()  # Force load to catch truncation errors
                
                # If successful, replace original with upscaled version
                shutil.move(temp_path, image_path)
                processed += 1
                
            except Exception as save_error:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise save_error  # Re-raise to be caught by outer except
            
        except Exception as e:
            print(f"  Error processing {os.path.basename(image_path)}: {e}")
            continue
    
    return processed, skipped

@click.command()
@click.option('--front_dir_path', default='game/front', show_default=True, help='The path to the directory containing the card fronts.')
@click.option('--back_dir_path', default='game/back', show_default=True, help='The path to the directory containing one or more card backs.')
@click.option('--double_sided_dir_path', default='game/double_sided', show_default=True, help='The path to the directory containing card backs for double-sided cards.')
@click.option('--card_size', default='standard', type=click.Choice(list(CARD_DIMENSIONS_MM.keys()), case_sensitive=False), show_default=True, help='The card size for DPI calculation.')
@click.option('--target_dpi', default=1200, type=click.IntRange(min=300), show_default=True, help='Target DPI for upscaling.')
@click.option('--force', is_flag=True, default=False, help='Force upscale even if already at target DPI.')
@click.option('--use_simple', is_flag=True, default=False, help='Use simple Lanczos upscaling instead of Real-ESRGAN.')
@click.option('--gpu_id', type=int, default=None, help='GPU device ID (None=auto, -1=CPU).')
@click.version_option("1.0.0")
def cli(
    front_dir_path: str,
    back_dir_path: str,
    double_sided_dir_path: str,
    card_size: str,
    target_dpi: int,
    force: bool,
    use_simple: bool,
    gpu_id: int
):
    """
    Upscale card images to target DPI using Real-ESRGAN or simple Lanczos resampling.
    
    This tool intelligently upscales images only when needed, preserving image quality
    and utilizing GPU acceleration when available.
    """
    print("=" * 60)
    print("Card Image Upscaler")
    print("=" * 60)
    print(f"Card size: {card_size}")
    print(f"Target DPI: {target_dpi}")
    print(f"Force upscale: {force}")
    print()
    
    # Initialize upsampler if not using simple method
    upsampler = None
    if not use_simple:
        try:
            print("Initializing Real-ESRGAN model...")
            upsampler = setup_realesrgan_model(gpu_id)
            print()
        except Exception as e:
            print(f"Failed to initialize Real-ESRGAN: {e}")
            print("Falling back to simple Lanczos upscaling...")
            use_simple = True
            print()
    
    if use_simple:
        print("Using simple Lanczos upscaling")
        print()
    
    # Process each directory
    total_processed = 0
    total_skipped = 0
    
    directories = [
        ('Front images', front_dir_path),
        ('Back images', back_dir_path),
        ('Double-sided images', double_sided_dir_path)
    ]
    
    for name, dir_path in directories:
        if not os.path.exists(dir_path):
            print(f"{name} ({dir_path}): Directory not found, skipping...")
            continue
        
        print(f"Processing {name} ({dir_path})...")
        processed, skipped = process_directory(
            dir_path,
            card_size,
            target_dpi,
            force,
            upsampler,
            use_simple
        )
        
        total_processed += processed
        total_skipped += skipped
        print()
    
    print("=" * 60)
    print(f"Upscaling complete!")
    print(f"  Processed: {total_processed} images")
    print(f"  Skipped: {total_skipped} images")
    print("=" * 60)

def upscale_for_create_pdf(
    front_dir_path: str,
    back_dir_path: str,
    double_sided_dir_path: str,
    card_size: str,
    target_dpi: int = 1200
):
    """
    Upscale images for use with create_pdf.py. Called internally from create_pdf.
    
    Args:
        front_dir_path: Path to front images
        back_dir_path: Path to back images
        double_sided_dir_path: Path to double-sided images
        card_size: Card size type
        target_dpi: Target DPI (default: 1200)
    """
    print("Starting automatic upscaling...")
    
    # Try to use Real-ESRGAN, fall back to simple if needed
    upsampler = None
    use_simple = False
    
    try:
        upsampler = setup_realesrgan_model(gpu_id=None)
    except:
        use_simple = True
        print("Using simple Lanczos upscaling (Real-ESRGAN not available)")
    
    # Process directories
    directories = [front_dir_path, back_dir_path, double_sided_dir_path]
    
    for dir_path in directories:
        if os.path.exists(dir_path):
            process_directory(
                dir_path,
                card_size,
                target_dpi,
                force=False,
                upsampler=upsampler,
                use_simple=use_simple
            )
    
    print("Upscaling complete.\n")

if __name__ == '__main__':
    cli()

