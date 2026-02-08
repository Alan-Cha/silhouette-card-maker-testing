#!/usr/bin/env python3
"""
DXF to Studio3 Batch Converter

This script automates Silhouette Studio to convert DXF files to .studio3 format.
It uses GUI automation (pyautogui) to control Silhouette Studio.

Requirements:
    pip install pyautogui pywinauto pillow

Usage:
    python dxf_to_studio3.py input_folder [output_folder]

    If output_folder is not specified, .studio3 files are saved alongside the DXF files.

Notes:
    - Silhouette Studio must be installed
    - The script will take control of keyboard/mouse - don't use the computer during conversion
    - Move mouse to top-left corner to abort (pyautogui failsafe)
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

# Check for required libraries
try:
    import pyautogui
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui pillow")
    sys.exit(1)

try:
    from pywinauto import Application, Desktop
    from pywinauto.keyboard import send_keys
    from pywinauto.findwindows import ElementNotFoundError
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False
    print("WARNING: pywinauto not installed. Using pyautogui only (less reliable).")
    print("         For better reliability, run: pip install pywinauto")


# Configuration
SILHOUETTE_STUDIO_PATH = r"C:\Program Files\Silhouette America\Silhouette Studio\Silhouette Studio.exe"
STARTUP_WAIT = 8  # Seconds to wait for Silhouette Studio to start
ACTION_DELAY = 0.5  # Delay between GUI actions
SAVE_DELAY = 2  # Extra delay after save operations


class SilhouetteAutomation:
    """Automates Silhouette Studio for file conversion."""

    def __init__(self, studio_path=SILHOUETTE_STUDIO_PATH):
        self.studio_path = studio_path
        self.app = None
        self.main_window = None

        # Configure pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions

    def start_silhouette_studio(self):
        """Launch Silhouette Studio and wait for it to be ready."""
        print(f"Starting Silhouette Studio...")

        if not os.path.exists(self.studio_path):
            raise FileNotFoundError(f"Silhouette Studio not found at: {self.studio_path}")

        # Start the application
        subprocess.Popen([self.studio_path])

        # Wait for startup
        print(f"Waiting {STARTUP_WAIT} seconds for startup...")
        time.sleep(STARTUP_WAIT)

        if HAS_PYWINAUTO:
            try:
                # Connect to the running application
                self.app = Application(backend="uia").connect(
                    path=self.studio_path,
                    timeout=30
                )
                # Find main window
                self.main_window = self.app.window(title_re=".*Silhouette Studio.*")
                self.main_window.wait('ready', timeout=30)
                print("Connected to Silhouette Studio")
            except Exception as e:
                print(f"Warning: Could not connect via pywinauto: {e}")
                print("Falling back to pyautogui only")
                self.app = None

    def close_silhouette_studio(self):
        """Close Silhouette Studio."""
        print("Closing Silhouette Studio...")
        if self.app and self.main_window:
            try:
                self.main_window.close()
            except:
                pass
        else:
            # Use Alt+F4
            pyautogui.hotkey('alt', 'F4')
        time.sleep(1)

        # Handle "Save changes?" dialog if it appears
        self._handle_save_dialog(save=False)

    def _handle_save_dialog(self, save=False):
        """Handle the 'Save changes?' dialog."""
        time.sleep(0.5)
        # Press N for "No" or Y for "Yes" / Enter for default
        if not save:
            pyautogui.press('n')  # Don't save
        else:
            pyautogui.press('y')  # Save
        time.sleep(0.3)

    def open_file(self, filepath):
        """Open a DXF file in Silhouette Studio."""
        filepath = os.path.abspath(filepath)
        print(f"Opening: {filepath}")

        # Use Ctrl+O to open file dialog
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(ACTION_DELAY * 2)

        # Type the file path
        # Clear any existing text first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)

        # Type the path - pyautogui.write() is slow, use clipboard instead
        self._type_text(filepath)
        time.sleep(ACTION_DELAY)

        # Press Enter to open
        pyautogui.press('enter')
        time.sleep(ACTION_DELAY * 3)  # Wait for file to load

    def _type_text(self, text):
        """Type text using clipboard (faster than pyautogui.write)."""
        import subprocess
        # Copy text to clipboard
        subprocess.run(['clip'], input=text.encode('utf-16-le'), check=True)
        # Paste
        pyautogui.hotkey('ctrl', 'v')

    def save_as_studio3(self, output_path):
        """Save the current document as a .studio3 file."""
        output_path = os.path.abspath(output_path)

        # Ensure .studio3 extension
        if not output_path.lower().endswith('.studio3'):
            output_path = os.path.splitext(output_path)[0] + '.studio3'

        print(f"Saving as: {output_path}")

        # Use Ctrl+Shift+S for "Save As"
        pyautogui.hotkey('ctrl', 'shift', 's')
        time.sleep(ACTION_DELAY * 2)

        # Type the output path
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        self._type_text(output_path)
        time.sleep(ACTION_DELAY)

        # Press Enter to save
        pyautogui.press('enter')
        time.sleep(SAVE_DELAY)

        # Handle overwrite confirmation if file exists
        if os.path.exists(output_path):
            time.sleep(0.3)
            pyautogui.press('y')  # Yes to overwrite
            time.sleep(SAVE_DELAY)

    def new_document(self):
        """Create a new document (close current without saving)."""
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(ACTION_DELAY)
        self._handle_save_dialog(save=False)
        time.sleep(ACTION_DELAY)

    def convert_file(self, input_dxf, output_studio3):
        """Convert a single DXF file to .studio3 format."""
        self.open_file(input_dxf)
        self.save_as_studio3(output_studio3)
        self.new_document()


def find_dxf_files(folder):
    """Find all DXF files in a folder."""
    folder = Path(folder)
    dxf_files = list(folder.glob("*.dxf")) + list(folder.glob("*.DXF"))
    return sorted(dxf_files)


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert DXF files to Silhouette Studio .studio3 format"
    )
    parser.add_argument(
        "input_folder",
        help="Folder containing DXF files to convert"
    )
    parser.add_argument(
        "output_folder",
        nargs="?",
        default=None,
        help="Output folder for .studio3 files (default: same as input)"
    )
    parser.add_argument(
        "--studio-path",
        default=SILHOUETTE_STUDIO_PATH,
        help="Path to Silhouette Studio executable"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be converted without actually converting"
    )

    args = parser.parse_args()

    # Validate input folder
    input_folder = Path(args.input_folder)
    if not input_folder.exists():
        print(f"ERROR: Input folder does not exist: {input_folder}")
        sys.exit(1)

    # Set output folder
    output_folder = Path(args.output_folder) if args.output_folder else input_folder
    output_folder.mkdir(parents=True, exist_ok=True)

    # Find DXF files
    dxf_files = find_dxf_files(input_folder)

    if not dxf_files:
        print(f"No DXF files found in: {input_folder}")
        sys.exit(0)

    print(f"Found {len(dxf_files)} DXF files to convert:")
    for dxf_file in dxf_files:
        output_file = output_folder / (dxf_file.stem + ".studio3")
        print(f"  {dxf_file.name} -> {output_file.name}")

    if args.dry_run:
        print("\nDry run - no files converted.")
        sys.exit(0)

    # Confirm before proceeding
    print("\n" + "="*60)
    print("IMPORTANT: This script will take control of your mouse/keyboard.")
    print("Do not use the computer during conversion.")
    print("Move mouse to TOP-LEFT CORNER to abort at any time.")
    print("="*60)

    response = input("\nProceed with conversion? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    # Start conversion
    automation = SilhouetteAutomation(args.studio_path)

    try:
        automation.start_silhouette_studio()

        successful = 0
        failed = 0

        for i, dxf_file in enumerate(dxf_files):
            output_file = output_folder / (dxf_file.stem + ".studio3")
            print(f"\n[{i+1}/{len(dxf_files)}] Converting: {dxf_file.name}")

            try:
                automation.convert_file(str(dxf_file), str(output_file))
                successful += 1
                print(f"  Success!")
            except Exception as e:
                failed += 1
                print(f"  FAILED: {e}")

        print(f"\n{'='*60}")
        print(f"Conversion complete: {successful} successful, {failed} failed")

    except KeyboardInterrupt:
        print("\n\nAborted by user.")
    except pyautogui.FailSafeException:
        print("\n\nAborted - mouse moved to corner (failsafe triggered).")
    finally:
        try:
            automation.close_silhouette_studio()
        except:
            pass


if __name__ == "__main__":
    main()
