import streamlit as st

import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from services.data import well_names, get_well_data, mark_anomalies
import pandas
from random import randrange

class Status(enum.Enum):
    OK = enum.auto()
    HYDRATE_PREDICTED = enum.auto()
    HYDRATE_DETECTED = enum.auto()

    def is_priority(self):
        return self != Status.OK

    def get_icon(self):
        if self == Status.OK:
            return ":material/check_circle:" # (v)
        elif self == Status.HYDRATE_PREDICTED:
            return ":material/warning:" # /!\
        elif self == Status.HYDRATE_DETECTED:
            return ":material/error:" # (!)
        else:
            return ":material/help:" # (?)

def random_status():
    # teehee
    number = randrange(0, 20)
    return Status.HYDRATE_DETECTED if number == 0 else Status.HYDRATE_PREDICTED if number == 1 else Status.OK

@dataclass
class Well:
    name: str
    data: pandas.DataFrame
    status: Status

def fetch_well_data(dateRange) -> list[Well]:
    wells = []
    for well_name in well_names:
        data = get_well_data(well_name, dateRange[0], dateRange[1])
        mark_anomalies(data)
        well = Well(well_name, data, random_status()) # TODO: Use small range of time based on interval
        wells.append(well)
    return wells

def display_wells(wells: list[Well], with_status: Status):
    for well in wells:
        slot = st.empty()
        if (well.status == with_status):
            icon = well.status.get_icon()
            with slot.container(key=f"well_{well.name.lower()}"):
                with st.expander(f"Oil Well &mdash; {well.name}", with_status.is_priority(), icon=icon):
                    if well.status == Status.OK:
                        st.info("No problems detected.", icon=icon)
                    elif well.status == Status.HYDRATE_PREDICTED:
                        st.warning("Readings suggest a hydrate is likely to form. Inspect the gas injector riser as soon as possible.", icon=icon)
                    elif well.status == Status.HYDRATE_DETECTED:
                        st.error("Detected formation of a hydrate. Immediate action is needed for the gas injector to function properly.", icon=icon)
                    st.scatter_chart(data=well.data, x="Time", y="Inst/Set/Valve", color="anomaly")

@st.fragment(run_every=20)
def well_listing(status_box, dateRange):
    status = status_box.status("Fetching latest information...")
    start_datetime = datetime.now()

    wells = fetch_well_data(dateRange)

    st.title("Alerts")
    priority_slot = st.empty()
    if any(well.status.is_priority() for well in wells):
        with priority_slot.container(key="priority_list"):
            display_wells(wells, Status.HYDRATE_DETECTED)
            display_wells(wells, Status.HYDRATE_PREDICTED)
    else:
        priority_slot.info("No problems detected.", icon=":material/check_circle:")

    st.divider()

    st.title("Oil Wells")
    with st.container(key="regular_list"):
        display_wells(wells, Status.OK)
    
    status.update(label=start_datetime.strftime("Updated %m/%d, %I:%M %p"), state="complete")
