import streamlit as st
import os

# from streamlit_extras.floating_button import floating_button # https://arnaudmiribel.github.io/streamlit-extras/extras/floating_button/
from streamlit_extras.pdf_viewer import (
    pdf_viewer,
)  # https://arnaudmiribel.github.io/streamlit-extras/extras/pdf_viewer/


def render_testing_tab():
    pdf_view_dir = st.text_input(
        label="Directory to list PDFs",
        value="./game/output",
        placeholder="./game/output",
    )
    test_expansion = st.expander(label="View PDFs", expanded=False)
    # dir = "C:/repos/silhouette-card-maker/examples/ZERO SUMZ"

    try:
        files = os.listdir(pdf_view_dir)
        filtered = [f for f in files if f.endswith(".pdf")]
        for f in filtered:
            with test_expansion.expander(label=f, expanded=False):
                # file_exp = testform.expander(f)
                pdf_viewer((os.path.join(pdf_view_dir, f)))
    except:
        filtered = []
        test_expansion.write("Invalid Directory")
