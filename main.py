import streamlit as st
from datetime import datetime, timedelta

from components import well

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

# Key in session state for storage of current slider values
DATE_RANGE_SLIDER_KEY = "date_range_slider"
# Key in session state for actual date range, used to keep slider setting between runs
DATE_RANGE_KEY = "date_range"

def on_date_range_slider_change():
    # Surely there's a better way but I don't care
    st.session_state[DATE_RANGE_KEY] = st.session_state[DATE_RANGE_SLIDER_KEY]

# Double-ended datetime slider
start_date = datetime.today() - timedelta(days=365)
end_date = datetime.today()
if DATE_RANGE_KEY not in st.session_state:
    st.session_state[DATE_RANGE_KEY] = (start_date, end_date)
st.slider(
    "Date range",
    key=DATE_RANGE_SLIDER_KEY,
    min_value=start_date,
    max_value=end_date,
    value=st.session_state[DATE_RANGE_KEY],
    step=timedelta(days=1),
    on_change=on_date_range_slider_change,
)

with st.container(key="footer"):
    status_box = st.empty()

well.well_listing(status_box)
