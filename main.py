import streamlit as st
from components import well
from datetime import datetime

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

with st.sidebar:
    st.title("Hydration Logs")
with st.container(key="footer"):
    status_box = st.empty()

st.title("DeHydrate")

@st.dialog("Add a new oil well")
def add_well_dialog():
    uploaded_files = st.file_uploader(
        label="Add a new oil well",
        type=["csv"],
        accept_multiple_files=True,
        key="add_well_file_uploader",
        help="Upload a CSV file containing gas injector data to analyze",
    )
    if st.button(
        label="Add",
        icon=":material/add:",
        help=("Analyze the well data and add it to the list" if len(uploaded_files) != 0 else "No files have been uploaded"),
        type="primary",
        disabled=(len(uploaded_files) == 0),
        use_container_width=True,
        key="add_well_finish_button"
    ):
        st.rerun()

if st.button(
    label="Add a new oil well",
    icon=":material/add:",
    help="Upload a CSV file containing gas injector data to analyze",
    key="add_well_button",
):
    add_well_dialog()

well.well_listing(status_box)
