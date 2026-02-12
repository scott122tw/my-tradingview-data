import cloudscraper
import json
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

date_from = "2026-02-10"
date_to = "2026-02-13"
url = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/",
    "Content-Type": "application/x-www-form-urlencoded"
}
payload = {
    "country[]": "5",
    "importance[]": "3",
    "timeZone": "8",
    "limit_from": "0",
    "dateFrom": date_from,
    "dateTo": date_to,
    "submitFilters": "1"
}

resp = scraper.post(url, data=payload, headers=headers)
if resp.status_code == 200:
    data = resp.json()
    print("PIDS:", data.get('pids'))
    html = data.get('data', '')
    soup = BeautifulSoup(html, 'lxml')
    rows = soup.find_all('tr', {'class': 'js-event-item'})
    
    print(f"Found {len(rows)} events.")
    for row in rows:
        text = row.get_text(strip=True)
        if "Unemployment Rate" in text:
            print("\nFOUND UNEMPLOYMENT RATE ROW:")
            print(f"ID: {row.get('id')}")
            print(f"Event Attr ID: {row.get('event_attr_id')}")
            print(f"Data Event Datetime: {row.get('data-event-datetime')}")
            print(f"Full Row Text: {text}")
else:
    print("Failed")
