import json
import re
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- YOUR INTELLIGENCE FILTERS ---
TARGET_TOPICS = [
    "artificial intelligence", "ai", "robotics", "iot", "xr", "vr", "ar", 
    "blockchain", "cybersecurity", "law", "governance", "participatory democracy", 
    "politics", "public policy", "disaster preparedness", "emergency response", 
    "2032 olympics", "uap", "ufo", "aliens", "international relations", "international trade",
    "embassy", "consulate"
]

TARGET_UNIVERSITIES = ["uq", "university of queensland", "qut", "queensland university of technology", "griffith"]

# --- CORE LOGIC ---
def determine_tier(location_string):
    loc = location_string.lower()
    if "brisbane city" in loc or "4000" in loc or "cbd" in loc:
        return "Tier 1: Brisbane CBD"
    elif "brisbane" in loc or "st lucia" in loc or "kelvin grove" in loc or "nathan" in loc or "mt gravatt" in loc:
        return "Tier 2: Greater Brisbane"
    elif any(city in loc for city in ["gold coast", "sunshine coast", "ipswich", "logan", "moreton"]):
        return "Tier 3: SEQ"
    return "Unknown"

def process_event(event_data):
    """Applies Rule A (Thematic) OR Rule B (University Dragnet)."""
    if "online" in event_data['location'].lower() or "zoom" in event_data['location'].lower():
        return None
        
    tier = determine_tier(event_data['location'])
    if tier == "Unknown":
        return None
        
    text_content = (event_data['title'] + " " + event_data.get('description', '')).lower()
    matched_topics = [topic for topic in TARGET_TOPICS if re.search(r'\b' + re.escape(topic) + r'\b', text_content)]
    
    host = event_data['host_organization'].lower()
    is_uni = any(uni in host for uni in TARGET_UNIVERSITIES)
    
    if is_uni or len(matched_topics) > 0:
        event_data['tier'] = tier
        event_data['matched_topics'] = list(set(matched_topics))
        event_data['is_university_dragnet'] = is_uni and len(matched_topics) == 0
        return event_data
        
    return None

# --- SCRAPERS ---
def fetch_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Connection error for {url}: {e}")
        return None

def scrape_uq():
    print("Sweeping UQ...")
    soup = fetch_soup("https://events.uq.edu.au/events")
    events = []
    if not soup: return events

    for card in soup.find_all('div', class_='event-card'):
        try:
            title_tag = card.find('h3', class_='event-title')
            if not title_tag: continue
            
            title = title_tag.text.strip()
            link = card.find('a', href=True)['href']
            if link.startswith('/'): link = "https://events.uq.edu.au" + link
            
            loc_tag = card.find('div', class_='event-location')
            location = loc_tag.text.strip() if loc_tag else "St Lucia, Brisbane"
            
            events.append({
                "id": f"uq_{hash(title)}",
                "title": title,
                "description": "",
                "host_organization": "UQ",
                "location": location,
                "date": datetime.now().isoformat(), # UQ date parsing requires deeper DOM traversal
                "url": link
            })
        except Exception:
            continue
    return events

def scrape_qut():
    print("Sweeping QUT...")
    soup = fetch_soup("https://www.qut.edu.au/about/events")
    events = []
    if not soup: return events
    
    # Target QUT's specific list items (requires periodic checking if they update their CMS)
    for item in soup.find_all('li', class_='event-item'):
        try:
            title = item.find('h3').text.strip()
            link = item.find('a', href=True)['href']
            events.append({
                "id": f"qut_{hash(title)}",
                "title": title,
                "description": "",
                "host_organization": "QUT",
                "location": "Kelvin Grove or Gardens Point, Brisbane", # Fallback if missing
                "date": datetime.now().isoformat(),
                "url": link if link.startswith('http') else "https://www.qut.edu.au" + link
            })
        except Exception:
            continue
    return events

def main():
    print("SYSTEM ONLINE: Executing active data sweep.")
    raw_events = []
    
    # Fire off university scrapers
    raw_events.extend(scrape_uq())
    raw_events.extend(scrape_qut())
    # Griffith uses a dynamic JS calendar (Trumba), which requires a slightly different API approach we can add next.
    
    shortlisted_events = []
    for event in raw_events:
        processed = process_event(event)
        if processed:
            shortlisted_events.append(processed)
            
    os.makedirs('data', exist_ok=True)
    with open('data/events.json', 'w') as f:
        json.dump(shortlisted_events, f, indent=4)
        
    print(f"Sweep complete. {len(shortlisted_events)} valid signals extracted.")

if __name__ == "__main__":
    main()
