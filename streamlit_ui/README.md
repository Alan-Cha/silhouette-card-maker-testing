# Streamlit UI Components

This directory contains the modular Streamlit UI components for the Silhouette Card Maker application.

## File Structure

- `__init__.py` - Package initialization file
- `plugins_ui.py` - "Run Plugin" tab implementation
- `generate_pdf_ui.py` - "Generate PDFs" tab implementation
- `offsets_ui.py` - "Offsets" tab implementation
- `settings_ui.py` - "Edit Settings/JSON Files" tab implementation
- `testing_ui.py` - "MiscTesting" tab implementation

## Architecture

Each tab is implemented as a separate module with a main render function:

```python
def render_[tab_name]_tab():
    """Render the [Tab Name] tab"""
    # Tab-specific implementation
```

### Usage

The main `start_streamlit.py` file imports and routes to these components:

```python
from streamlit_ui.plugins_ui import render_plugins_tab
from streamlit_ui.generate_pdf_ui import render_generate_pdf_tab
# ... other imports

if selected_tab == "Run Plugin":
    render_plugins_tab()
elif selected_tab == "Generate PDFs":
    render_generate_pdf_tab()
# ... other routing
```

## Adding New Tabs

To add a new tab:

1. Create a new `.py` file in this directory
2. Implement a `render_[tab_name]_tab()` function
3. Import the function in `start_streamlit.py`
4. Add the tab to the `option_menu` list
5. Add routing logic in the main file

## Dependencies

Each UI module imports only what it needs:

- `streamlit` for UI components
- `utilities` for shared functionality
- Specific modules for their functionality (e.g., `create_pdf`, `offset_pdf`)
