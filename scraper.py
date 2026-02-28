import json
import re
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from duckduckgo_search import DDGS

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
def determine_tier(location_string, is_web_fallback=False):
    loc = location_string.lower()
    if "brisbane city" in loc or "4000" in loc or "cbd" in loc:
        return "Tier 1: Brisbane CBD"
    elif "brisbane" in loc or "st lucia" in loc or "kelvin grove" in loc or "nathan" in loc or "mt gravatt" in loc:
        return "Tier 2: Greater Brisbane"
    elif any(city in loc for city in ["gold coast", "sunshine coast", "ipswich", "logan", "moreton"]):
        return "Tier 3: SEQ"
    
    # If the search engine found it using our SEQ keywords, but the snippet missed the city name, force it through.
    if is_web_fallback:
        return "Tier 3: SEQ (Area Assumed)"
        
    return "Unknown"

def process_event(event_data):
    if "online" in event_data['location'].lower() or "zoom" in event_data['location'].lower():
        return None
        
    is_web = event_data['host_organization'] == "Eventbrite/Meetup"
    tier = determine_tier(event_data['location'], is_web_fallback=is_web)
    
    if tier == "Unknown":
        return None
        
    text_content = (event_data['title'] + " " + event_data.get('description', '')).lower()
    matched_topics = [topic for topic in TARGET_TOPICS if re.search(r'\b' + re.escape(topic) + r'\b', text_content)]
    
    host = event_data['host_organization'].lower()
    is_uni = any(uni in host for uni in TARGET_UNIVERSITIES)
    
    if is_uni or len(matched_topics) > 0:
        event_data['tier'] = tier
        event_data['matched_topics'] = list(set(matched_topics)) if matched_topics else ["University Broadcast"]
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
    except Exception as e:
        print(f"Connection error for {url}: {e}")
        return None

def scrape_uq():
    print("Sweeping UQ...")
    soup = fetch_soup("https://events.uq.edu.au/events")
    events = []
    if not soup: return events

    # Relaxed search: look for any links containing '/event' to bypass strict class names
    for link in soup.find_all('a', href=True):
        href = link['href']
        title = link.text.strip()
        if '/event' in href and len(title) > 10: # Avoid grabbing nav links like "All Events"
            url = href if href.startswith('http') else "https://events.uq.edu.au" + href
            events.append({
                "id": f"uq_{hash(title)}",
                "title": title,
                "description": "",
                "host_organization": "UQ",
                "location": "St Lucia, Brisbane", # Fallback location to pass filter
                "date": datetime.now().isoformat(),
                "url": url
            })
    return events

def scrape_platforms_via_search():
    print("Sweeping Meetup & Eventbrite via DuckDuckGo...")
    events = []
    base_locations = '("Brisbane" OR "Gold Coast")'
    
    queries = [
        f'site:eventbrite.com.au OR site:meetup.com {base_locations} ("Artificial Intelligence" OR "Cybersecurity")',
        f'site:eventbrite.com.au OR site:meetup.com {base_locations} ("Law" OR "Governance" OR "Participatory Democracy" OR "Public Policy")',
        f'site:eventbrite.com.au OR site:meetup.com {base_locations} ("Disaster Preparedness" OR "Emergency Response" OR "UAP" OR "Aliens")'
    ]

    try:
        with DDGS() as ddgs:
            for query in queries:
                results = ddgs.text(query, max_results=10)
                if not results: continue
                
                for r in results:
                    snippet = r.get('body', '')
                    title = r.get('title', '').replace(" | Eventbrite", "").replace(" | Meetup", "")
                    events.append({
                        "id": f"web_{hash(r['href'])}",
                        "title": title[:100], # Keep titles clean
                        "description": snippet,
                        "host_organization": "Eventbrite/Meetup",
                        "location": snippet + " " + title, 
                        "date": datetime.now().isoformat(),
                        "url": r['href']
                    })
    except Exception as e:
        print(f"Search bypass error: {e}")
        
    return events

def main():
    print("SYSTEM ONLINE: Executing active data sweep.")
    raw_events = []
    
    raw_events.extend(scrape_uq())
    raw_events.extend(scrape_platforms_via_search()) 
    
    print(f"RAW SWEEP COMPLETE. Found {len(raw_events)} total potential signals.")
    
    shortlisted_events = []
    for event in raw_events:
        processed = process_event(event)
        if processed:
            shortlisted_events.append(processed)
            
    os.makedirs('data', exist_ok=True)
    with open('data/events.json', 'w') as f:
        json.dump(shortlisted_events, f, indent=4)
        
    print(f"TRIAGE COMPLETE. {len(shortlisted_events)} signals passed the filters and were saved.")

if __name__ == "__main__":
    main()
