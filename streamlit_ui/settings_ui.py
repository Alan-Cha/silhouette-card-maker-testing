import streamlit as st
from utilities import LAYOUTS_JSON_PATH, OFFSET_JSON_PATH, manage_json_file


def render_settings_tab():
    """Render the Edit Settings/JSON Files tab"""
    st.markdown("## Card Size Definitions")

    card_size_editor = st.expander("Show/Edit", icon=":material/info:")
    card_size_data = unedited_card_data = st.session_state.card_sizes_from_layouts
    edited_card_sizes = card_size_editor.data_editor(card_size_data, num_rows="fixed")
    card_size_data = ""
    col1, col2 = card_size_editor.columns(2)
    col1.button(
        "Save",
        key="cscol1",
        on_click=manage_json_file,
        args=(LAYOUTS_JSON_PATH, "card_sizes", edited_card_sizes),
    )
    col2.button(
        "Undo Changes",
        key="cscol2",
        on_click=manage_json_file,
        args=(LAYOUTS_JSON_PATH, "card_sizes", unedited_card_data),
    )

    st.markdown("## Offset Data")

    offset_expander = st.expander("Show/Edit", icon=":material/info:")
    try:
        offsets_data = unedited_offsets_data = st.session_state.offsets_data
        edited_offsets_data = offset_expander.data_editor(
            offsets_data, num_rows="fixed"
        )
        offsets_data = ""
        col1, col2 = offset_expander.columns(2)
        col1.button(
            "Save",
            key="oscol1",
            on_click=manage_json_file,
            args=(OFFSET_JSON_PATH, None, edited_offsets_data),
        )
        col2.button(
            "Undo Changes",
            key="oscol2",
            on_click=manage_json_file,
            args=(OFFSET_JSON_PATH, None, unedited_offsets_data),
        )
    except:
        offset_expander.write("No Offset data loaded/found.")
    st.markdown("## Page Layout Definitions (Data editor doesn't like this data yet)")
