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


#Submit Button
if(ui.st.button("Submit Waste Entry")):
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True) #Add new entry to dataframe
    df.to_csv(CSV_FILE, index=False) #Save to CSV
    ui.st.success("Waste entry logged successfully!") #Success message



#View Log Button
if(ui.st.checkbox("View Waste Log")): 

    ui.st.sidebar.header("Filters") #Sidebar header
    categories = df["Item Category"].dropna().unique()
    locations = df["Location"].dropna().unique()

    #Side bar filters
    selected_categories = ui.st.sidebar.multiselect("Filter by Category", categories, default=categories) #Category filter
    selected_locations = ui.st.sidebar.multiselect("Filter by Location", locations, default=locations) #Location filter

    filtered_df = df[
        (df["Item Category"].isin(selected_categories)) &
        (df["Location"].isin(selected_locations))
    ] #Apply filters

    #Display filtered dataframe
    ui.st.subheader("Waste Log")
    ui.st.dataframe(filtered_df) #Display dataframe


    #Total Waste Calculation
    filtered_df["Quantity Wasted (kg)"] = pd.to_numeric(filtered_df["Quantity Wasted (kg)"], errors='coerce').fillna(0)
    total_waste = filtered_df["Quantity Wasted (kg)"].sum() #Calculate total waste
    ui.st.write(f"Total Waste: {total_waste} kg") #Display

    #Top 3 Wasted Items
    top3 = filtered_df.groupby("Item Name", as_index=False)["Quantity Wasted (kg)"].sum().nlargest(3, "Quantity Wasted (kg)") #Top 3 wasted items
    ui.st.subheader("Top 3 Wasted Items")
    ui.st.dataframe(top3) #Display top 3

    #Bar Chart for Waste by Category
    grouped_df = filtered_df.groupby(["Item Category", "Reason"], as_index=False).agg({
        "Quantity Wasted (kg)": "sum",
        "Cost ($)": "sum"
    })#Group by category

    top_item_row = grouped_df.loc[grouped_df["Quantity Wasted (kg)"].idxmax()]
    

    bar_fig = px.bar(
    grouped_df,
    x="Item Category",
    y="Quantity Wasted (kg)",
    color="Reason",#Stacked by Reason
    hover_data={
        "Quantity Wasted (kg)": True,
        "Cost ($)": True,
    },
    text_auto=True,
    title="Total Waste by Category"
)
    
    bar_fig.add_annotation(
    x=top_item_row["Item Category"],
    y=top_item_row["Quantity Wasted (kg)"] * 1.3,
    text=f"Top Wasted Item: {top_item_row['Reason']} ({top_item_row['Quantity Wasted (kg)']} kg)",
    showarrow=False,
    font=dict(color="white", size=12, family="Arial"),
    align="center",
    bordercolor="white",
    borderwidth=1,
    borderpad=4,
    bgcolor="rgba(0, 0, 0, 0.6)",
    opacity=0.8
)
    
    bar_fig.update_traces(
    hovertemplate=
    "<b>Category:</b> %{x}<br>" +
    "<b>Reason:</b> %{customdata[0]}<br>" +
    "<b>Quantity:</b> %{y} kg<br>" +
    "<b>Cost:</b> $%{customdata[1]:.2f}",
    customdata=grouped_df[["Reason", "Cost ($)"]].values,
    selector=dict(type='bar')
)


    ui.st.plotly_chart(bar_fig) #Display bar chart


    #Line Chart for Waste Trend
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce').dt.normalize() #Convert to datetime
    filtered_df["Quantity Wasted (kg)"] = pd.to_numeric(filtered_df["Quantity Wasted (kg)"], errors='coerce').fillna(0)
    filtered_df = filtered_df.dropna(subset=['Date']) #Drop rows with invalid dates

    waste_weekly = filtered_df.set_index('Date').resample('W')["Quantity Wasted (kg)"].sum().reset_index() #Resample weekly

    waste_weekly["MA4"] = waste_weekly["Quantity Wasted (kg)"].rolling(4, min_periods=1).mean() #4-week moving average

    waste_trend_fig = px.line(waste_weekly, x="Date", y=["Quantity Wasted (kg)", "MA4"], 
                             title="Weekly Waste Trend"
    )
    waste_trend_fig.update_xaxes(rangeslider_visible = True) #Add range slider
    ui.st.plotly_chart(waste_trend_fig) #Display line chart for waste

    #Line chart for Cost Trend
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce').dt.normalize()
    cost_weekly = filtered_df.set_index('Date').resample('W')["Cost ($)"].sum().reset_index() #Resample weekly
    cost_weekly["MA4"] = cost_weekly["Cost ($)"].rolling(4, min_periods=1).mean() #4-week moving average

    cost_trend_fig = px.line(cost_weekly, x="Date", y=["Cost ($)", "MA4"], 
                             title="Weekly Cost Trend"
    )
    cost_trend_fig.update_xaxes(rangeslider_visible = True) #Add range slider
    ui.st.plotly_chart(cost_trend_fig) #Display line chart for cost
    





    

        






