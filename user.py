#User Interface

import streamlit as st

import pandas as pd
from datetime import datetime

CSV_FILE = "waste_log.csv"


class UserInterface:

    def __init__(self):
        self.st = st

    def display_title(self):
        self.st.title("Waste Management Tracker")
    
    def get_input(self):
        pass
        






