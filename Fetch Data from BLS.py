import pandas as pd
import requests
import json
import os
from datetime import datetime
from github import Github

# Function to fetch data from BLS API/website
def fetch_bls_data(series_ids, start_year, end_year, api_key):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {"Content-Type": "application/json"}

    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": api_key,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)  # Debugging line to see the full response
        if "Results" in data and "series" in data["Results"]:
            return data["Results"]
        else:
            raise ValueError(f"No valid data returned from the BLS API. Response: {data}")
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

#Process BLS Data
def process_bls_data(raw_data):
    data_frames = []
    for series in raw_data["series"]:  # Access series directly from the results
        series_id = series["seriesID"]
        series_data = pd.DataFrame(series["data"])
        series_data["series_id"] = series_id
        series_data["value"] = pd.to_numeric(series_data["value"], errors="coerce")
        series_data["year"] = pd.to_numeric(series_data["year"], errors="coerce")
        # Create a valid date string in the format YYYY-MM-DD
        series_data["date"] = series_data["year"].astype(str) + "-" + pd.to_datetime(
            series_data["periodName"], format="%B", errors="coerce"
        ).dt.month.astype(str).str.zfill(2) + "-01"
        data_frames.append(series_data)

    combined_data = pd.concat(data_frames)
    combined_data["date"] = pd.to_datetime(combined_data["date"])
    return combined_data


# Function to save data to GitHub
def save_data_to_github(data, repo_name, file_path, commit_message, github_token):
    from io import StringIO

    # Convert DataFrame to CSV string
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()

    # Authenticate with GitHub
    g = Github(github_token)
    repo = g.get_user().get_repo(repo_name)

    try:
        # Check if file exists
        file = repo.get_contents(file_path)
        # Update the file
        repo.update_file(
            file_path, commit_message, csv_content, file.sha
        )
        print(f"Updated file: {file_path} in repo: {repo_name}")
    except Exception:
        # Create a new file
        repo.create_file(file_path, commit_message, csv_content)
        print(f"Created new file: {file_path} in repo: {repo_name}")

if __name__ == "__main__":
    # Keys, Tokens, and Repo Paths
    api_key = "ba188c33045d4c419c06b6de6849fb86"
    github_token = "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"
    repo_name = "SemesterProjectECON8320850.1248"
    file_path = "data/bls_data.csv"
    commit_message = "Update BLS data"

    series_ids = [
        "CES0000000001",  # Total Non-Farm Workers
        "LNS14000000",  # Unemployment Rates
        "LNS12000000",  # Civilian Employment (Seasonally Adjusted)
        "CES0500000003",  # Total Private Average Hourly Earnings of All Employees (Seasonally Adjusted)
        "CES0500000008",  # Total Private Average Hourly Earnings of Prod. and Nonsup. Employees (Seasonally Adjusted)
        "SMS31000000000000001"  # Nebraska, Total Nonfarm (Seasonally Adjusted)
    ]
    start_year = 2022  # Replace with your desired start year
    end_year = 2024  # Replace with your desired end year

    try:
        raw_data = fetch_bls_data(series_ids, start_year, end_year, api_key)
        processed_data = process_bls_data(raw_data)
        save_data_to_github(processed_data, repo_name, file_path, commit_message, github_token)
    except Exception as e:
        print(f"An error occurred: {e}")
