import cloudscraper

scraper = cloudscraper.create_scraper()

url_history = "https://www.investing.com/economic-calendar/Service/History"
url_get_history = "https://www.investing.com/economic-calendar/Service/getHistory"

payload = {
    "eventID": "300",
    "event_attr_id": "300",
    "dateFrom": "2023-01-01",
    "dateTo": "2024-01-01",
    "is_range": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/unemployment-rate-300"
}

print("Testing History...")
r1 = scraper.post(url_history, data=payload, headers=headers)
print(f"History: {r1.status_code}")

print("Testing getHistory...")
r2 = scraper.post(url_get_history, data=payload, headers=headers)
print(f"getHistory: {r2.status_code}")
if r2.status_code == 200:
    print(r2.text[:200])
