import streamlit as st

from well import *

wells = load_wells_in_dir("data")

@st.fragment
def preview_card(well):
    @st.dialog(f"{well.name} Details")
    def well_dialog():
        st.line_chart(well.data, x="Time")

    st.subheader(well.name)
    st.button(
        "Details...",
        key=f"{well.name}:details-button",
        help="View detailed information about this well",
        on_click=well_dialog,
    )

st.title("Wells")

for well in wells:
    with st.container(
        key=f"{well.name}:preview",
        border=True,
    ):
        preview_card(well)
