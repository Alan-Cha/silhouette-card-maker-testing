@echo off
REM Build script for create_pdf.exe
REM Ensure you run this from the project root (where requirements.txt is)

REM Install all dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Build the executable with PyInstaller
python -m pip install pyinstaller
python -m pyinstaller --onefile create_pdf.py --distpath .

REM Clean up build artifacts
rmdir /s /q build
rmdir /s /q __pycache__
del create_pdf.spec

echo Build complete. create_pdf.exe is now in the project root.
