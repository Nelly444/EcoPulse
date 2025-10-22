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
        itemName = self.st.text_input("Enter the name of the waste item: ")
        itemCategory = self.st.selectbox("Select the category of the waste item: ",
                                        ["Plastic", "Paper", "Metal", "Glass", "Organic", "Other"])
        quantityWasted = self.st.number_input("Enter the quantity wasted (in kg): ", min_value=0.0, step=0.1)
        reasonWasted = self.st.text_area("Enter the reason for the waste: ")
        dateWasted = self.st.date_input("Enter the date of waste:")
        cost = self.st.number_input("Enter the cost associated with the waste (in $): ", min_value=0.0, step=0.01)
        location = self.st.text_input("Enter the location where the waste occurred: ")
        
        return {
            "itemName": itemName,
            "itemCategory": itemCategory,
            "quantityWasted": quantityWasted,
            "reason": reasonWasted,
            "date": dateWasted,
            "cost": cost,
            "location": location
        }
    
try:
    df = pd.read_csv(CSV_FILE) # Load existing data
except FileNotFoundError: # If file doesn't exist, create a new one
    df = pd.DataFrame(columns=["itemName", "itemCategory", "quantityWasted", "reason", "date", "cost", "location"]) # Define columns
    df.to_csv(CSV_FILE, index=False) # Create file if it doesn't exist


ui = UserInterface() #Create UI instance
ui.display_title() #Display title

entry = ui.get_input() #Get user input

if(ui.st.button("Submit Waste Entry")): #Submit Button
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True) #Add new entry to dataframe
    df.to_csv(CSV_FILE, index=False) #Save to CSV
    ui.st.success("Waste entry logged successfully!") #Success message

if(ui.st.button("View Waste Log")): #View Log Button
    ui.st.subheader("Waste Log")
    ui.st.dataframe(df) #Display dataframe

    

        






