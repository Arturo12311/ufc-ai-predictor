# ufc_helpers.py

import requests
from bs4 import BeautifulSoup
import re
import math

def inches_to_cm(inches):
    return round(inches * 2.54, 2)

def feet_inches_to_cm(feet, inches):
    return round((feet * 30.48) + (inches * 2.54), 2)

def get_fighter_stats(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to load fighter page: {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.find('span', class_='b-content__title-highlight').text.strip()
    stats = soup.find_all('li', class_='b-list__box-list-item b-list__box-list-item_type_block')
    clean = lambda s: s.get_text(strip=True).split(':')[-1].strip()

    def extract_height(txt):
        match = re.match(r"(\d+)' (\d+)\"", txt)
        if match:
            return feet_inches_to_cm(int(match[1]), int(match[2]))
        return None

    def extract_weight(txt):
        match = re.match(r"(\d+) lbs.", txt)
        return round(int(match[1]) * 0.453592, 2) if match else None

    def extract_reach(txt):
        return inches_to_cm(int(txt.replace('"', '').strip())) if '"' in txt else None

    height = extract_height(clean(stats[0]))
    weight = extract_weight(clean(stats[1]))
    reach = extract_reach(clean(stats[2]))
    stance = clean(stats[3])
    dob = clean(stats[4])

    from datetime import datetime
    age = None
    try:
        dob = datetime.strptime(dob, '%b %d, %Y')
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        pass

    to_float = lambda x: float(x.strip('%')) / 100 if '%' in x else float(x)

    return {
        'name': name,
        'height': height,
        'weight': weight,
        'reach': reach,
        'stance': stance,
        'age': age,
        'SLpM_total': to_float(clean(stats[5])),
        'SApM_total': to_float(clean(stats[7])),
        'sig_str_acc_total': to_float(clean(stats[6])),
        'td_acc_total': to_float(clean(stats[11])),
        'str_def_total': to_float(clean(stats[8])),
        'td_def_total': to_float(clean(stats[12])),
        'sub_avg': to_float(clean(stats[13])),
        'td_avg': to_float(clean(stats[10]))
    }

def calculate_diff(red, blue):
    diff_keys = [
        'kd', 'sig_str', 'sig_str_att', 'sig_str_acc', 'str',
        'str_att', 'str_acc', 'td', 'td_att', 'td_acc', 'sub_att',
        'rev', 'ctrl_sec',
        'wins_total', 'losses_total', 'age', 'height', 'weight', 'reach',
        'SLpM_total', 'SApM_total', 'sig_str_acc_total', 'td_acc_total',
        'str_def_total', 'td_def_total', 'sub_avg', 'td_avg'
    ]

    def safe(val):
        return 0.0 if val is None else val

    return {
        f"{key}_diff": safe(red.get(key)) - safe(blue.get(key))
        for key in diff_keys
    }

def get_next_event_fighters():
    print("🔍 Fetching next UFC event fighters...")
    event_url = "http://ufcstats.com/statistics/events/upcoming"
    res = requests.get(event_url)
    if res.status_code != 200:
        raise Exception("Could not fetch upcoming events page.")

    soup = BeautifulSoup(res.text, 'html.parser')
    first_event_link = soup.select_one("table.b-statistics__table-events a")['href']
    print(f"📅 Upcoming Event: {first_event_link}")

    event_page = requests.get(first_event_link)
    soup = BeautifulSoup(event_page.text, 'html.parser')
    rows = soup.select("tr.b-fight-details__table-row")

    fights = []
    for row in rows:
        fighter_links = row.select("td.b-fight-details__table-col a")
        if len(fighter_links) >= 2:
            red_url = fighter_links[0]['href']
            blue_url = fighter_links[1]['href']
            fights.append((red_url, blue_url))
    print(f"✅ Found {len(fights)} fights in next card.")
    return fights
