# Development Environment Setup

If you're starting with a fresh install of your operating system, follow these steps to set up your development environment:

## 1. Install Python

- Download Python from the official website: https://www.python.org/downloads/
- Run the installer and **check the box to add Python to your PATH**.
- Verify installation:
   ```powershell
   python --version
   ```

## 2. Install Node.js

- Download Node.js (LTS version recommended) from: https://nodejs.org/
- Run the installer and follow the prompts.
- Verify installation:
   ```powershell
   node --version
   npm --version
   ```

Once Python and Node.js are installed, continue with the project setup steps below.
# Silhouette Card Maker GUI

- Node.js (v18 or newer recommended)
- Python (v3.10+ recommended)
- All Python dependencies listed in the project root `requirements.txt`
## 1. Install Python

- **Windows:** Download Python from the official website: https://www.python.org/downloads/
   - Run the installer and **check the box to add Python to your PATH**.
- **Linux/Mac:** Install via your package manager or download from the website.
   - Ubuntu/Debian:
      ```bash
      sudo apt update && sudo apt install python3 python3-pip
      ```
   - Mac (Homebrew):
      ```bash
      brew install python3
      ```
- Verify installation:
   ```powershell
   python --version
   ```
   ```bash
   python3 --version
   ```

## Setup

   npm install
   ```

2. **Install Python dependencies**
## 2. Install Node.js

- **Windows:** Download Node.js (LTS version recommended) from: https://nodejs.org/
   - Run the installer and follow the prompts.
- **Linux/Mac:** Install via your package manager or download from the website.
   - Ubuntu/Debian:
      ```bash
      sudo apt update && sudo apt install nodejs npm
      ```
   - Mac (Homebrew):
      ```bash
      brew install node
      ```
- Verify installation:
   ```powershell
   node --version
   npm --version
   ```
   ```bash
   node --version
   npm --version
   ```
   ```powershell
   cd ..
   python -m pip install -r requirements.txt
   ```

3. **Build the Python executable**
   (Optional, for standalone PDF generation)

   **Windows:**
   ```powershell
   .\build_entrypoints.bat
   ```

   **macOS/Linux:**
   ```bash
   ./build_entrypoints.sh
   ```

   This will create the PDF generator executable in the project root:
   - Windows: `create_pdf.exe`
   - macOS/Linux: `create_pdf`

   The build script will:
   1. Install/upgrade pip
   2. Install required Python packages
   3. Install PyInstaller
   4. Build a standalone executable
   5. Clean up temporary build files

## Running the GUI

1. **Start the Electron app**
   ```powershell
   cd GUI
   npm run start
   ```

The GUI will open in a new window. You can generate PDFs, view images, and use all available features.

## Development Notes
- The Electron app communicates with Python via IPC and can run either the script or the compiled executable.
- For advanced features, see the main project README and the scripts in the root directory.

## Troubleshooting
- If you see errors about missing Python modules, ensure you installed all dependencies from `requirements.txt`.
- If you see errors about missing `create_pdf.exe`, run the build script as shown above.
- For Windows, use PowerShell or Command Prompt. For Mac/Linux, adapt commands as needed.

---

For more help, see the main project README or contact the project maintainer.
