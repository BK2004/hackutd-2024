import streamlit as st
import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas

from services.data import well_names, get_well_data, mark_anomalies, MIN_TIMESTAMP
import notifications

STEP_INTERVAL = 24 # hours

global last_timestamp
last_timestamp = MIN_TIMESTAMP

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
            if self.status.is_priority():
                notify_alert(self)
        self.alert_status = st.session_state[alert_key]
    
    def append(self, data: pandas.DataFrame):
        self.data = pandas.concat([self.data, data])

def fetch_well_data(timestamp) -> list[Well]:
    global last_timestamp

    if 'wells' not in st.session_state:
        st.session_state['wells'] = {}
    
    for well_name in well_names:
        data = get_well_data(well_name, last_timestamp, timestamp)
        mark_anomalies(data)
        if well_name not in st.session_state.wells:
            st.session_state.wells[well_name] = Well(well_name, data, getStatus(data))
        else:
            st.session_state.wells[well_name].append(data)
            if data[(data['anomaly'] == True)].size > 0:
                st.session_state[f"well_alert_{well_name.lower()}"] = Status.HYDRATE_DETECTED
                st.session_state.wells[well_name].alert_status = Status.HYDRATE_DETECTED
                st.session_state.wells[well_name].status = Status.HYDRATE_DETECTED if data.iloc[-1]["anomaly"] == True else Status.OK
    return st.session_state.wells

def getStatus(data):
    if len(data) == 0: return Status.OK

    if data.iloc[-1]['anomaly'] == True:
        return Status.HYDRATE_DETECTED
    return Status.OK

def display_wells(wells: list[Well], with_status: Status):
    for well_name in wells:
        slot = st.empty()
        well = wells[well_name]
        if (well.alert_status == with_status):
            with slot.container(key=f"well_{well.name.lower()}"):
                with st.expander(f"Oil Well &mdash; **{well.name}**", with_status.is_priority(), icon=well.status.get_icon()):
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
                            well.alert_status = well.status

                        st.button(
                            label="Mark as resolved",
                            icon=":material/close:",
                            help=("Mark this issue as resolved and update oil well status" if can_dismiss else "This issue is ongoing and cannot be dismissed"),
                            key=f"well_alert_dismiss_{well.name.lower()}",
                            disabled=(not can_dismiss),
                            on_click=dismiss,
                            args=[well]
                        )

@st.fragment(run_every=2)
def well_listing(status_box):
    global last_timestamp

    if last_timestamp is None:
        last_timestamp = MIN_TIMESTAMP
    status = status_box.status("Fetching latest information...")

    timechange = timedelta(days=(datetime.now() - st.session_state["timestamp_0"] + MIN_TIMESTAMP).second/2)
    wells = fetch_well_data(MIN_TIMESTAMP + timechange)

    st.subheader("Alerts")
    priority_slot = st.empty()
    if any(wells[well].alert_status.is_priority() for well in wells):
        with priority_slot.container(key="priority_list"):
            display_wells(wells, Status.HYDRATE_DETECTED)
            display_wells(wells, Status.HYDRATE_PREDICTED)
    else:
        priority_slot.info("No problems detected.", icon=":material/check_circle:")

    st.divider()

    st.subheader("Oil Wells")
    with st.container(key="regular_list"):
        display_wells(wells, Status.OK)
    last_timestamp = MIN_TIMESTAMP + timechange
    
    status.update(label=(MIN_TIMESTAMP + timechange).strftime("Updated %m/%d, %I:%M %p"), state="complete")

PUSH_TAG_KEY = "push_tag"

def notify_alert(well: Well):
    if PUSH_TAG_KEY not in st.session_state:
        st.session_state[PUSH_TAG_KEY] = 1
    notifications.send_push(
        title=("Hydrate formation detected" if well.status == Status.HYDRATE_DETECTED else "Hydrate formation likely"),
        body=f"Oil Well \u2014 {well.name}",
        icon_path=f"./images/{'error' if well.status == Status.HYDRATE_DETECTED else 'warning'}_icon.png",
        tag=st.session_state[PUSH_TAG_KEY],
    )
    st.session_state[PUSH_TAG_KEY] += 1

    with st.sidebar.container(border=True):
        st.write("**Hydrate Formation Detected**" if well.status == Status.HYDRATE_DETECTED else "**Hydrate formation likely**")
        st.write(f"Oil Well - **{well.name}**")
        st.write("Time: " + st.session_state['timestamp'].strftime("%m/%d, %I:%M %p"))
