import streamlit as st

import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from services.data import well_names, get_well_data, mark_anomalies
import pandas
from random import randrange

class Status(enum.IntEnum):
    OK = 0
    HYDRATE_PREDICTED = 1
    HYDRATE_DETECTED = 2

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
    alert_status: Status = field(init=False)

    def __post_init__(self):
        alert_key: str = f"well_alert_{self.name.lower()}"
        if alert_key not in st.session_state or self.status > st.session_state[alert_key]:
            st.session_state[alert_key] = self.status
        self.alert_status = st.session_state[alert_key]

def fetch_well_data() -> list[Well]:
    wells = []
    for well_name in well_names:
        data = get_well_data(well_name, datetime.now() - timedelta(weeks=8), datetime.now())
        mark_anomalies(data)
        well = Well(well_name, data, random_status()) # TODO: Use small range of time based on interval
        wells.append(well)
    return wells

def display_wells(wells: list[Well], with_status: Status):
    for well in wells:
        slot = st.empty()
        if (well.alert_status == with_status):
            with slot.container(key=f"well_{well.name.lower()}"):
                with st.expander(f"Oil Well &mdash; {well.name}", with_status.is_priority(), icon=well.status.get_icon()):
                    if well.alert_status == Status.OK:
                        st.info("No problems detected.", icon=":material/check_circle:")
                    elif well.alert_status == Status.HYDRATE_PREDICTED:
                        st.warning("Readings suggest a hydrate is likely to form. Inspect the gas injector riser as soon as possible.", icon=":material/warning:")
                    elif well.alert_status == Status.HYDRATE_DETECTED:
                        st.error("Detected formation of a hydrate. Immediate action is needed for the gas injector to function properly.", icon=":material/error:")

                    st.scatter_chart(
                        data=well.data,
                        x="Time",
                        y="Inst/Set/Valve",
                        color="anomaly",
                        size=50,
                    )

                    if with_status.is_priority():
                        can_dismiss = well.status < well.alert_status
                        def dismiss(well: Well):
                            # Reset alert status back to the current status
                            st.session_state[f"well_alert_{well.name.lower()}"] = well.status

                        st.button(
                            label="Dismiss alert",
                            icon=":material/close:",
                            help=("Mark this issue as resolved and update oil well status" if can_dismiss else "This issue is ongoing and cannot be dismissed"),
                            key=f"well_alert_dismiss_{well.name.lower()}",
                            disabled=(not can_dismiss),
                            on_click=dismiss,
                            args=[well]
                        )

@st.fragment(run_every=20)
def well_listing(status_box):
    status = status_box.status("Fetching latest information...")
    start_datetime = datetime.now()

    wells = fetch_well_data()

    st.title("Alerts")
    priority_slot = st.empty()
    if any(well.alert_status.is_priority() for well in wells):
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
