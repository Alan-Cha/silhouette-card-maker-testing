#!/bin/bash
# Build script for create_pdf executable
# Ensure you run this from the project root (where requirements.txt is)

echo "Checking Python version..."
python3 --version

echo ""
echo "Note: If using Python 3.13+, some packages may need older versions."
echo "Consider using Python 3.11 or 3.12 for best compatibility."
echo ""

echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, deleting and recreating..."
    rm -rf venv
fi
python3 -m venv venv
echo "Virtual environment created."

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel --no-warn-script-location

echo ""
echo "Installing dependencies from requirements.txt..."
# Install all packages except numpy first
python -m pip install click==8.1.8 natsort==8.4.0 Pillow==11.3.0 pydantic==2.11.1 Requests==2.32.3 pypdfium2==4.30.0 split-image==2.0.1 --no-warn-script-location

echo ""
echo "Installing numpy (using compatible version)..."
# Try to install numpy from pre-built wheel, fall back to older version if needed
python -m pip install numpy --only-binary :all: --no-warn-script-location || python -m pip install numpy==1.26.4 --no-warn-script-location

echo ""
echo "Installing PyInstaller..."
python -m pip install pyinstaller --no-warn-script-location

echo ""
echo "Building executable with PyInstaller..."
python -m PyInstaller --onefile --add-data "assets:assets" create_pdf.py --distpath .

echo ""
echo "Deactivating virtual environment..."
deactivate

echo ""
echo "Cleaning up build artifacts..."
rm -rf build
rm -rf __pycache__
rm -f create_pdf.spec

echo ""
echo "Build complete. create_pdf executable is now in the project root."