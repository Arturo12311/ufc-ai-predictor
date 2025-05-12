import pandas as pd
import os
import time
from ufc_helpers import get_fighter_stats, calculate_diff
import requests
from bs4 import BeautifulSoup

DATASET_FILE = "large_dataset.csv"

# Load existing dataset
if os.path.exists(DATASET_FILE):
    df_existing = pd.read_csv(DATASET_FILE)
    seen_fights = set(zip(df_existing['r_fighter'], df_existing['b_fighter'], df_existing['event_name']))
    print(f"✅ Loaded {len(df_existing)} rows from existing dataset.")
else:
    df_existing = pd.DataFrame()
    seen_fights = set()
    print("📄 No existing dataset found. Starting fresh...")

# Get all completed UFC event URLs
def get_all_event_links():
    print("🔎 Collecting all event links...")
    base_url = "http://ufcstats.com/statistics/events/completed"
    event_links = []
    page = 1

    while True:
        url = f"{base_url}?page={page}"
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, 'html.parser')
        anchors = soup.select("table.b-statistics__table-events a[href*='event-details']")
        if not anchors:
            break
        for a in anchors:
            event_links.append(a['href'])
        page += 1
        time.sleep(0.5)
    print(f"✅ Found {len(event_links)} event links.")
    return event_links

# Get fight URLs from an event page
def get_fight_links(event_url):
    res = requests.get(event_url, timeout=5)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.select("tr.b-fight-details__table-row")
    links = []
    for row in rows:
        link = row.get("data-link")
        if link:
            links.append(link)
    return links

# Extract fight data from fight page
def extract_fight_data(fight_url):
    res = requests.get(fight_url, timeout=5)
    if res.status_code != 200:
        return None
    soup = BeautifulSoup(res.text, 'html.parser')

    # Fighters
    names = [tag.text.strip() for tag in soup.select("h3.b-fight-details__person-name")]
    if len(names) < 2:
        return None
    r_name, b_name = names[:2]

    # Event name
    event_name = soup.select_one("h2.b-content__title").text.strip()

    # Fighter profiles
    fighter_links = [a['href'] for a in soup.select("a.b-link.b-fight-details__person-link")]
    if len(fighter_links) < 2:
        return None
    r_stats = get_fighter_stats(fighter_links[0])
    b_stats = get_fighter_stats(fighter_links[1])

    if not r_stats or not b_stats:
        return None

    diffs = calculate_diff(r_stats, b_stats)
    fight_data = {
        'event_name': event_name,
        'r_fighter': r_stats['name'],
        'b_fighter': b_stats['name'],
        **diffs
    }
    return fight_data

# Main logic
all_event_links = get_all_event_links()[1:]
new_rows = []

for event_url in all_event_links:
    try:
        fight_urls = get_fight_links(event_url)
        for fight_url in fight_urls:
            try:
                fight_data = extract_fight_data(fight_url)
                if not fight_data:
                    continue
                key = (fight_data['r_fighter'], fight_data['b_fighter'], fight_data['event_name'])
                if key in seen_fights:
                    continue
                new_rows.append(fight_data)
                seen_fights.add(key)
                print(f"✅ Added: {key}")
            except Exception as e:
                print(f"❌ Error processing fight: {fight_url} — {e}")
            time.sleep(0.3)
    except Exception as e:
        print(f"❌ Error processing event: {event_url} — {e}")

if new_rows:
    df_new = pd.DataFrame(new_rows)
    df_all = pd.concat([df_existing, df_new], ignore_index=True)
    df_all.to_csv(DATASET_FILE, index=False)
    print(f"💾 Dataset updated: {len(df_all)} total rows saved to {DATASET_FILE}")
else:
    print("📭 No new fights to add.")