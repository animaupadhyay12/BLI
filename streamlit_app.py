import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import os

DATE_TRACKER_FILE = "last_fetch_date.json"
DATA_FILE = "bls_data.xlsx"

# Map each BLS series ID to a human-readable name
SERIES_NAME_MAP = {
    "LNS14000000": "Unemployment Rate (16 yrs and over)",
    "CES0000000001": "Total Nonfarm Employment",
    "LNS11000000": "Civilian Labor Force Level",
    "LNS12000000": "Civilian Employment Level",
    "LNS13000000": "Civilian Unemployment Level",
    "CES0500000002": "Total Private Average Weekly Hours",
    "CES0500000007": "Total Private Average Hourly Earnings"
}

st.title("BLS Monthly Data Dashboard")
st.write("This dashboard displays the latest BLS data trends with descriptive labels for easier understanding.")

# Display Last Update Date
if os.path.exists(DATE_TRACKER_FILE):
    with open(DATE_TRACKER_FILE, "r") as file:
        last_fetch_date = json.load(file)["last_fetch"]
        st.subheader(f"Last Data Update: {last_fetch_date}")
else:
    st.warning("No last fetch date found. Please run 'fetch_bls_data.py' first.")

if os.path.exists(DATA_FILE):
    data = pd.read_excel(DATA_FILE)
    if not data.empty:
        st.subheader("Data Table")
        st.write(data)

        # Visualization
        st.subheader("Data Visualization")
        series_ids = data['Series ID'].unique()
        for series_id in series_ids:
            # Get descriptive name from the map
            series_name = SERIES_NAME_MAP.get(series_id, series_id)

            st.write(f"### {series_name}")
            series_data = data[data['Series ID'] == series_id].copy()
            series_data['Date'] = pd.to_datetime(series_data[['Year', 'Month']].assign(day=1))
            series_data = series_data.sort_values('Date')

            fig, ax = plt.subplots()
            ax.plot(series_data['Date'], series_data['Value'], marker='o', linestyle='-')
            ax.set_title(f"Trend: {series_name}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Value")
            ax.grid(True)
            st.pyplot(fig)
    else:
        st.warning("Data file is empty. Please run 'fetch_bls_data.py' to populate the data.")
else:
    st.error("No data file found. Please run 'fetch_bls_data.py' to fetch and create the data file.")
