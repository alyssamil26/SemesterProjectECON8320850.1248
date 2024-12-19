import subprocess
import pandas as pd
import streamlit as st
import os

# Step 1: Run the Fetch Data from BLS script
def update_csv():
    try:
        # Repository and script details
        repo_url = "https://github.com/alyssamil26/SemesterProjectECON8320850.1248.git"
        repo_dir = "SemesterProjectECON8320850.1248"  # Local directory name for the repo
        script_name = "Fetch Data from BLS.py"

        # Clone the repository if it doesn't exist, or pull the latest changes
        if not os.path.exists(repo_dir):
            subprocess.run(["git", "clone", repo_url], check=True)
        else:
            subprocess.run(["git", "-C", repo_dir, "pull"], check=True)

        # Construct the path to the script
        script_path = os.path.join(repo_dir, script_name)

        # Run the script
        subprocess.run(["python", script_path], check=True)

        st.success("CSV file updated successfully from GitHub!")
    except subprocess.CalledProcessError as e:
        st.error(f"Error running Fetch Data from BLS script: {e}")


# Step 2: Load the CSV file from the repository
def load_data(csv_file):
    try:
        # Mapping of series IDs to their descriptive names
        series_mapping = {
            "CES0000000001": "Total Non-Farm Workers",
            "LNS14000000": "Unemployment Rates",
            "LNS12000000": "Civilian Employment (Seasonally Adjusted)",
            "CES0500000003": "Total Private Average Hourly Earnings of All Employees (Seasonally Adjusted)",
            "CES0500000008": "Total Private Average Hourly Earnings of Prod. and Nonsup. Employees (Seasonally Adjusted)",
            "SMS31000000000000001": "Nebraska, Total Nonfarm (Seasonally Adjusted)"
        }

        # Load the CSV
        data = pd.read_csv(csv_file)

        # Drop duplicates
        data = data.drop_duplicates()

        # Convert 'year' column to string to avoid comma formatting
        data['year'] = data['year'].astype(str)

        # Drop the 'period' column
        if 'period' in data.columns:
            data.drop(columns=['period'], inplace=True)

        # Drop the 'latest' column
        if 'latest' in data.columns:
            data.drop(columns=['period'], inplace=True)

        # Rename the 'periodName' column to 'Month'
        if 'periodName' in data.columns:
            data.rename(columns={'periodName': 'Month'}, inplace=True)

        # Replace series_id with descriptive names
        if 'series_id' in data.columns:
            data['series_id'] = data['series_id'].replace(series_mapping)

        return data
    except FileNotFoundError:
        st.error(f"CSV file {csv_file} not found. Please update the data first.")
        return None


# Step 3: Build the Streamlit Dashboard
def build_dashboard(data):
    st.title("Labor Statistics Dashboard")

    st.write("### Series Tables")

    # Create a separate table for each series without 'footnotes'
    for series_name in data['series_id'].unique():
        st.write(f"#### {series_name}")
        series_data = data[data['series_id'] == series_name].drop(columns=['footnotes'], errors='ignore')
        st.dataframe(series_data)

    st.write("### Visualizations")

    # Line charts for each series
    for series_name in data['series_id'].unique():
        series_data = data[data['series_id'] == series_name]
        st.write(f"#### {series_name}")
        st.line_chart(series_data.set_index('date')['value'])

# Main function to coordinate the Streamlit app
def main():
    st.sidebar.title("Options")
    csv_file = "data/bls_data.csv"  # Path to your CSV file

    # Load and display data
    data = load_data(csv_file)
    if data is not None:
        build_dashboard(data)

# Entry point for the script
if __name__ == "__main__":
    main()