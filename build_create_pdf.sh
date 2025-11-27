#!/bin/bash
# Build script for create_pdf executable
# Ensure you run this from the project root (where requirements.txt is)

# Install all dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Build the executable with PyInstaller
python3 -m pip install pyinstaller
python3 -m pyinstaller --onefile create_pdf.py --distpath .

# Clean up build artifacts
rm -rf build
rm -rf __pycache__
rm -f create_pdf.spec

echo "Build complete. create_pdf executable is now in the project root."