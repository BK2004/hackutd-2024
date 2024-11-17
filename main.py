import streamlit as st
import pandas as pd
from components import well
from datetime import datetime
import services

DEFAULT_SESSION_STATES = {
    "timestamp_0": datetime.now(),
}

# Custom CSS for the fixed footer
st.html("""
    <style>
        div.st-key-footer {
            position: fixed;
            bottom: 0;
            background-color: white;
            z-index: 999;
            box-shadow: 0 0 1rem 1rem white;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
""")

for k in DEFAULT_SESSION_STATES:
    st.session_state[k] = DEFAULT_SESSION_STATES[k]

with st.container(key="footer"):
    status_box = st.empty()

st.title("DeHydrate")

@st.dialog("Add a new oil well")
def add_well_dialog():
    well_name = st.text_input("Oil well name")
    uploaded_file = st.file_uploader(
        label="Add a new oil well",
        type=["csv"],
        accept_multiple_files=False,
        key="add_well_file_uploader",
        help="Upload a CSV file containing gas injector data to analyze",
    )
    if st.button(
        label="Add",
        icon=":material/add:",
        help=("Analyze the well data and add it to the list" if uploaded_file is not None and not well_name.isspace() else "More information needed"),
        type="primary",
        disabled=(uploaded_file is None or well_name.isspace()),
        use_container_width=True,
        key="add_well_finish_button"
    ):
        uploaded_data = pd.read_csv(uploaded_file)
        services.data = pd.concat([services.data, services.convert_data(well_name, uploaded_data)])
        services.well_names.append(well_name)

        st.rerun()

if st.button(
    label="Add a new oil well",
    icon=":material/add:",
    help="Upload a CSV file containing gas injector data to analyze",
    key="add_well_button",
):
    add_well_dialog()

well.well_listing(status_box)
