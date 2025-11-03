#User Interface

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, date

CSV_FILE = "waste_log.csv"

class UserInterface:

    def __init__(self):
        self.st = st

    def display_title(self):
        self.st.markdown(
            "<h1 style='color:#4CAF50; text-align:center;'>EcoPulse</h1>",
            unsafe_allow_html=True
        )
    
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
     # Convert date from datetime.date to pd.Timestamp
    entry["Date"] = pd.Timestamp(entry["Date"])

    # Ensure the new entry has the same columns and proper order
    new_entry_df = pd.DataFrame([entry], columns=df.columns)

    # Concatenate safely 
    if df.empty:
        df = new_entry_df
    else:
        df = pd.concat([df, new_entry_df], ignore_index=True)

    # Save to CSV
    df.to_csv(CSV_FILE, index=False)

    # Success message
    ui.st.success("Waste entry logged successfully!")

#Reset Waste log Button
if ui.st.button("Reset Waste Log"):
    # Reset the DataFrame and CSV
    df = pd.DataFrame(columns=["Item Name", "Item Category", "Quantity Wasted (kg)",
                               "Reason", "Date", "Cost ($)", "Location"])
    df.to_csv(CSV_FILE, index=False)
    ui.st.success("Waste log has been reset.")

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

    if not grouped_df.empty:

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
        top_item_row = grouped_df.loc[grouped_df["Quantity Wasted (kg)"].idxmax()] #Get top wasted item row
        
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
    else:
        ui.st.info("No data available to display the bar chart.")


    #Prepping Data for Line Charts

    # Ensure 'Date' column is proper datetime
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Date'])
    filtered_df['Date'] = filtered_df['Date'].dt.normalize()



    filtered_df["Quantity Wasted (kg)"] = pd.to_numeric(filtered_df["Quantity Wasted (kg)"], errors='coerce').fillna(0)
    filtered_df['Cost ($)'] = (
    filtered_df['Cost ($)']
        .astype(str).str.replace(r'[^0-9.\-]', '', regex=True)
        .replace('', np.nan)
        .astype(float)
)
    for col in filtered_df.select_dtypes(include=['object']).columns:
        filtered_df[col] = filtered_df[col].astype(str).replace('nan', '')

    filtered_df = filtered_df.dropna(subset=['Date']) #Drop rows with invalid dates
    filtered_df = filtered_df.sort_values('Date') #Sort by date before plotting

    #Line chart for Waste Trend
    if not filtered_df.empty:
        waste_weekly = (
            filtered_df.set_index('Date').resample('W')["Quantity Wasted (kg)"].sum().reset_index() #Resample weekly
        )
        if not waste_weekly.empty and waste_weekly["Quantity Wasted (kg)"].sum() > 0:
            waste_weekly["MA4"] = waste_weekly["Quantity Wasted (kg)"].rolling(4, min_periods=1).mean() #4-week moving average

            waste_trend_fig = px.line(waste_weekly, x="Date", y=["Quantity Wasted (kg)", "MA4"], 
                                    title="Weekly Waste Trend",
                                    labels={"value": "Quantity Wasted (kg)", "variable": "Legend"}
            )
            waste_trend_fig.update_xaxes(rangeslider_visible = True, tickformat='%b %d', showgrid=True) #Add range slider
            waste_trend_fig.update_yaxes(title="Quantity Wasted (kg)", showgrid=True)
            waste_trend_fig.update_traces(mode='lines+markers')  #Show markers for clarity
            ui.st.plotly_chart(waste_trend_fig) #Display line chart for waste
        else:
            ui.st.info("Not enough data to ddisplay the weekly waste trend.")
    else:
        ui.st.info("No waste data available.")

    #Line chart for Cost Trend
    if not filtered_df.empty:
        cost_weekly = filtered_df.set_index('Date').resample('W')["Cost ($)"].sum().reset_index() #Resample weekly
        if not cost_weekly.empty and cost_weekly["Cost ($)"].sum() > 0:
            cost_weekly["MA4"] = cost_weekly["Cost ($)"].rolling(4, min_periods=1).mean() #4-week moving average
            cost_trend_fig = px.line(cost_weekly, x="Date", y=["Cost ($)", "MA4"], 
                                    title="Weekly Cost Trend",
                                    labels={"value": "Cost ($)", "variable": "Legend"}
            )
            cost_trend_fig.update_xaxes(rangeslider_visible = True, tickformat='%b %d', showgrid=True) #Add range slider
            cost_trend_fig.update_yaxes(title="USD per week", showgrid=True)
            cost_trend_fig.update_traces(mode='lines+markers')  #Show markers for clarity
            ui.st.plotly_chart(cost_trend_fig) #Display line chart for cost
        else:
            ui.st.info("Not enough data to display the weekly cost trend.")
    else:
        ui.st.info("No cost data available.")
    
     #Smart Recommendations
    with ui.st.expander("Smart Recommendations"):
        ui.st.subheader("Automated Weekly Insights")

        # Ensure Date is datetime before creating Week column
        if 'Date' in filtered_df.columns:
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
            filtered_df = filtered_df.dropna(subset=['Date'])
        
        # Create Week column from Date (only if Date exists and is datetime)
        if 'Date' in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df['Date']):
            filtered_df['Week'] = filtered_df['Date'].dt.to_period('W')
        else:
            ui.st.error("Date column is missing or not in datetime format. Cannot create Week column.")
            filtered_df['Week'] = None

        #Rule 1 High Waste Share (>30%)
        # Check if Week column is valid before using it
        if 'Week' not in filtered_df.columns or filtered_df['Week'].isna().all():
            ui.st.error("Week column is missing or invalid. Cannot analyze current week data.")
            this_week_df = pd.DataFrame()
        else:
            current_week = filtered_df['Week'].max()
            this_week_df = filtered_df[filtered_df['Week'] == current_week]
            
            # Only strip if dataframe is not empty
            if not this_week_df.empty:
                this_week_df['Item Category'] = this_week_df['Item Category'].str.strip()
                this_week_df['Item Name'] = this_week_df['Item Name'].str.strip()

        if not this_week_df.empty:
            category_sums = this_week_df.groupby('Item Category')["Quantity Wasted (kg)"].sum().reset_index()
            item_totals = this_week_df.groupby(['Item Name', 'Item Category'])["Quantity Wasted (kg)"].sum().reset_index()

            merged = pd.merge(item_totals, category_sums, on='Item Category', suffixes=('', '_CatTotal'))
            merged['ShareOfCategory'] = merged['Quantity Wasted (kg)'] / merged['Quantity Wasted (kg)_CatTotal'] * 100


            flagged_items = merged[merged['ShareOfCategory'] > 30]

            ui.st.markdown("**Items with High Waste Share (>30%) in their Category this Week:**")
            if not flagged_items.empty:
                ui.st.warning("Order 20% less the next cycle for these items:")
                ui.st.dataframe(flagged_items[['Item Name', 'Item Category', 'ShareOfCategory']].round(2))
            else:
                ui.st.success("No items exceeded 30% waste share in their category this week.")
        else:

            ui.st.info("No waste data available for the current week to generate insights.")

        #Rule 2 Top 3 waste for 2 consecutive weeks
        
        ui.st.markdown("Items in Top 3 Waste for 2 Consecutive Weeks")

        # Check if Week column exists and is valid
        if 'Week' not in filtered_df.columns or filtered_df['Week'].isna().all():
            ui.st.error("Week column is missing or invalid. Cannot analyze consecutive weeks.")
        else:
            filtered_df['Item Name'] = filtered_df['Item Name'].str.strip()
            filtered_df['Item Category'] = filtered_df['Item Category'].str.strip()
                
            # Drop rows where Week is None/NaN before grouping
            rule2_df = filtered_df.dropna(subset=['Week']).copy()
            
            if rule2_df.empty:
                ui.st.info("No valid week data available for consecutive week analysis.")
            else:
                #Calculate weekly totals   
                weekly_totals = rule2_df.groupby(['Week', 'Item Name'], as_index=False)["Quantity Wasted (kg)"].sum()
                weekly_totals = weekly_totals.sort_values(['Week', 'Quantity Wasted (kg)'], ascending=[True, False])

                top3_per_week = (
                    weekly_totals
                    .groupby('Week')       # group by the Week column
                    .head(3)               # take top 3 rows per week
                    .reset_index(drop=True)
                )

                consecutive_flags = []

                # Sort weeks by their start time to ensure proper order
                week_list = sorted(top3_per_week['Week'].unique(), key=lambda x: x.start_time)

                if len(week_list) < 2:
                    ui.st.info("Not enough weekly data to analyze consecutive weeks yet.")
                else:
                    #Check for consecutive weeks
                    for i in range(1, len(week_list)):
                        prev_week = week_list[i-1]
                        curr_week = week_list[i]
                        
                        # Check if weeks are consecutive by comparing with prev_week + 1
                        # Period objects support addition: prev_week + 1 should equal curr_week if consecutive
                        next_expected_week = prev_week + 1
                        
                        # Use start_time comparison as reliable method to check consecutiveness
                        # Consecutive weeks should be 7 days apart
                        time_diff = curr_week.start_time - prev_week.start_time
                        days_diff = time_diff.days
                        
                        # Check if weeks are consecutive (exactly 7 days apart, or using Period comparison)
                        is_consecutive = (days_diff == 7) or (curr_week == next_expected_week)
                        
                        if is_consecutive:
                            this_week_items = set(top3_per_week[top3_per_week['Week'] == week_list[i]]['Item Name'].astype(str).str.strip().tolist()) #Items this week
                            prev_week_items = set(top3_per_week[top3_per_week['Week'] == week_list[i-1]]['Item Name'].astype(str).str.strip().tolist()) #Items previous week

                            repeated_items = this_week_items.intersection(prev_week_items) #Find common items

                            #Flag repeated items
                            for item in repeated_items:
                                consecutive_flags.append({
                                    "Item Name": item,
                                    "Week 1": str(week_list[i-1]),
                                    "Week 2": str(week_list[i]),
                                    "Recommendation": "Check the vendor/date rotation."
                                })

                #Display flagged items
                if consecutive_flags:
                    flagged_df = pd.DataFrame(consecutive_flags)
                    ui.st.warning("These items were in the Top 3 for 2 consecutive weeks:")
                    ui.st.dataframe(flagged_df)
                else:
                    ui.st.success("No items were in the Top 3 for 2 consecutive weeks.")









    

        






