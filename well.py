import streamlit as st

import os
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

def load_wells_in_dir(dir_path: str) -> list[Well]:
    return [
        Well(dir_path + "/" + filename)
        for filename in os.listdir(dir_path)
        if filename.endswith(".csv")
    ]
