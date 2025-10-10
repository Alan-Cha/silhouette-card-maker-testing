"""
Quick fix script for Real-ESRGAN torchvision compatibility issue.

Run this after installing dependencies if you get:
"ModuleNotFoundError: No module named 'torchvision.transforms.functional_tensor'"
"""

import os
import sys

def fix_basicsr_compatibility():
    """Patch basicsr to work with newer torchvision versions."""
    
    # Find basicsr installation
    try:
        import basicsr
        basicsr_path = os.path.dirname(basicsr.__file__)
    except ImportError:
        # If import fails due to the bug, find it manually
        import site
        site_packages = site.getsitepackages()[0]
        basicsr_path = os.path.join(site_packages, 'basicsr')
        
        if not os.path.exists(basicsr_path):
            print("Error: basicsr not found. Please install it first:")
            print("  pip install basicsr")
            sys.exit(1)
    
    degradations_file = os.path.join(basicsr_path, 'data', 'degradations.py')
    
    if not os.path.exists(degradations_file):
        print(f"Error: degradations.py not found at {degradations_file}")
        sys.exit(1)
    
    # Read the file
    with open(degradations_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'try:' in content and 'from torchvision.transforms.functional import rgb_to_grayscale' in content:
        print("✅ basicsr is already patched!")
        return
    
    # Apply the patch
    old_import = 'from torchvision.transforms.functional_tensor import rgb_to_grayscale'
    new_import = '''try:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional import rgb_to_grayscale'''
    
    if old_import not in content:
        print("Warning: Expected import statement not found. File may already be modified.")
        print(f"Looking for: {old_import}")
        sys.exit(1)
    
    # Replace the import
    new_content = content.replace(old_import, new_import)
    
    # Write back
    with open(degradations_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Successfully patched: {degradations_file}")
    print("Real-ESRGAN should now work with newer torchvision versions!")

if __name__ == '__main__':
    fix_basicsr_compatibility()

