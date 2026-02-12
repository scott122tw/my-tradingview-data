import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import os
import re

# Configuration
API_URL = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"
OUTPUT_DIR = "seeds"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "unemployment_forecast.csv")

def extract_month_year(release_date, text):
    """
    Extracts the period month from the event text (e.g., 'Unemployment Rate (Jan)')
    and determines the correct year based on release date.
    Returns strings 'YYYY-MM'.
    """
    if not text:
        return ""
    
    match = re.search(r'\((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\)', text, re.IGNORECASE)
    if not match:
        return ""
    
    month_str = match.group(1).title()
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    period_month = month_map.get(month_str[:3])
    if not period_month:
        return ""
    
    release_year = release_date.year
    release_month = release_date.month
    
    # Logic to determine year of the data
    # If period month is 12 (Dec) and release month is 1 (Jan), year is previous year.
    year = release_year
    if period_month > release_month and (period_month - release_month) > 6:
       year = release_year - 1
    elif period_month < release_month and (release_month - period_month) > 6:
        # e.g. Release Dec, Period Jan (Next year? Unlikely for past data but possible for revisions)
        year = release_year + 1
        
    return f"{year}-{period_month:02d}"

def fetch_unemployment_data():
    scraper = cloudscraper.create_scraper()
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.investing.com/economic-calendar/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    all_data = []
    
    # Check if we should fetch history (full run) or just update (incremental)
    # Default to 180 days update to be safe for daily runs
    total_days = 180
    chunk_days = 90
    
    current_date = datetime.now()
    start_date = current_date - timedelta(days=total_days)
    end_date = current_date
    
    # Iterate in chunks
    chunk_start = start_date
    while chunk_start < end_date:
        chunk_end = min(chunk_start + timedelta(days=chunk_days), end_date)
        
        date_from_str = chunk_start.strftime('%Y-%m-%d')
        date_to_str = chunk_end.strftime('%Y-%m-%d')
        
        print(f"Fetching chunk: {date_from_str} to {date_to_str}...")
        
        payload = {
            "country[]": "5",       # USA
            "importance[]": "3",    # High Importance
            "timeZone": "28",       # Taipei (GMT+8)
            "timeFilter": "timeRemain",
            "currentTab": "custom",
            "submitFilters": "1",
            "limit_from": "0",
            "dateFrom": date_from_str,
            "dateTo": date_to_str
        }

        try:
            resp = scraper.post(API_URL, data=payload, headers=headers)
            
            if resp.status_code == 200:
                json_data = resp.json()
                html = json_data.get('data', '')
                
                if html:
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Filter for Event ID 300 (Unemployment Rate)
                    event_rows = soup.find_all('tr', attrs={'event_attr_id': '300'})
                    print(f"  Found {len(event_rows)} Unemployment Rate events in this chunk.")
                    
                    for row in event_rows:
                        timestamp_str = row.get('data-event-datetime', '')
                        
                        actual_td = row.find('td', {'id': lambda x: x and x.startswith('eventActual_')})
                        forecast_td = row.find('td', {'id': lambda x: x and x.startswith('eventForecast_')})
                        previous_td = row.find('td', {'id': lambda x: x and x.startswith('eventPrevious_')})
                        event_td = row.find('td', class_='event')
                        
                        actual_text = actual_td.get_text(strip=True) if actual_td else ""
                        forecast_text = forecast_td.get_text(strip=True) if forecast_td else ""
                        previous_text = previous_td.get_text(strip=True) if previous_td else ""
                        event_text = event_td.get_text(strip=True) if event_td else ""

                        if timestamp_str and actual_text:
                            try:
                                # Format: "2023/10/06 08:30:00" -> 21:30 via TZ=28 response
                                dt_obj = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
                                
                                release_date = dt_obj.strftime("%Y-%m-%d")
                                release_time = dt_obj.strftime("%H:%M")
                                period_month = extract_month_year(dt_obj, event_text)
                                
                                all_data.append({
                                    "發布日期": release_date,
                                    "時間": release_time,
                                    "失業率月份": period_month,
                                    "實際": actual_text,
                                    "預測": forecast_text,
                                    "前值": previous_text
                                })
                            except ValueError:
                                pass
            else:
                print(f"Failed chunk {date_from_str} with status {resp.status_code}")

        except Exception as e:
            print(f"Error fetching chunk {date_from_str}: {e}")
            
        # Move to next chunk
        chunk_start = chunk_end + timedelta(days=1)
        # Be polite
        time.sleep(1)

    # Load existing data handling
    # If columns mismatch, we overwrite to establish new schema
    final_df = pd.DataFrame()
    cols_order = ["發布日期", "時間", "失業率月份", "實際", "預測", "前值"]

    if all_data:
        final_df = pd.DataFrame(all_data)
        
        # Clean numeric data
        for col in ['實際', '預測', '前值']:
            if col in final_df.columns:
                final_df[col] = final_df[col].astype(str).str.replace('%', '').str.strip()
                final_df[col] = final_df[col].replace(['--', 'Wait', '', '\xa0', 'nan', 'None'], '')
        
        final_df = final_df[final_df['實際'] != '']
        final_df = final_df.sort_values(by='發布日期')
        final_df = final_df.drop_duplicates(subset=['發布日期'], keep='last')
        
    if os.path.exists(OUTPUT_FILE):
        try:
            old_df = pd.read_csv(OUTPUT_FILE, dtype=str)
            # Check if headers match new schema
            if set(old_df.columns) == set(cols_order):
                print(f"Appending to existing file ({len(old_df)} records).")
                if not final_df.empty:
                    combined = pd.concat([old_df, final_df], ignore_index=True)
                    combined = combined.drop_duplicates(subset=['發布日期'], keep='last')
                    final_df = combined.sort_values(by='發布日期')
                else:
                    final_df = old_df
            else:
                print("Old file schema mismatch. Overwriting with new data.")
        except Exception as e:
            print(f"Error reading existing file: {e}")

    if not final_df.empty:
        # Reorder columns
        final_df = final_df[cols_order] 
        final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\nSaved {len(final_df)} records to {OUTPUT_FILE}")
        print(final_df.tail())
    else:
        print("No data available to save.")

if __name__ == "__main__":
    fetch_unemployment_data()
