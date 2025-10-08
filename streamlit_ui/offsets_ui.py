import re
import click
import streamlit as st
from utilities import get_click_command_options, convert_click_options_to_dict
from offset_pdf import offset_pdf


def render_offsets_tab():
    """Render the Offsets tab"""
    if "offset_pdf_options" not in st.session_state:
        offset_pdf_options = get_click_command_options(offset_pdf)
        st.session_state.offset_pdf_options = offset_pdf_options
    else:
        offset_pdf_options = st.session_state.offset_pdf_options

    offset_pdf_expander = st.expander("Adjust Offsets", expanded=False)
    offset_pdf_form = offset_pdf_expander.form(
        key="offset_pdf_form", enter_to_submit=False
    )

    try:
        if st.session_state.offsets_data:
            temp_offset = st.session_state.offsets_data
            for o in offset_pdf_options:
                if o["name"] == "x_offset":
                    o["value"] = temp_offset.x_offset
                elif o["name"] == "y_offset":
                    o["value"] = temp_offset.y_offset

        offset_pdf_form.link_button(
            "offset_pdf.py Documentation Page",
            "https://alan-cha.github.io/silhouette-card-maker/docs/offset/",
            icon=":material/live_help:",
        )

        opcol1, opcol2 = offset_pdf_form.columns([1, 1])

        for opt in offset_pdf_options:

            if isinstance(opt["type"], click.types.StringParamType):
                opt["value"] = opcol1.text_input(
                    label=opt["help"],
                    value=opt["value"],
                    placeholder=opt["default"],
                    key=opt["name"],
                )

            elif isinstance(opt["type"], click.types.BoolParamType):
                if opt["is_flag"]:
                    opt["value"] = opcol2.toggle(
                        label=opt["help"], value=opt["value"], key=opt["name"]
                    )

            elif isinstance(opt["type"], click.types.IntRange):
                num_input_kwargs = {
                    "label": opt["help"],
                    "value": opt["value"],
                    "key": opt["name"],
                }

                if getattr(opt["type"], "max", None) is not None:
                    num_input_kwargs["max_value"] = opt["type"].max

                if getattr(opt["type"], "min", None) is not None:
                    num_input_kwargs["min_value"] = opt["type"].min

                opt["value"] = opcol2.number_input(**num_input_kwargs)

            elif isinstance(opt["type"], click.types.IntParamType):
                num_input_kwargs = {
                    "label": opt["help"],
                    "value": opt["value"],
                    "key": opt["name"],
                    "step": 1,
                }
                if getattr(opt["type"], "max", None) is not None:
                    num_input_kwargs["max_value"] = opt["type"].max

                if getattr(opt["type"], "min", None) is not None:
                    num_input_kwargs["min_value"] = opt["type"].min

                opt["value"] = opcol1.number_input(**num_input_kwargs)
            elif isinstance(opt["type"], click.types.FloatParamType):
                pass
            elif isinstance(opt["type"], click.types.Choice):
                if re.search(r"card_size|paper_size", opt["name"]):
                    pass
                else:
                    print(f"Choice, {opt['name']}")

            else:
                pass
        gen_offset_only_save = offset_pdf_form.toggle(
            label="Just save my values (Don't Submit)"
        )
    except:
        offset_pdf_form.write("No Offset data loaded/found.")
        pass

    running_log_placeholder = st.empty()

    if offset_pdf_form.form_submit_button("Submit/Save"):
        if not gen_offset_only_save:
            offset_pdf_options_dict = convert_click_options_to_dict(offset_pdf_options)
            offset_pdf.callback(**offset_pdf_options_dict)
            offset_pdf_expander.info("PDF Generation Sent")
        # Maybe bug? I think one of these two are not working.
        st.session_state.offset_pdf_options = offset_pdf_options
        _save_cached_data("offset_pdf_options", offset_pdf_options)


def _save_cached_data(cachename, variable):
    """Save cached data to session state"""
    st.session_state.cachename = variable
