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

This folder contains the Electron-based graphical user interface for the Silhouette Card Maker project.

## Prerequisites
- Node.js (v18 or newer recommended)
- Python (v3.10+ recommended)
- All Python dependencies listed in the project root `requirements.txt`

## Setup

1. **Install Node.js dependencies**
   ```powershell
   cd GUI
   npm install
   ```

2. **Install Python dependencies**
   ```powershell
   cd ..
   python -m pip install -r requirements.txt
   ```

3. **Build the Python executable**
   (Optional, for standalone PDF generation)
   ```powershell
   .\build_create_pdf.bat
   ```
   This will create `create_pdf.exe` in the project root.

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
