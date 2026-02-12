import cloudscraper
import requests
import json

scraper = cloudscraper.create_scraper()

endpoints = [
    "https://www.investing.com/economic-calendar/Service/History",
    "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData",
    "https://www.investing.com/common/modules/js_instrument_chart/api/data.php"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/unemployment-rate-300"
}

payload_history = {
    "eventID": "300",
    "event_attr_id": "300",
    "dateFrom": "2020-01-01",
    "dateTo": "2023-01-01",
    "is_range": "1"
}

# Payload for getCalendarFilteredData might be different
payload_filtered = {
    "country[]": "5", # USA
    "importance[]": "3",
    "timeZone": "8",
    "timeFilter": "timeRemain",
    "currentTab": "custom",
    "submitFilters": "1",
    "limit_from": "0"
}

print("Testing endpoints...")

for url in endpoints:
    print(f"\nTesting {url}...")
    try:
        # Try as POST
        if "History" in url:
            resp = scraper.post(url, data=payload_history, headers=headers)
        elif "getCalendarFilteredData" in url:
             resp = scraper.post(url, data=payload_filtered, headers=headers)
        else:
            resp = scraper.get(url, headers=headers) # data.php might be get?
            
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Response preview:")
            print(resp.text[:200])
        else:
            print("Failed.")
    except Exception as e:
        print(f"Error: {e}")
