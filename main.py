import streamlit as st
import pandas as pd
import datetime as dt
import os
from datetime import datetime, timedelta

from components import well

header = st.container()
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

### Custom CSS for the sticky header
st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: sticky;
        top: 2.875rem;
        background-color: rgb(14,17,23);
        z-index: 999;
    }
    .fixed-header {
        border: 2px solid white;
    }
</style>
    """,
    unsafe_allow_html=True
)
    
with header:
    # Double-ended datetime slider
    start_date = datetime(year=2024,month=11,day=16) - timedelta(days=365)
    end_date = datetime(year=2024,month=11,day=16)
    selected_date_range = st.slider(
    "Select a date range",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    step=timedelta(days=1),
    )

well.well_listing()
