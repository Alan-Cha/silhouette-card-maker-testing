import os
import subprocess
import importlib.util
import click
import streamlit as st
from utilities import get_plugin_display_name, get_click_command_options


def render_plugins_tab():
    """Render the Run Plugin tab"""
    st.markdown("## Run Plugin")

    plugins_dir = "plugins"
    available_plugin_dirs = [
        d
        for d in os.listdir(plugins_dir)
        if os.path.isdir(os.path.join(plugins_dir, d))
    ]

    # Get proper display names
    plugin_options = {
        get_plugin_display_name(plugin_dir): plugin_dir
        for plugin_dir in available_plugin_dirs
    }

    plugin_expander = st.expander("Card Fetching", expanded=True)

    with plugin_expander:
        selected_plugin_display = st.selectbox(
            "Select Card Game Plugin",
            list(plugin_options.keys()),
            help="Choose the card game plugin to use for fetching card images",
        )

        # Get the actual directory name from the selected display name
        selected_plugin = plugin_options[selected_plugin_display]

        # Deck list management
        decklist_dir = os.path.join("game", "decklist")
        os.makedirs(decklist_dir, exist_ok=True)

        # Get existing deck files
        existing_files = [
            f
            for f in os.listdir(decklist_dir)
            if f.endswith((".txt", ".ydk", ".ydke"))
            and os.path.isfile(os.path.join(decklist_dir, f))
        ]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Select Existing Deck")
            selected_file = st.selectbox(
                "Choose existing deck file",
                [""] + existing_files,
                help="Select a previously uploaded deck file",
                key="deck_file_selector",
            )

        with col2:
            st.subheader("Upload New Deck")

            if not st.session_state.get("just_uploaded", False):
                uploaded_file = st.file_uploader(
                    "Upload deck file",
                    type=["txt", "ydk", "ydke"],
                    help="Upload a new deck file (.txt, .ydk, or .ydke)",
                    key="file_uploader",
                )

                if uploaded_file is not None:
                    st.info(f"Ready to upload: {uploaded_file.name}")

                    if st.button("Upload File", type="secondary", key="upload_button"):
                        file_path = os.path.join(decklist_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"File {uploaded_file.name} uploaded successfully!")

                        # Clear the file uploader and set upload flag
                        if "file_uploader" in st.session_state:
                            del st.session_state["file_uploader"]

                        st.session_state["just_uploaded"] = True
                        st.session_state["last_uploaded_file"] = uploaded_file.name
                        st.rerun()
            else:
                st.success(
                    f"Last uploaded: {st.session_state.get('last_uploaded_file', 'Unknown file')}"
                )
                if st.button(
                    "Upload Another File", type="secondary", key="upload_another"
                ):
                    st.session_state["just_uploaded"] = False
                    st.rerun()

        deck_file_path = None
        if selected_file and selected_file != "":
            deck_file_path = os.path.join(decklist_dir, selected_file)

        if deck_file_path:
            st.info(f"Selected deck file: {os.path.basename(deck_file_path)}")

            fetch_file = os.path.join(plugins_dir, selected_plugin, "fetch.py")
            if os.path.exists(fetch_file):

                # Load deck formats
                selected_format = _load_deck_formats(plugins_dir, selected_plugin)

                # Load plugin options
                plugin_options = _load_plugin_options(
                    plugins_dir, selected_plugin, fetch_file
                )

                # Generate Cards button
                if st.button("Generate Cards", type="primary"):
                    if selected_format:
                        _execute_plugin(
                            fetch_file,
                            deck_file_path,
                            selected_format,
                            plugin_options,
                            selected_plugin,
                        )
                    else:
                        st.warning("Please select a deck format")
            else:
                st.error(f"Plugin {selected_plugin} does not have a fetch.py file")
        else:
            st.info("Please select or upload a deck file to continue")


def _load_deck_formats(plugins_dir, selected_plugin):
    """Load deck formats for the selected plugin"""
    try:
        import sys

        plugin_path = os.path.join(plugins_dir, selected_plugin)

        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        try:
            spec = importlib.util.spec_from_file_location(
                "deck_formats",
                os.path.join(plugins_dir, selected_plugin, "deck_formats.py"),
            )
            deck_formats_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(deck_formats_module)

            if hasattr(deck_formats_module, "DeckFormat"):
                format_options = [fmt.value for fmt in deck_formats_module.DeckFormat]
                return st.selectbox(
                    "Deck Format",
                    format_options,
                    help="Select the format of your deck file",
                )
            else:
                return st.text_input(
                    "Deck Format",
                    help="Enter the deck format (plugin doesn't define standard formats)",
                )
        finally:
            if plugin_path in sys.path:
                sys.path.remove(plugin_path)

    except Exception as e:
        st.warning(f"Could not load deck formats for {selected_plugin}: {e}")
        return st.text_input("Deck Format", help="Enter the deck format manually")


def _load_plugin_options(plugins_dir, selected_plugin, fetch_file):
    """Load and render plugin options"""
    plugin_options = []
    try:
        import sys

        plugin_path = os.path.join(plugins_dir, selected_plugin)

        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        try:
            spec = importlib.util.spec_from_file_location("fetch", fetch_file)
            fetch_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fetch_module)

            if hasattr(fetch_module, "cli"):
                plugin_options = get_click_command_options(fetch_module.cli)

                # Filter out the required arguments (deck_path and format)
                plugin_options = [
                    opt
                    for opt in plugin_options
                    if opt["name"] not in ["deck_path", "format"]
                ]
        finally:
            if plugin_path in sys.path:
                sys.path.remove(plugin_path)

        if plugin_options:
            st.subheader("Plugin Options")
            opt_col1, opt_col2 = st.columns(2)

            for i, opt in enumerate(plugin_options):
                current_col = opt_col1 if i % 2 == 0 else opt_col2

                with current_col:
                    _render_option_input(opt)

    except Exception as e:
        st.info(f"Could not load plugin options for {selected_plugin}: {e}")

    return plugin_options


def _render_option_input(opt):
    """Render input widget for a single option"""
    if isinstance(opt["type"], click.types.StringParamType):
        if opt.get("multiple", False):
            opt["value"] = st.text_input(
                label=opt["help"] or opt["name"],
                value="",
                placeholder="Enter multiple values separated by commas",
                key=f"plugin_opt_{opt['name']}",
                help=(
                    f"Multiple values allowed. {opt['help']}"
                    if opt["help"]
                    else "Multiple values allowed"
                ),
            )
        else:
            opt["value"] = st.text_input(
                label=opt["help"] or opt["name"],
                value=opt.get("default", ""),
                key=f"plugin_opt_{opt['name']}",
            )

    elif isinstance(opt["type"], click.types.BoolParamType):
        if opt.get("is_flag", False):
            opt["value"] = st.checkbox(
                label=opt["help"] or opt["name"],
                value=opt.get("default", False),
                key=f"plugin_opt_{opt['name']}",
            )

    elif isinstance(opt["type"], click.types.IntRange):
        num_input_kwargs = {
            "label": opt["help"] or opt["name"],
            "value": opt.get("default", 0),
            "key": f"plugin_opt_{opt['name']}",
        }

        if hasattr(opt["type"], "max") and opt["type"].max is not None:
            num_input_kwargs["max_value"] = opt["type"].max
        if hasattr(opt["type"], "min") and opt["type"].min is not None:
            num_input_kwargs["min_value"] = opt["type"].min

        opt["value"] = st.number_input(**num_input_kwargs)

    elif isinstance(opt["type"], click.types.IntParamType):
        opt["value"] = st.number_input(
            label=opt["help"] or opt["name"],
            value=opt.get("default", 0),
            step=1,
            key=f"plugin_opt_{opt['name']}",
        )

    elif isinstance(opt["type"], click.types.FloatParamType):
        opt["value"] = st.number_input(
            label=opt["help"] or opt["name"],
            value=float(opt.get("default", 0.0)),
            key=f"plugin_opt_{opt['name']}",
        )

    elif isinstance(opt["type"], click.types.Choice):
        opt["value"] = st.selectbox(
            label=opt["help"] or opt["name"],
            options=opt["type"].choices,
            index=(
                0
                if opt.get("default") is None
                else opt["type"].choices.index(opt["default"])
            ),
            key=f"plugin_opt_{opt['name']}",
        )

    else:
        # Fallback for unknown types
        opt["value"] = st.text_input(
            label=opt["help"] or opt["name"],
            value=str(opt.get("default", "")),
            key=f"plugin_opt_{opt['name']}",
        )


def _execute_plugin(
    fetch_file, deck_file_path, selected_format, plugin_options, selected_plugin
):
    """Execute the plugin with the provided options"""
    try:
        # Prepare command to run the plugin's fetch.py
        cmd = ["py", fetch_file, deck_file_path, selected_format]

        for opt in plugin_options:
            if "value" in opt and opt["value"]:
                option_name = f"--{opt['name']}"  # Keep underscores as-is

                if isinstance(opt["type"], click.types.BoolParamType) and opt.get(
                    "is_flag", False
                ):
                    if opt["value"]:
                        cmd.append(option_name)
                elif opt.get("multiple", False) and isinstance(opt["value"], str):
                    for value in opt["value"].split(","):
                        value = value.strip()
                        if value:
                            cmd.extend([option_name, value])
                else:
                    cmd.extend([option_name, str(opt["value"])])

        with st.spinner(f"Fetching cards using {selected_plugin} plugin..."):
            st.code(" ".join(cmd))

            # Run the fetch command
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=os.getcwd()
            )

            if result.returncode == 0:
                st.success("Cards fetched successfully!")
                if result.stdout:
                    st.text_area("Output:", result.stdout, height=200)
            else:
                st.error("Error fetching cards:")
                if result.stderr:
                    st.text_area("Error:", result.stderr, height=200)
                if result.stdout:
                    st.text_area("Output:", result.stdout, height=200)

    except Exception as e:
        st.error(f"Failed to run plugin: {e}")
