#!/usr/bin/env python3
"""
DXF to Studio3 Converter with Full Automation

This script automates Silhouette Studio with mouse interactions for:
- Page orientation (portrait/landscape)
- Centering cutting paths
- Registration mark settings

Requirements:
    pip install pyautogui pywinauto pillow click

Usage:
    python dxf_to_studio3_advanced.py convert input.dxf output.studio3 --orientation landscape
    python dxf_to_studio3_advanced.py calibrate

Window Size Strategy:
    The script forces Silhouette Studio to a fixed window size (1920x1080)
    to ensure consistent UI element positions. If your screen is smaller,
    adjust WINDOW_WIDTH and WINDOW_HEIGHT.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from enum import Enum

import click

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui pillow")
    sys.exit(1)

try:
    from pywinauto import Application
except ImportError:
    print("ERROR: pywinauto not installed. Run: pip install pywinauto")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_STUDIO_PATH = r"C:\Program Files\Silhouette America\Silhouette Studio\Silhouette Studio.exe"

# Fixed window size for consistent coordinates
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_X = 0
WINDOW_Y = 0

# Timing (seconds). These defaults work for most machines.
# Use --action_delay on the CLI to increase if Silhouette Studio is slow.
STARTUP_WAIT = 10  # Wait for Silhouette Studio to start
ACTION_DELAY = 1.0  # Delay between UI actions
FILE_LOAD_DELAY = 5.0  # Wait for DXF file to fully load
PANEL_SWITCH_DELAY = 1.5  # Wait after clicking a sidebar panel icon
SAVE_DELAY = 3.0  # Wait for save dialog / file write

# Default calibration file location
CALIBRATION_FILE = Path(__file__).parent / "silhouette_ui_coordinates.json"


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
# Utility Functions
# =============================================================================

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


def connect_and_resize_studio(studio_path: str = DEFAULT_STUDIO_PATH):
    """
    Connect to a running Silhouette Studio and resize it.

    Uses pywinauto's win32 backend which supports move_window().
    Returns (window_wrapper, window_rect_dict).
    """
    app = Application(backend="win32").connect(path=studio_path, timeout=30)
    window = app.window(title_re=".*Silhouette Studio.*")
    window.restore()
    time.sleep(0.5)
    window.move_window(
        x=WINDOW_X, y=WINDOW_Y,
        width=WINDOW_WIDTH, height=WINDOW_HEIGHT
    )
    time.sleep(0.5)

    rect = window.rectangle()
    window_rect = {
        "x": rect.left,
        "y": rect.top,
        "width": rect.width(),
        "height": rect.height()
    }
    print(f"Window set to {window_rect['width']}x{window_rect['height']} "
          f"at ({window_rect['x']}, {window_rect['y']})")
    return window, window_rect


def start_and_resize_studio(studio_path: str = DEFAULT_STUDIO_PATH):
    """
    Start Silhouette Studio and resize it to a fixed window size.

    Returns (window_wrapper, window_rect_dict).
    """
    print("Starting Silhouette Studio...")

    if not os.path.exists(studio_path):
        raise FileNotFoundError(f"Not found: {studio_path}")

    subprocess.Popen([studio_path])
    print(f"Waiting {STARTUP_WAIT}s for startup...")
    time.sleep(STARTUP_WAIT)

    return connect_and_resize_studio(studio_path)


# =============================================================================
# Silhouette Studio Automation
# =============================================================================

class SilhouetteAutomation:
    """
    Automates Silhouette Studio operations.

    Uses pyautogui for mouse/keyboard input (clicking, typing, shortcuts).
    Uses pywinauto (win32 backend) for window management (positioning, resizing).

    All click coordinates are window-relative, loaded from a calibration JSON file.
    The actual window position is queried before each click so that coordinates
    remain correct even if the window has been moved.
    """

    def __init__(self, studio_path: str = DEFAULT_STUDIO_PATH, calibration_file: Path = None,
                 action_delay: float = ACTION_DELAY):
        self.studio_path = studio_path
        self.window = None  # pywinauto window wrapper
        self.action_delay = action_delay

        # Load calibration if available
        cal_file = calibration_file or CALIBRATION_FILE
        self.calibration = load_calibration(cal_file)
        if self.calibration:
            print(f"Loaded calibration for Silhouette Studio {self.calibration.get('silhouette_studio_version', 'unknown')}")
        else:
            print("No calibration file found.")
            print(f"Run 'calibrate' command to create: {cal_file}")

    def _get_window_origin(self):
        """Get the current top-left corner of the Silhouette Studio window."""
        if self.window:
            rect = self.window.rectangle()
            return rect.left, rect.top
        return 0, 0

    def start(self):
        """Start Silhouette Studio with fixed window size."""
        print("Starting Silhouette Studio...")

        if not os.path.exists(self.studio_path):
            raise FileNotFoundError(f"Not found: {self.studio_path}")

        subprocess.Popen([self.studio_path])
        print(f"Waiting {STARTUP_WAIT}s for startup...")
        time.sleep(STARTUP_WAIT)

        self.window, _ = connect_and_resize_studio(self.studio_path)

    def close(self):
        """Close Silhouette Studio."""
        print("Closing Silhouette Studio...")
        pyautogui.hotkey('alt', 'F4')
        time.sleep(0.5)
        pyautogui.press('n')  # Don't save
        time.sleep(1)

    def _click(self, x: int, y: int):
        """Click at window-relative coordinates.

        Queries the current window position so clicks remain correct
        even if the window has been moved.
        """
        win_x, win_y = self._get_window_origin()
        abs_x = win_x + x
        abs_y = win_y + y
        pyautogui.click(abs_x, abs_y)
        time.sleep(self.action_delay)

    def _click_element(self, element_id: str):
        """
        Click a calibrated element by ID.

        Reads window-relative coordinates from the calibration JSON.
        """
        if self.calibration and element_id in self.calibration.get("elements", {}):
            elem = self.calibration["elements"][element_id]
            x = elem["relative"]["x"]
            y = elem["relative"]["y"]
            self._click(x, y)
            return True
        else:
            print(f"Warning: Element '{element_id}' not calibrated. Run 'calibrate' first.")
            return False

    # -------------------------------------------------------------------------
    # File Operations
    # -------------------------------------------------------------------------

    def open_file(self, filepath: str):
        """Open a DXF file."""
        filepath = os.path.abspath(filepath)
        print(f"Opening: {filepath}")

        pyautogui.hotkey('ctrl', 'o')
        time.sleep(self.action_delay * 2)

        # Type path into the file dialog
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        set_clipboard(filepath)
        paste()
        time.sleep(self.action_delay)

        pyautogui.press('enter')
        # Wait for Silhouette Studio to fully load the DXF
        print(f"  Waiting {FILE_LOAD_DELAY}s for file to load...")
        time.sleep(FILE_LOAD_DELAY)

    def save_as(self, output_path: str):
        """Save as .studio3 file."""
        output_path = os.path.abspath(output_path)
        if not output_path.lower().endswith('.studio3'):
            output_path = os.path.splitext(output_path)[0] + '.studio3'

        print(f"Saving: {output_path}")

        pyautogui.hotkey('ctrl', 'shift', 's')
        time.sleep(self.action_delay * 2)

        # Type path into the save dialog
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        set_clipboard(output_path)
        paste()
        time.sleep(self.action_delay)

        pyautogui.press('enter')
        time.sleep(SAVE_DELAY)

        # Handle overwrite confirmation
        pyautogui.press('y')
        time.sleep(SAVE_DELAY)

    def new_document(self):
        """Create new document (discard current)."""
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(self.action_delay)
        pyautogui.press('n')  # Don't save
        time.sleep(self.action_delay)

    # -------------------------------------------------------------------------
    # Page Setup
    # -------------------------------------------------------------------------

    def set_orientation(self, orientation: Orientation):
        """Set page orientation to portrait or landscape."""
        print(f"  Setting orientation: {orientation.value}")

        self._click_element("page_setup")
        time.sleep(PANEL_SWITCH_DELAY)

        if orientation == Orientation.PORTRAIT:
            self._click_element("portrait_button")
        else:
            self._click_element("landscape_button")

    # -------------------------------------------------------------------------
    # Transform / Centering
    # -------------------------------------------------------------------------

    def select_all_and_group(self):
        """Select all objects and group them."""
        print("  Selecting all and grouping...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(self.action_delay)
        pyautogui.hotkey('ctrl', 'g')
        time.sleep(self.action_delay)

    def center_to_page(self):
        """Center the selected object(s) to the page."""
        print("  Centering to page...")

        self.select_all_and_group()
        self._click_element("transform")
        time.sleep(PANEL_SWITCH_DELAY)
        self._click_element("center_to_page")

    # -------------------------------------------------------------------------
    # Registration Marks
    # -------------------------------------------------------------------------

    def set_registration_marks(self, settings: RegistrationSettings):
        """Configure registration mark settings."""
        print(f"  Setting registration marks: enabled={settings.enabled}")

        self._click_element("print_cut")
        time.sleep(PANEL_SWITCH_DELAY)

        # Enable registration marks
        self._click_element("regmark_checkbox")
        time.sleep(self.action_delay)

        if settings.enabled:
            # Set length
            self._click_element("regmark_length_field")
            type_in_field(str(settings.length_mm))

            # Set thickness
            self._click_element("regmark_thickness_field")
            type_in_field(str(settings.thickness_mm))

            # Set inset
            self._click_element("regmark_inset_field")
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
# Calibration
# =============================================================================

# Elements to calibrate, grouped by which panel they belong to.
# The user is guided through each panel in sequence so they only
# need to open each sidebar tool once.
CALIBRATION_ELEMENTS = [
    # --- Page Setup ---
    {
        "id": "page_setup",
        "name": "Page Setup icon in sidebar",
        "description": "Click the Page Setup tool icon in the left sidebar"
    },
    {
        "id": "portrait_button",
        "name": "Portrait orientation button",
        "description": "The Page Setup panel should now be open. "
                       "Scroll down if needed to find the orientation buttons."
    },
    {
        "id": "landscape_button",
        "name": "Landscape orientation button",
        "description": "Next to the Portrait button"
    },
    # --- Transform ---
    {
        "id": "transform",
        "name": "Transform icon in sidebar",
        "description": "Click the Transform tool icon in the left sidebar"
    },
    {
        "id": "center_to_page",
        "name": "Center to Page button",
        "description": "The Transform panel should now be open. "
                       "Find the Center to Page button."
    },
    # --- Print & Cut ---
    {
        "id": "print_cut",
        "name": "Print & Cut icon in sidebar",
        "description": "Click the Print & Cut (registration marks) tool icon in the left sidebar"
    },
    {
        "id": "regmark_checkbox",
        "name": "Registration marks enable checkbox",
        "description": "The Print & Cut panel should now be open. "
                       "Find the checkbox to enable registration marks."
    },
    {
        "id": "regmark_length_field",
        "name": "Registration mark length input field",
        "description": "The numerical input field for mark length"
    },
    {
        "id": "regmark_thickness_field",
        "name": "Registration mark thickness input field",
        "description": "The numerical input field for mark thickness"
    },
    {
        "id": "regmark_inset_field",
        "name": "Registration mark inset input field",
        "description": "The numerical input field for mark inset"
    },
]


# =============================================================================
# CLI
# =============================================================================

@click.group()
def cli():
    """Convert DXF files to Silhouette Studio .studio3 format with full automation."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--orientation", type=click.Choice(["portrait", "landscape"]), default="landscape", show_default=True, help="Page orientation.")
@click.option("--no_center", is_flag=True, help="Don't center paths to page.")
@click.option("--registration", is_flag=True, help="Enable registration marks.")
@click.option("--reg_length", type=float, default=10.0, show_default=True, help="Registration mark length (mm).")
@click.option("--reg_thickness", type=float, default=0.5, show_default=True, help="Registration mark thickness (mm).")
@click.option("--reg_inset", type=float, default=5.0, show_default=True, help="Registration mark inset (mm).")
@click.option("--action_delay", type=float, default=ACTION_DELAY, show_default=True, help="Delay between UI actions (seconds). Increase if Silhouette Studio is slow.")
@click.option("--calibration_file", type=click.Path(), default=str(CALIBRATION_FILE), show_default=True, help="Path to calibration JSON file.")
@click.option("--studio_path", default=DEFAULT_STUDIO_PATH, show_default=True, help="Path to Silhouette Studio executable.")
def convert(input_file, output_file, orientation, no_center, registration,
            reg_length, reg_thickness, reg_inset, action_delay, calibration_file, studio_path):
    """Convert a DXF file to .studio3 with page setup and registration marks."""
    orient = Orientation(orientation)
    reg_settings = None
    if registration:
        reg_settings = RegistrationSettings(
            enabled=True,
            length_mm=reg_length,
            thickness_mm=reg_thickness,
            inset_mm=reg_inset
        )

    click.echo("=" * 60)
    click.echo("DXF to Studio3 Converter")
    click.echo("=" * 60)
    click.echo()
    click.echo("WARNING: Do not use mouse/keyboard during conversion!")
    click.echo("Move mouse to top-left corner to abort.")
    click.echo()

    if not click.confirm("Proceed?"):
        click.echo("Aborted.")
        return

    automation = SilhouetteAutomation(studio_path, Path(calibration_file), action_delay)

    try:
        automation.start()
        automation.convert(
            input_file,
            output_file,
            orientation=orient,
            center=not no_center,
            registration=reg_settings
        )
        click.echo("\nConversion complete!")
    except KeyboardInterrupt:
        click.echo("\nAborted by user.")
    except pyautogui.FailSafeException:
        click.echo("\nAborted - mouse moved to corner.")
    finally:
        try:
            automation.close()
        except:
            pass


@cli.command()
@click.option("--calibration_file", type=click.Path(), default=str(CALIBRATION_FILE), show_default=True, help="Output path for calibration JSON.")
@click.option("--studio_path", default=DEFAULT_STUDIO_PATH, show_default=True, help="Path to Silhouette Studio executable.")
def calibrate(calibration_file, studio_path):
    """
    Interactively calibrate UI element coordinates.

    Starts Silhouette Studio at a fixed window size, then prompts you
    to hover over each UI element and press Enter to record its position.

    Saves window-relative coordinates to a JSON file that can be
    committed to the repo.
    """
    output_file = Path(calibration_file)

    click.echo("=" * 60)
    click.echo("UI Coordinate Calibration Tool")
    click.echo("=" * 60)
    click.echo()
    click.echo("This tool will:")
    click.echo(f"  1. Start Silhouette Studio at {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    click.echo("  2. Prompt you to hover over each UI element")
    click.echo("  3. Save relative coordinates to:")
    click.echo(f"     {output_file}")
    click.echo()
    click.echo("Press 's' to skip an element, Ctrl+C to abort.")
    click.echo()

    if not click.confirm("Start Silhouette Studio and begin calibration?"):
        click.echo("Aborted.")
        return

    # Start Silhouette Studio at fixed size
    _, window_rect = start_and_resize_studio(studio_path)

    click.echo()
    version = click.prompt("What version of Silhouette Studio are you using?", default="unknown")
    click.echo()

    calibration = {
        "version": "1.0",
        "silhouette_studio_version": version,
        "window": window_rect,
        "elements": {},
        "notes": "All coordinates are relative to the window top-left corner"
    }

    try:
        for element in CALIBRATION_ELEMENTS:
            click.echo(f"\n--- {element['name']} ---")
            click.echo(f"    {element['description']}")

            response = input("Position mouse and press Enter (or 's' to skip): ").strip().lower()

            if response == 's':
                click.echo("  Skipped")
                continue

            pos = pyautogui.position()

            # Store as window-relative coordinates
            rel_x = pos.x - window_rect['x']
            rel_y = pos.y - window_rect['y']

            calibration["elements"][element["id"]] = {
                "name": element["name"],
                "relative": {"x": rel_x, "y": rel_y}
            }

            click.echo(f"  Recorded: relative=({rel_x}, {rel_y})")

    except KeyboardInterrupt:
        click.echo("\n\nCalibration interrupted.")
        if not click.confirm("Save partial calibration?", default=False):
            click.echo("Discarded.")
            return

    # Save calibration
    save_calibration(calibration, output_file)

    # Print summary
    click.echo()
    click.echo("=" * 60)
    click.echo("Calibration Summary")
    click.echo("=" * 60)
    click.echo(f"Window size: {window_rect['width']}x{window_rect['height']}")
    click.echo(f"Elements recorded: {len(calibration['elements'])}")
    click.echo()
    for elem_id, elem_data in calibration['elements'].items():
        click.echo(f"  {elem_id}: ({elem_data['relative']['x']}, {elem_data['relative']['y']})")
    click.echo()
    click.echo("You can commit this file to your repo so others can use it.")
    click.echo("Different screen sizes/DPI may require re-calibration.")


if __name__ == "__main__":
    cli()
