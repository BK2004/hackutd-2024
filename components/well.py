import streamlit as st

import enum
import os
from datetime import datetime, timedelta
from services.data import well_names, getWellData, mark_anomalies
import pandas

class Status(enum.Enum):
    OK = enum.auto()
    HYDRATION_PREDICTED = enum.auto()
    HYDRATION_DETECTED = enum.auto()

    def is_priority(self):
        return self != Status.OK

    def get_icon(self):
        if self == Status.OK:
            return ":material/check_circle:" # (v)
        elif self == Status.HYDRATION_PREDICTED:
            return ":material/warning:" # /!\
        elif self == Status.HYDRATION_DETECTED:
            return ":material/error:" # (!)
        else:
            return ":material/help:" # (?)

def random_status():
    from random import choice
    # teehee
    return choice([Status.OK, Status.OK, Status.OK, Status.OK, Status.OK, Status.OK, Status.OK, Status.OK, Status.HYDRATION_PREDICTED, Status.HYDRATION_DETECTED])

class Well:
    def __init__(self, data: pandas.DataFrame, status: Status, name: str):
        self.name: str = name
        self.data: pandas.DataFrame = data
        self.status: Status = status

def fetch_well_data() -> list[Well]:
    wells = []
    for well_name in well_names:
        data = getWellData(well_name, datetime.now() - timedelta(weeks=8), datetime.now())
        mark_anomalies(data)
        well = Well(data, random_status(), well_name) # TODO: Use small range of time based on interval
        wells.append(well)
    return wells

def display_well(well: Well, priority_only: bool):
    slot = st.empty()
    if (well.status.is_priority() == priority_only):
        icon = well.status.get_icon()
        with slot.container(key=f"well:{well.name}"):
            with st.expander(well.name, priority_only, icon=icon):
                if well.status == Status.OK:
                    st.info("No problems detected", icon=icon)
                elif well.status == Status.HYDRATION_PREDICTED:
                    st.warning("Hydration predicted to occur soon", icon=icon)
                elif well.status == Status.HYDRATION_DETECTED:
                    st.error("Hydration presence detected", icon=icon)
                st.scatter_chart(data=well.data, x="Time", y="Inst/Set/Valve", color="anomaly")

@st.fragment(run_every=15)
def well_listing():
    status = st.status("Fetching latest information...")
    start_datetime = datetime.now()

    wells = fetch_well_data()

    priority_slot = st.empty()
    with priority_slot.container(key="priority-list"):
        st.title("Alerts")
        for well in wells:
            display_well(well, True)
        st.divider()
    
    with st.container(key="regular-list"):
        st.title("Wells")
        for well in wells:
            display_well(well, False)

    status.update(label=start_datetime.strftime("Updated %m/%d, %I:%M %p"), state="complete")
