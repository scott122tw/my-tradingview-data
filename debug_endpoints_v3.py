import cloudscraper
import requests
import json

scraper = cloudscraper.create_scraper()

date_from = "2024-01-01"
date_to = "2026-02-13" # 2 years

url = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Try to filter by eventID in this endpoint
payload_filtered = {
    "country[]": "5",
    "importance[]": "3",
    "timeZone": "8",
    "timeFilter": "timeRemain",
    "currentTab": "custom",
    "submitFilters": "1",
    "limit_from": "0",
    "dateFrom": date_from,
    "dateTo": date_to,
    "eventID": "300", # Speculation
    "text": "Unemployment Rate" # Speculation (search text?)
}

print(f"Testing {url} with eventID filter...")

try:
    resp = scraper.post(url, data=payload_filtered, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        html_content = data.get('data', '')
        print(f"HTML Content Length: {len(html_content)}")
        # Check if it ONLY contains unemployment rate?
        # A simple check: count occurrences of "Unemployment Rate" vs total rows.
        print("Snippet:", html_content[:200])
        
        # Check specific row count
        count_unemployment = html_content.count("Unemployment Rate")
        print(f"Count of 'Unemployment Rate': {count_unemployment}")
    else:
        print(f"Failed: {resp.status_code}")
except Exception as e:
    print(f"Error: {e}")
