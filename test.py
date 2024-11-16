import os
import streamlit as st
import pandas as pd

@st.dialog
def well_dialog():
    pass

st.sidebar.title("Alerts")

st.title("Wells")

for filename in os.listdir("data"):
    if filename.endswith(".csv"):
        df = pd.read_csv("data/" + filename)
        df = df.ffill()
        st.subheader(filename.split("_")[0])
        st.line_chart(
            df,
            x="Time",
            y=("Inj Gas Meter Volume Instantaneous", "Inj Gas Meter Volume Setpoint", "Inj Gas Valve Percent Open"),
        )
