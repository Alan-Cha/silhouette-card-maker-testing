@echo off
REM Build script for create_pdf.exe
REM Ensure you run this from the project root (where requirements.txt is)

echo Checking Python version...
python --version

echo.
echo Note: If using Python 3.13+, some packages may need older versions.
echo Consider using Python 3.11 or 3.12 for best compatibility.
echo.

echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, deleting and recreating...
    rmdir /s /q venv
)
py -3.12 -m venv venv
echo Virtual environment created.

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel --no-warn-script-location

echo.
echo Installing dependencies from requirements.txt...
REM Install all packages except numpy first
python -m pip install click==8.1.8 natsort==8.4.0 Pillow==11.3.0 pydantic==2.11.1 Requests==2.32.3 pypdfium2==4.30.0 split-image==2.0.1 --no-warn-script-location

echo.
echo Installing numpy (using compatible version)...
REM Try to install numpy from pre-built wheel, fall back to older version if needed
python -m pip install numpy --only-binary :all: --no-warn-script-location || python -m pip install numpy==1.26.4 --no-warn-script-location

echo.
echo Installing PyInstaller...
python -m pip install pyinstaller --no-warn-script-location

echo.
echo Building executable with PyInstaller...
python -m PyInstaller --onefile --add-data "assets;assets" create_pdf.py --distpath .

echo.
echo Deactivating virtual environment...
call venv\Scripts\deactivate.bat

echo.
echo Cleaning up build artifacts...
rmdir /s /q build
rmdir /s /q __pycache__
del create_pdf.spec

echo.
echo Build complete. create_pdf.exe is now in the project root.
