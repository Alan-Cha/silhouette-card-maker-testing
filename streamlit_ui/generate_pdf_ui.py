import re
import click
import streamlit as st
from utilities import CardSize, PaperSize, get_click_command_options, convert_click_options_to_dict, validate_gen_options
from create_pdf import cli


def render_generate_pdf_tab():
    """Render the Generate PDFs tab"""
    
    if "create_pdf_options" not in st.session_state:
        create_pdf_options = get_click_command_options(cli)
        st.session_state.create_pdf_options = create_pdf_options
    else:
        create_pdf_options = st.session_state.create_pdf_options

    gen_pdf_expander = st.expander("Generate PDFs", expanded=True)
    card_size = gen_pdf_expander.pills(
        label="Card Size", options=[c.name for c in CardSize], default="STANDARD"
    )
    paper_size = gen_pdf_expander.pills(
        label="Paper Size", options=[p.name for p in PaperSize], default="LETTER"
    )

    gen_pdf_form = gen_pdf_expander.form(key="gen_pdf_form", enter_to_submit=False)
    gen_pdf_form.link_button(
        "create_pdf.py Documentation Page",
        "https://alan-cha.github.io/silhouette-card-maker/docs/create/",
        icon=":material/live_help:",
    )

    gpcol1, gpcol2, gpcol3 = gen_pdf_form.columns([1, 1, 1])
    optional = gpcol3.expander("Additional Options", expanded=False)

    for opt in create_pdf_options:
        if isinstance(opt["type"], click.types.StringParamType):
            if opt["show_default"] is True:
                if re.search(r"directory|path", opt["help"]):
                    opt["value"] = gpcol1.text_input(
                        label=opt["help"],
                        value=opt["value"],
                        placeholder=opt["default"],
                        key=opt["name"],
                    )
                else:
                    opt["value"] = gpcol1.text_input(
                        label=opt["help"],
                        value=opt["value"],
                        placeholder=opt["default"],
                        key=opt["name"],
                    )
            else:
                opt["value"] = optional.text_input(
                    label=opt["help"],
                    value=opt["value"],
                    placeholder=opt["default"],
                    key=opt["name"],
                )

        elif isinstance(opt["type"], click.types.BoolParamType):
            if opt["is_flag"]:
                if opt["show_default"] is True:
                    opt["value"] = gpcol3.toggle(
                        label=opt["help"], value=opt["value"], key=opt["name"]
                    )
                else:
                    opt["value"] = optional.toggle(
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

            opt["value"] = gpcol2.number_input(**num_input_kwargs)

        elif isinstance(opt["type"], click.types.IntParamType):
            pass
        elif isinstance(opt["type"], click.types.FloatParamType):
            pass
        elif isinstance(opt["type"], click.types.Choice):
            if re.search(r"card_size", opt["name"]):
                opt["value"] = CardSize[card_size].value
            if re.search(r"paper_size", opt["name"]):
                opt["value"] = PaperSize[paper_size].value
        else:
            pass

    gen_pdf_only_save = gen_pdf_form.toggle(label="Just save my values (Don't Submit)")
    gen_pdf_form_submit = gen_pdf_form.form_submit_button(
        label="Create PDFs",
        on_click=_save_cached_data,
        args=("create_pdf_options", create_pdf_options),
    )

    if gen_pdf_form_submit:
        if not gen_pdf_only_save:
            create_pdf_options_dict = convert_click_options_to_dict(create_pdf_options)
            del create_pdf_options_dict["version"]

            create_pdf_options_dict = validate_gen_options(create_pdf_options_dict)

            st.success("PDF Generation Sent")
            cli.callback(**create_pdf_options_dict)
        # Maybe bug? I think one of these two are not working.
        st.session_state.create_pdf_options = create_pdf_options
        _save_cached_data("create_pdf_options", create_pdf_options)


def _save_cached_data(cachename, variable):
    """Save cached data to session state"""
    st.session_state.cachename = variable
