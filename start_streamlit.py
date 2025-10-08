from streamlit_option_menu import (
    option_menu,
)  # https://github.com/victoryhb/streamlit-option-menu

import streamlit as st
from utilities import reload_jsons

# Import tab modules
from streamlit_ui.plugins_ui import render_plugins_tab
from streamlit_ui.generate_pdf_ui import render_generate_pdf_tab
from streamlit_ui.offsets_ui import render_offsets_tab
from streamlit_ui.settings_ui import render_settings_tab
from streamlit_ui.testing_ui import render_testing_tab

st.set_page_config(
    page_title="Silhouette Card Maker",
    page_icon="🃏",
    initial_sidebar_state="collapsed",
    layout="wide",
    menu_items={  # Items in the built-in 3 dot menu top right. Not adjustable.
        "Get Help": "https://alan-cha.github.io/silhouette-card-maker/docs",
        "About": "https://github.com/Alan-Cha/silhouette-card-maker",
    },
)


def on_tab_change(key):
    pass


st.markdown("# Silhouette Card Maker")
if (
    ("df" not in st.session_state)
    or ("card_sizes_from_layouts" not in st.session_state)
    or ("paper_layouts_from_layouts" not in st.session_state)
    or ("offsets_data" not in st.session_state)
):
    reload_jsons()

selected_tab = option_menu(
    None,
    [
        "Run Plugin",
        "Generate PDFs",
        "Offsets",
        "Edit Settings/JSON Files",
        "MiscTesting",
    ],
    icons=["download", "suit-club-fill", "rulers", "gear", "bug"],
    on_change=on_tab_change,
    default_index=0,
    key="selected_tab",
    orientation="horizontal",
)

# Route to appropriate tab based on selection
if selected_tab == "Run Plugin":
    render_plugins_tab()
elif selected_tab == "Generate PDFs":
    render_generate_pdf_tab()
elif selected_tab == "Offsets":
    render_offsets_tab()
elif selected_tab == "Edit Settings/JSON Files":
    render_settings_tab()
elif selected_tab == "MiscTesting":
    render_testing_tab()
