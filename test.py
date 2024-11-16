import os
import streamlit as st
import pandas

class Well:
    def __init__(self, path: str):
        self.path = path
        self.name = path.split("/")[-1].split("_")[0]
        self.data = None
        self.load_data()
    
    def load_data(self):
        self.data = pandas.read_csv(self.path)
        self.data = self.data.ffill()
    
    def render_preview(self, parent):
        parent.subheader(self.name)
        parent.line_chart(self.data, x="Time")

def load_wells_in_dir(dir_path: str) -> list[Well]:
    return [
        Well(dir_path + "/" + filename)
        for filename in os.listdir(dir_path)
        if filename.endswith(".csv")
    ]

def main():
    wells = load_wells_in_dir("data")

    @st.dialog("the title")
    def well_dialog(well_name):
        pass

    st.sidebar.title("Alerts")

    st.title("Wells")

    for well in wells:
        well.render_preview(st)

if __name__ == "__main__":
    main()
