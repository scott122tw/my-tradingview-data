import cloudscraper
import requests
import json
import datetime

scraper = cloudscraper.create_scraper()

# Update to a recent date where we expect data
date_from = "2026-02-10"
date_to = "2026-02-13"

url = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Payload filtering for US High Importance events
payload_filtered = {
    "country[]": "5", # USA
    "importance[]": "3", # High
    "timeZone": "8",
    "timeFilter": "timeRemain",
    "currentTab": "custom",
    "submitFilters": "1",
    "limit_from": "0",
    "dateFrom": date_from,
    "dateTo": date_to
}

print(f"Testing {url} with date range {date_from} to {date_to}...")

try:
    resp = scraper.post(url, data=payload_filtered, headers=headers)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("Response received.")
        try:
            data = resp.json()
            # The 'data' field usually contains HTML.
            print("Keys in JSON:", data.keys())
            html_content = data.get('data', '')
            print(f"HTML Content Length: {len(html_content)}")
            if len(html_content) > 0:
                 print("Snippet of HTML:")
                 print(html_content[:500])
                 
                 # Check for "Unemployment Rate" in the HTML
                 if "Unemployment Rate" in html_content:
                     print("\nFound 'Unemployment Rate' in the response provided by getCalendarFilteredData!")
                 else:
                     print("\n'Unemployment Rate' NOT found in the response.")
            else:
                print("No HTML data found.")
        except json.JSONDecodeError:
            print("Could not decode JSON.")
            print(resp.text[:500])
    else:
        print("Request failed.")
except Exception as e:
    print(f"Error: {e}")
