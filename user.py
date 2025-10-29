#User Interface

import streamlit as st
import plotly.express as px
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
            "Item Name": itemName,
            "Item Category": itemCategory,
            "Quantity Wasted (kg)": quantityWasted,
            "Reason": reasonWasted,
            "Date": dateWasted,
            "Cost ($)": cost,
            "Location": location
        }
    
try:
    df = pd.read_csv(CSV_FILE) # Load existing data
except FileNotFoundError: # If file doesn't exist, create a new one
    df = pd.DataFrame(columns=["Item Name", "Item Category", "Quantity Wasted (kg)", "Reason", "Date", "Cost ($)", "Location"]) # Define columns
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


    #Total Waste Calculation
    df["Quantity Wasted (kg)"] = pd.to_numeric(df["Quantity Wasted (kg)"], errors='coerce').fillna(0)
    total_waste = df["Quantity Wasted (kg)"].sum() #Calculate total waste
    ui.st.write(f"Total Waste: {total_waste} kg") #Display

    #Top 3 Wasted Items
    top3 = df.groupby("Item Name", as_index=False)["Quantity Wasted (kg)"].sum().nlargest(3, "Quantity Wasted (kg)") #Top 3 wasted items
    ui.st.subheader("Top 3 Wasted Items")
    ui.st.dataframe(top3) #Display top 3

    #Bar Chart
    category_df = df.groupby("Item Category", as_index=False)["Quantity Wasted (kg)"].sum() #Group by category
    color_map {
        "Plastic": "blue",
        "Paper": "green",
        "Metal": "gray",
        "Glass": "orange",
        "Organic": "brown",
        "Other": "gray"
    }

    bar_fig = px.bar(category_df, x="Item Category", y="Quantity Wasted (kg)", color="Item Category", color_discrete_map=color_map, text_auto=True, title="Total Waste by Category") #Bar chart
    ui.st.plotly_chart(bar_fig) #Display bar chart


    #Line Chart
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce') #Convert to datetime
    trend_df = df.groupby("Date", as_index=False)["Quantity Wasted (kg)"].sum() #Group by date
    trend_fig = px.line(trend_df, x="Date", y="Quantity Wasted (kg)", title="Waste Trend Over Time") #Line chart
    ui.st.plotly_chart(trend_fig) #Display line chart


    

        






