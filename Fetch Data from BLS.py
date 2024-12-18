import pandas as pd
import requests
import json
import os
from datetime import datetime

# Function to fetch data from BLS API/website
def fetch_bls_data(series_ids, start_year, end_year, api_key):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {"Content-Type": "application/json"}
    api_key = "72bd5ec7070048a99f4892a5b9221399"

    series_ids = [
        "CEU0000000001",  # Total Non-Farm Workers
        "LNS14000000",  # Unemployment Rates
        "LNS12000000",  # Civilian Employment (Seasonally Adjusted)
        "CES0500000003",  # Total Private Average Hourly Earnings of All Employees - Seasonally Adjusted
        "CES0500000008",  # Total Private Average Hourly Earnings of Prod. and Nonsup. Employees - Seasonally Adjusted
        "SMS31000000000000001",  # Nebraska, Total Nonfarm, Seasonally adjusted
    ]

    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": api_key,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        if "Results" in data:
            return data["Results"]["series"][0]["data"]
        else:
            print(f"No data found for series: {series_id}")
            return []
    else:
        print(f"Error fetching data. Please try again later.")
        return None

# Function to process BLS data
def process_bls_data(raw_data):
    data_frames = []
    for series in raw_data["Results"]["series"]:
        series_id = series["seriesID"]
        series_data = pd.DataFrame(series["data"])
        series_data["series_id"] = series_id
        series_data["value"] = pd.to_numeric(series_data["value"], errors='coerce')
        series_data["year"] = pd.to_numeric(series_data["year"], errors='coerce')
        data_frames.append(series_data)

    combined_data = pd.concat(data_frames)
    combined_data["date"] = pd.to_datetime(
        combined_data["year"].astype(str) + combined_data["periodName"]
    )
    return combined_data

# Function to save data to CSV (with appending capability)
def save_data_to_csv(data, file_name="bls_data.csv"):
    if os.path.exists(file_name):
        # Load existing data and append new data
        existing_data = pd.read_csv(file_name)
        data = pd.concat([existing_data, data]).drop_duplicates(subset=["series_id", "date"]).reset_index(drop=True)
    data.to_csv(file_name, index=False)
    st.success(f"Data saved to {file_name}")
    return file_name

# Main Streamlit app
def main():
    st.title("BLS Labor Statistics Dashboard")

    # Load API key
    api_key = st.text_input("Enter your BLS API Key", type="password")

    # Specify series IDs and data range
    series_ids = st.text_input("Enter BLS Series IDs (comma-separated)", "CES0000000001,LNS14000000").split(",")
    start_year = st.number_input("Start Year", min_value=2000, max_value=datetime.now().year, value=datetime.now().year - 1)
    end_year = st.number_input("End Year", min_value=2000, max_value=datetime.now().year, value=datetime.now().year)

    if st.button("Fetch and Save Data"):
        raw_data = fetch_bls_data(series_ids, start_year, end_year, api_key)

        if raw_data and "Results" in raw_data:
            processed_data = process_bls_data(raw_data)

            st.write("### Raw Data")
            st.write(processed_data)

            # Save data to CSV
            file_name = save_data_to_csv(processed_data)

            st.write(f"Data saved to `{file_name}`. Please commit this file to your GitHub repository.")

            # Create visualizations
            st.write("### Visualizations")
            for series_id in series_ids:
                series_data = processed_data[processed_data["series_id"] == series_id]

                if not series_data.empty:
                    st.line_chart(series_data.set_index("date")["value"])
                else:
                    st.warning(f"No data available for Series ID: {series_id}")

