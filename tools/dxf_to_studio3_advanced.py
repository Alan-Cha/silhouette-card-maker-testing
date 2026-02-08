#!/usr/bin/env python3
"""
Advanced DXF to Studio3 Converter with Full Automation

This script automates Silhouette Studio with mouse interactions for:
- Page orientation (portrait/landscape)
- Centering cutting paths
- Registration mark settings

Requirements:
    pip install pyautogui pywinauto pillow opencv-python

Usage:
    python dxf_to_studio3_advanced.py input.dxf output.studio3 --orientation landscape

Window Size Strategy:
    The script forces Silhouette Studio to a fixed window size (1920x1080)
    to ensure consistent UI element positions. If your screen is smaller,
    adjust WINDOW_WIDTH and WINDOW_HEIGHT.
"""

import os
import sys
import time
import subprocess
import argparse
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui pillow")
    sys.exit(1)

try:
    from pywinauto import Application, Desktop
    from pywinauto.keyboard import send_keys
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False
    print("WARNING: pywinauto not installed. Window management disabled.")
    print("         Run: pip install pywinauto")

# Try to import opencv for better image matching
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


# =============================================================================
# Configuration
# =============================================================================

SILHOUETTE_STUDIO_PATH = r"C:\Program Files\Silhouette America\Silhouette Studio\Silhouette Studio.exe"

# Fixed window size for consistent coordinates
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_X = 0
WINDOW_Y = 0

# Timing
STARTUP_WAIT = 10  # Seconds to wait for startup
ACTION_DELAY = 0.5  # Delay between actions
SCROLL_DELAY = 0.3
SAVE_DELAY = 2.0


class Orientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class RegistrationSettings:
    """Settings for registration marks."""
    enabled: bool = True
    length_mm: float = 10.0
    thickness_mm: float = 0.5
    inset_mm: float = 5.0


# =============================================================================
# UI Element Coordinates (for 1920x1080 window)
# These need to be calibrated for your specific Silhouette Studio version
# =============================================================================

@dataclass
class UICoordinates:
    """
    UI element coordinates for Silhouette Studio.

    These are relative to the application window (not screen).
    Calibrate these by running the calibration tool.
    """
    # Sidebar tools (left side)
    sidebar_x: int = 45  # X position of sidebar icons

    # Tool positions (Y coordinates)
    page_setup_y: int = 180
    transform_y: int = 220
    print_cut_y: int = 380

    # Page Setup panel
    page_setup_panel_x: int = 200
    orientation_section_y: int = 400
    portrait_btn_offset: Tuple[int, int] = (20, 0)
    landscape_btn_offset: Tuple[int, int] = (60, 0)

    # Transform panel
    transform_panel_x: int = 200
    center_to_page_y: int = 300

    # Print & Cut panel
    regmark_enable_y: int = 300
    regmark_length_y: int = 340
    regmark_thickness_y: int = 380
    regmark_inset_y: int = 420


# Default coordinates - adjust these for your setup
UI = UICoordinates()


# =============================================================================
# Utility Functions
# =============================================================================

def get_window_offset() -> Tuple[int, int]:
    """Get the top-left corner of the Silhouette Studio window."""
    if not HAS_PYWINAUTO:
        return (0, 0)

    try:
        app = Application(backend="uia").connect(path=SILHOUETTE_STUDIO_PATH)
        window = app.window(title_re=".*Silhouette Studio.*")
        rect = window.rectangle()
        return (rect.left, rect.top)
    except:
        return (0, 0)


def click_window_relative(x: int, y: int, offset: Tuple[int, int] = None):
    """Click at a position relative to the window."""
    if offset is None:
        offset = get_window_offset()

    abs_x = offset[0] + x
    abs_y = offset[1] + y

    pyautogui.click(abs_x, abs_y)
    time.sleep(ACTION_DELAY)


def scroll_in_panel(amount: int, x: int = None, y: int = None):
    """Scroll within a panel. Negative = down, positive = up."""
    if x and y:
        offset = get_window_offset()
        pyautogui.moveTo(offset[0] + x, offset[1] + y)

    pyautogui.scroll(amount)
    time.sleep(SCROLL_DELAY)


def type_in_field(value: str):
    """Clear a field and type a new value."""
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.write(str(value))
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(ACTION_DELAY)


def set_clipboard(text: str):
    """Set clipboard text (Windows)."""
    subprocess.run(['clip'], input=text.encode('utf-16-le'), check=True)


def paste():
    """Paste from clipboard."""
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)


# =============================================================================
# Image-Based Element Finding (Optional, more robust)
# =============================================================================

class ImageFinder:
    """Find UI elements using image recognition."""

    def __init__(self, icons_folder: Path):
        self.icons_folder = icons_folder
        self.cache = {}

    def find(self, icon_name: str, confidence: float = 0.9) -> Optional[Tuple[int, int]]:
        """
        Find an icon on screen and return its center coordinates.

        Args:
            icon_name: Name of the icon file (without extension)
            confidence: Match confidence (0.0 to 1.0)

        Returns:
            (x, y) center coordinates, or None if not found
        """
        icon_path = self.icons_folder / f"{icon_name}.png"

        if not icon_path.exists():
            print(f"Warning: Icon image not found: {icon_path}")
            return None

        try:
            location = pyautogui.locateOnScreen(
                str(icon_path),
                confidence=confidence if HAS_OPENCV else None
            )
            if location:
                return pyautogui.center(location)
        except Exception as e:
            print(f"Image search error: {e}")

        return None

    def click(self, icon_name: str, confidence: float = 0.9) -> bool:
        """Find and click an icon. Returns True if successful."""
        pos = self.find(icon_name, confidence)
        if pos:
            pyautogui.click(pos)
            time.sleep(ACTION_DELAY)
            return True
        return False


# =============================================================================
# Silhouette Studio Automation
# =============================================================================

class SilhouetteAutomation:
    """Automates Silhouette Studio operations."""

    def __init__(self, studio_path: str = SILHOUETTE_STUDIO_PATH, calibration_file: Path = None):
        self.studio_path = studio_path
        self.app = None
        self.window = None
        self.window_offset = (0, 0)

        # Load calibration if available
        cal_file = calibration_file or CALIBRATION_FILE
        self.calibration = load_calibration(cal_file)
        if self.calibration:
            print(f"Loaded calibration for Silhouette Studio {self.calibration.get('silhouette_studio_version', 'unknown')}")
        else:
            print("No calibration file found. Using default coordinates.")
            print(f"Run with --calibrate to create: {cal_file}")

        # Optional image-based finding
        icons_folder = Path(__file__).parent / "silhouette_icons"
        self.image_finder = ImageFinder(icons_folder) if icons_folder.exists() else None

    def start(self):
        """Start Silhouette Studio with fixed window size."""
        print(f"Starting Silhouette Studio...")

        if not os.path.exists(self.studio_path):
            raise FileNotFoundError(f"Not found: {self.studio_path}")

        subprocess.Popen([self.studio_path])
        print(f"Waiting {STARTUP_WAIT}s for startup...")
        time.sleep(STARTUP_WAIT)

        # Resize window to fixed size
        if HAS_PYWINAUTO:
            try:
                self.app = Application(backend="uia").connect(
                    path=self.studio_path,
                    timeout=30
                )
                self.window = self.app.window(title_re=".*Silhouette Studio.*")
                self.window.restore()
                self.window.move_window(
                    x=WINDOW_X,
                    y=WINDOW_Y,
                    width=WINDOW_WIDTH,
                    height=WINDOW_HEIGHT
                )
                time.sleep(1)
                self.window_offset = (WINDOW_X, WINDOW_Y)
                print(f"Window set to {WINDOW_WIDTH}x{WINDOW_HEIGHT} at ({WINDOW_X}, {WINDOW_Y})")
            except Exception as e:
                print(f"Warning: Could not set window size: {e}")

    def close(self):
        """Close Silhouette Studio."""
        print("Closing Silhouette Studio...")
        pyautogui.hotkey('alt', 'F4')
        time.sleep(0.5)
        pyautogui.press('n')  # Don't save
        time.sleep(1)

    def _click(self, x: int, y: int):
        """Click at window-relative coordinates."""
        abs_x = self.window_offset[0] + x
        abs_y = self.window_offset[1] + y
        pyautogui.click(abs_x, abs_y)
        time.sleep(ACTION_DELAY)

    def _click_element(self, element_id: str, fallback_x: int = None, fallback_y: int = None):
        """
        Click a calibrated element by ID.

        Uses calibration data if available, otherwise falls back to provided coordinates.
        """
        if self.calibration and element_id in self.calibration.get("elements", {}):
            elem = self.calibration["elements"][element_id]
            x = elem["relative"]["x"]
            y = elem["relative"]["y"]
            self._click(x, y)
            return True
        elif fallback_x is not None and fallback_y is not None:
            self._click(fallback_x, fallback_y)
            return True
        else:
            print(f"Warning: Element '{element_id}' not calibrated and no fallback provided")
            return False

    def _scroll(self, amount: int, x: int, y: int):
        """Scroll at a specific position."""
        abs_x = self.window_offset[0] + x
        abs_y = self.window_offset[1] + y
        pyautogui.moveTo(abs_x, abs_y)
        pyautogui.scroll(amount)
        time.sleep(SCROLL_DELAY)

    # -------------------------------------------------------------------------
    # File Operations
    # -------------------------------------------------------------------------

    def open_file(self, filepath: str):
        """Open a DXF file."""
        filepath = os.path.abspath(filepath)
        print(f"Opening: {filepath}")

        pyautogui.hotkey('ctrl', 'o')
        time.sleep(ACTION_DELAY * 2)

        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        set_clipboard(filepath)
        paste()
        time.sleep(ACTION_DELAY)

        pyautogui.press('enter')
        time.sleep(ACTION_DELAY * 3)

    def save_as(self, output_path: str):
        """Save as .studio3 file."""
        output_path = os.path.abspath(output_path)
        if not output_path.lower().endswith('.studio3'):
            output_path = os.path.splitext(output_path)[0] + '.studio3'

        print(f"Saving: {output_path}")

        pyautogui.hotkey('ctrl', 'shift', 's')
        time.sleep(ACTION_DELAY * 2)

        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        set_clipboard(output_path)
        paste()
        time.sleep(ACTION_DELAY)

        pyautogui.press('enter')
        time.sleep(SAVE_DELAY)

        # Handle overwrite confirmation
        pyautogui.press('y')
        time.sleep(SAVE_DELAY)

    def new_document(self):
        """Create new document (discard current)."""
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(ACTION_DELAY)
        pyautogui.press('n')  # Don't save
        time.sleep(ACTION_DELAY)

    # -------------------------------------------------------------------------
    # Page Setup
    # -------------------------------------------------------------------------

    def click_page_setup(self):
        """Click the Page Setup tool in the sidebar."""
        print("  Opening Page Setup...")

        # Try image-based first
        if self.image_finder and self.image_finder.click("page_setup_icon"):
            return

        # Try calibrated coordinates, fall back to defaults
        self._click_element("page_setup", UI.sidebar_x, UI.page_setup_y)

    def set_orientation(self, orientation: Orientation):
        """Set page orientation to portrait or landscape."""
        print(f"  Setting orientation: {orientation.value}")

        self.click_page_setup()
        time.sleep(ACTION_DELAY)

        # Scroll down in the panel to find orientation section
        self._scroll(-3, UI.page_setup_panel_x, UI.orientation_section_y)
        time.sleep(SCROLL_DELAY)

        # Click portrait or landscape button
        if orientation == Orientation.PORTRAIT:
            offset = UI.portrait_btn_offset
        else:
            offset = UI.landscape_btn_offset

        self._click(
            UI.page_setup_panel_x + offset[0],
            UI.orientation_section_y + offset[1]
        )

    # -------------------------------------------------------------------------
    # Transform / Centering
    # -------------------------------------------------------------------------

    def click_transform(self):
        """Click the Transform tool in the sidebar."""
        print("  Opening Transform...")

        if self.image_finder and self.image_finder.click("transform_icon"):
            return

        self._click_element("transform", UI.sidebar_x, UI.transform_y)

    def select_all_and_group(self):
        """Select all objects and group them."""
        print("  Selecting all and grouping...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(ACTION_DELAY)
        pyautogui.hotkey('ctrl', 'g')
        time.sleep(ACTION_DELAY)

    def center_to_page(self):
        """Center the selected object(s) to the page."""
        print("  Centering to page...")

        self.select_all_and_group()
        self.click_transform()
        time.sleep(ACTION_DELAY)

        # Click "Center to Page" or "Align Center" button
        # This might be a dropdown or button depending on version
        self._click(UI.transform_panel_x, UI.center_to_page_y)

    # -------------------------------------------------------------------------
    # Registration Marks
    # -------------------------------------------------------------------------

    def click_print_cut(self):
        """Click the Print & Cut tool in the sidebar."""
        print("  Opening Print & Cut...")

        if self.image_finder and self.image_finder.click("print_cut_icon"):
            return

        self._click_element("print_cut", UI.sidebar_x, UI.print_cut_y)

    def set_registration_marks(self, settings: RegistrationSettings):
        """Configure registration mark settings."""
        print(f"  Setting registration marks: enabled={settings.enabled}")

        self.click_print_cut()
        time.sleep(ACTION_DELAY)

        # Enable/disable registration marks
        self._click(UI.page_setup_panel_x + 20, UI.regmark_enable_y)

        if settings.enabled:
            # Set length
            self._click(UI.page_setup_panel_x + 100, UI.regmark_length_y)
            type_in_field(str(settings.length_mm))

            # Set thickness
            self._click(UI.page_setup_panel_x + 100, UI.regmark_thickness_y)
            type_in_field(str(settings.thickness_mm))

            # Set inset
            self._click(UI.page_setup_panel_x + 100, UI.regmark_inset_y)
            type_in_field(str(settings.inset_mm))

    # -------------------------------------------------------------------------
    # Full Conversion Workflow
    # -------------------------------------------------------------------------

    def convert(
        self,
        input_dxf: str,
        output_studio3: str,
        orientation: Orientation = Orientation.LANDSCAPE,
        center: bool = True,
        registration: Optional[RegistrationSettings] = None
    ):
        """
        Full conversion workflow:
        1. Open DXF
        2. Set orientation
        3. Center paths
        4. Set registration marks
        5. Save as .studio3
        """
        print(f"\nConverting: {input_dxf}")

        self.open_file(input_dxf)

        if orientation:
            self.set_orientation(orientation)

        if center:
            self.center_to_page()

        if registration:
            self.set_registration_marks(registration)

        self.save_as(output_studio3)
        self.new_document()

        print("  Done!")


# =============================================================================
# Calibration Tool
# =============================================================================

# Default calibration file location
CALIBRATION_FILE = Path(__file__).parent / "silhouette_ui_coordinates.json"


def get_window_rect() -> dict:
    """Get the current Silhouette Studio window rectangle."""
    if not HAS_PYWINAUTO:
        return {"x": 0, "y": 0, "width": 1920, "height": 1080}

    try:
        app = Application(backend="uia").connect(path=SILHOUETTE_STUDIO_PATH)
        window = app.window(title_re=".*Silhouette Studio.*")
        rect = window.rectangle()
        return {
            "x": rect.left,
            "y": rect.top,
            "width": rect.width(),
            "height": rect.height()
        }
    except Exception as e:
        print(f"Warning: Could not get window rect: {e}")
        return {"x": 0, "y": 0, "width": 1920, "height": 1080}


def load_calibration(filepath: Path = CALIBRATION_FILE) -> Optional[dict]:
    """Load calibration data from JSON file."""
    if not filepath.exists():
        return None

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load calibration: {e}")
        return None


def save_calibration(data: dict, filepath: Path = CALIBRATION_FILE):
    """Save calibration data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nCalibration saved to: {filepath}")


def run_calibration(output_file: Path = CALIBRATION_FILE):
    """
    Interactive tool to find UI element coordinates.

    Run this with Silhouette Studio open, then move your mouse
    to each UI element and press Enter to record its position.

    Saves coordinates to a JSON file that can be committed to the repo.
    """
    print("=" * 60)
    print("UI Coordinate Calibration Tool")
    print("=" * 60)
    print()
    print("This tool records UI element positions and saves them to:")
    print(f"  {output_file}")
    print()
    print("Instructions:")
    print("1. Open Silhouette Studio and arrange it as desired")
    print("2. For each element, position your mouse over it")
    print("3. Press Enter to record the position")
    print("4. Press 's' to skip an element")
    print("5. Press Ctrl+C to abort")
    print()

    # Get window position first
    input("First, make sure Silhouette Studio is visible. Press Enter to continue...")
    window_rect = get_window_rect()
    print(f"Window detected at: ({window_rect['x']}, {window_rect['y']}) "
          f"size: {window_rect['width']}x{window_rect['height']}")

    # Elements to calibrate - these map to UICoordinates fields
    elements = [
        {
            "id": "sidebar_x",
            "name": "Any sidebar icon (to get X position)",
            "description": "The horizontal center of the left sidebar icons"
        },
        {
            "id": "page_setup",
            "name": "Page Setup icon in sidebar",
            "description": "The Page Setup tool icon"
        },
        {
            "id": "transform",
            "name": "Transform icon in sidebar",
            "description": "The Transform tool icon"
        },
        {
            "id": "print_cut",
            "name": "Print & Cut icon in sidebar",
            "description": "The Print & Cut (registration marks) tool icon"
        },
        {
            "id": "portrait_button",
            "name": "Portrait orientation button",
            "description": "Open Page Setup first, scroll to find orientation buttons"
        },
        {
            "id": "landscape_button",
            "name": "Landscape orientation button",
            "description": "Next to the Portrait button"
        },
        {
            "id": "center_horizontal",
            "name": "Center Horizontally button",
            "description": "Open Transform panel, find the align/center buttons"
        },
        {
            "id": "center_vertical",
            "name": "Center Vertically button",
            "description": "Usually near Center Horizontally"
        },
        {
            "id": "regmark_checkbox",
            "name": "Registration marks enable checkbox",
            "description": "Open Print & Cut panel, find the checkbox"
        },
        {
            "id": "regmark_type_dropdown",
            "name": "Registration mark type dropdown",
            "description": "Dropdown to select Type 1, Type 2, etc."
        },
        {
            "id": "regmark_length_field",
            "name": "Registration mark length input field",
            "description": "The text field for mark length"
        },
        {
            "id": "regmark_thickness_field",
            "name": "Registration mark thickness input field",
            "description": "The text field for mark thickness"
        },
    ]

    # Store results
    calibration = {
        "version": "1.0",
        "silhouette_studio_version": "unknown",  # User can fill this in
        "window": window_rect,
        "elements": {},
        "notes": "Coordinates are relative to window top-left corner"
    }

    print()
    version = input("What version of Silhouette Studio are you using? (e.g., 4.5.123): ")
    calibration["silhouette_studio_version"] = version or "unknown"
    print()

    try:
        for element in elements:
            print(f"\n--- {element['name']} ---")
            print(f"    {element['description']}")

            response = input("Position mouse and press Enter (or 's' to skip): ").strip().lower()

            if response == 's':
                print("  Skipped")
                continue

            pos = pyautogui.position()

            # Convert to window-relative coordinates
            rel_x = pos.x - window_rect['x']
            rel_y = pos.y - window_rect['y']

            calibration["elements"][element["id"]] = {
                "name": element["name"],
                "absolute": {"x": pos.x, "y": pos.y},
                "relative": {"x": rel_x, "y": rel_y}
            }

            print(f"  Recorded: absolute=({pos.x}, {pos.y}), relative=({rel_x}, {rel_y})")

    except KeyboardInterrupt:
        print("\n\nCalibration interrupted.")
        response = input("Save partial calibration? [y/N]: ")
        if response.lower() != 'y':
            print("Discarded.")
            return

    # Save calibration
    save_calibration(calibration, output_file)

    # Print summary
    print()
    print("=" * 60)
    print("Calibration Summary")
    print("=" * 60)
    print(f"Window size: {window_rect['width']}x{window_rect['height']}")
    print(f"Elements recorded: {len(calibration['elements'])}")
    print()
    print("To use this calibration, the script will automatically load it from:")
    print(f"  {output_file}")
    print()
    print("You can commit this file to your repo so others can use it.")
    print("Different screen sizes/DPI may require re-calibration.")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert DXF to Studio3 with full automation"
    )
    parser.add_argument("input", nargs="?", help="Input DXF file")
    parser.add_argument("output", nargs="?", help="Output .studio3 file")
    parser.add_argument(
        "--orientation",
        choices=["portrait", "landscape"],
        default="landscape",
        help="Page orientation"
    )
    parser.add_argument(
        "--no-center",
        action="store_true",
        help="Don't center paths to page"
    )
    parser.add_argument(
        "--registration",
        action="store_true",
        help="Enable registration marks"
    )
    parser.add_argument(
        "--reg-length",
        type=float,
        default=10.0,
        help="Registration mark length (mm)"
    )
    parser.add_argument(
        "--reg-thickness",
        type=float,
        default=0.5,
        help="Registration mark thickness (mm)"
    )
    parser.add_argument(
        "--reg-inset",
        type=float,
        default=5.0,
        help="Registration mark inset (mm)"
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Run calibration tool to find UI coordinates"
    )
    parser.add_argument(
        "--calibration-file",
        type=Path,
        default=CALIBRATION_FILE,
        help=f"Path to calibration JSON file (default: {CALIBRATION_FILE})"
    )
    parser.add_argument(
        "--studio-path",
        default=SILHOUETTE_STUDIO_PATH,
        help="Path to Silhouette Studio"
    )

    args = parser.parse_args()

    if args.calibrate:
        run_calibration(args.calibration_file)
        return

    if not args.input or not args.output:
        parser.error("input and output are required (unless using --calibrate)")

    # Prepare settings
    orientation = Orientation(args.orientation)
    registration = None
    if args.registration:
        registration = RegistrationSettings(
            enabled=True,
            length_mm=args.reg_length,
            thickness_mm=args.reg_thickness,
            inset_mm=args.reg_inset
        )

    # Run conversion
    print("=" * 60)
    print("DXF to Studio3 Advanced Converter")
    print("=" * 60)
    print()
    print("WARNING: Do not use mouse/keyboard during conversion!")
    print("Move mouse to top-left corner to abort.")
    print()

    response = input("Proceed? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    automation = SilhouetteAutomation(args.studio_path, args.calibration_file)

    try:
        automation.start()
        automation.convert(
            args.input,
            args.output,
            orientation=orientation,
            center=not args.no_center,
            registration=registration
        )
        print("\nConversion complete!")
    except KeyboardInterrupt:
        print("\nAborted by user.")
    except pyautogui.FailSafeException:
        print("\nAborted - mouse moved to corner.")
    finally:
        try:
            automation.close()
        except:
            pass


if __name__ == "__main__":
    main()
