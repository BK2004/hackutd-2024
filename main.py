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

with st.container(key="footer"):
    status_box = st.empty()

well.well_listing(status_box)
