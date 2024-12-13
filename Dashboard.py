#%%



#%%
#pip install streamlit requests pandas matplotlib
#%%
#SetUpBLSAPI

import requests
import pandas as pd
import json

API_KEY = "your_bls_api_key"
BASE_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

def fetch_bls_data(series_id):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "seriesid": [series_id],
        "startyear": "2020",
        "endyear": "2024",
        "registrationkey": API_KEY
    }
    response = requests.post(BASE_URL, json=payload, headers=headers)
    data = response.json()
    return pd.DataFrame(data['Results']['series'][0]['data'])
#%%
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch data from the BLS API
def fetch_bls_data(series_id):
    API_KEY = "your_bls_api_key"  # Replace with your actual API key
    BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    headers = {'Content-Type': 'application/json'}
    payload = {
        "seriesid": [series_id],
        "startyear": "2020",  # Specify your desired start year
        "endyear": "2024",    # Specify your desired end year
        "registrationkey": API_KEY
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Convert the JSON response into a pandas DataFrame
        df = pd.DataFrame(data['Results']['series'][0]['data'])
        df['value'] = df['value'].astype(float)  # Ensure numeric values
        return df
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Streamlit app
st.title("US Labor Statistics Dashboard")

# Input for BLS Series ID
series_id = st.text_input("Enter BLS Series ID", "LNS14000000")  # Example: Unemployment rate

if st.button("Update Data"):
    data = fetch_bls_data(series_id)
    if not data.empty:
        # Process data for visualization
        data['date'] = pd.to_datetime(data['year'] + data['period'].str[1:], format='%Y%m')
        data = data.sort_values('date')

        # Display data
        st.subheader("Statistics Overview")
        st.write(data)

        # Plot data
        st.subheader("Trend Chart")
        plt.figure(figsize=(10, 5))
        plt.plot(data['date'], data['value'], marker='o')
        plt.title("Labor Statistics Trend")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.grid(True)
        st.pyplot(plt)
#%%
