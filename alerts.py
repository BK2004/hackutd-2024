import  streamlit  as  st
from streamlit_notifications import send_push

def YellowHydrate(wellName, time):
    send_push(title= "WARNING: Hydration Likely", body = wellName + " at time " + time)

def RedHydrate(wellName, time):
    send_push(title= "CRITICAL: Hydration Detected", body = wellName + " at time " + time)

