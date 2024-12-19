import subprocess
import pandas as pd
import streamlit as st

# Step 1: Run the Fetch Data from BLS script
def update_csv():
    try:
        # Execute the "Fetch Data from BLS.py" script
        subprocess.run(["python", "Fetch Data from BLS.py"], check=True)
        st.success("CSV file updated successfully!")
    except subprocess.CalledProcessError as e:
        st.error(f"Error running Fetch Data from BLS script: {e}")

# Step 2: Load the CSV file from the repository
def load_data(csv_file):
    try:
        data = pd.read_csv(csv_file)
        return data
    except FileNotFoundError:
        st.error(f"CSV file {csv_file} not found. Please update the data first.")
        return None

# Step 3: Build the Streamlit Dashboard
def build_dashboard(data):
    st.title("Labor Statistics Dashboard")
    st.write("### Data Overview")
    st.dataframe(data)

    st.write("### Visualizations")

    # Line Chart of Values
    for series_id in data['series_id'].unique():
        series_data = data[data['series_id'] == series_id]
        st.write(f"#### Series ID: {series_id}")
        st.line_chart(series_data.set_index('date')['value'])

# Main Streamlit App
def main():
    st.sidebar.title("Options")
    if st.sidebar.button("Update CSV"):
        update_csv()

    # File location of the CSV
    csv_file = "data/bls_data.csv"  # Adjust path if needed

    # Load and display data
    data = load_data(csv_file)
    if data is not None:
        build_dashboard(data)

if __name__ == "__main__":
    main()