import requests
import json
import pandas as pd
import datetime
import os

DATE_TRACKER_FILE = "last_fetch_date.json"
DATA_FILE = "bls_data.xlsx"

def should_update_data():
    """Check if data should be fetched (if last fetch >30 days ago or not fetched yet)."""
    if not os.path.exists(DATE_TRACKER_FILE):
        return True
    with open(DATE_TRACKER_FILE, "r") as file:
        data = json.load(file)
        last_fetch_date = datetime.datetime.strptime(data["last_fetch"], "%Y-%m-%d")
    return (datetime.datetime.now() - last_fetch_date).days >= 30

def update_fetch_date():
    """Update the last fetch date to today."""
    with open(DATE_TRACKER_FILE, "w") as file:
        json.dump({"last_fetch": datetime.datetime.now().strftime("%Y-%m-%d")}, file)

def fetch_bls_data():
    """Fetch data from the BLS API and save it as an Excel file."""
    headers = {'Content-type': 'application/json'}
    current_year = datetime.datetime.now().year
    last_year = current_year - 1
    data = json.dumps({
        "seriesid": [
            "LNS14000000", 
            "CES0000000001", 
            "LNS11000000", 
            "LNS12000000", 
            "LNS13000000", 
            "CES0500000002", 
            "CES0500000007"
        ],
        "startyear": str(last_year),
        "endyear": str(current_year)
    })
    
    response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = response.json()

    all_series_data = []
    for series in json_data.get('Results', {}).get('series', []):
        seriesId = series['seriesID']
        for item in series['data']:
            # Only include monthly data (M01-M12)
            if 'M01' <= item['period'] <= 'M12':
                all_series_data.append({
                    "Series ID": seriesId,
                    "Year": int(item['year']),
                    "Month": int(item['period'][1:]),
                    "Value": float(item['value'])
                })

    if all_series_data:
        df = pd.DataFrame(all_series_data)
        df.to_excel(DATA_FILE, index=False)  # Save to Excel file
        update_fetch_date()
        print("Data successfully fetched and updated.")
    else:
        print("No data returned from the BLS API. Please check the API request.")

if __name__ == "__main__":
    if should_update_data():
        print("Fetching updated data...")
        fetch_bls_data()
    else:
        print("Data is up to date. No new fetch required.")
