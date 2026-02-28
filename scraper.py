import json
import re
import os
import requests
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from duckduckgo_search import DDGS

TARGET_TOPICS = [
    "artificial intelligence", "ai", "robotics", "iot", "xr", "vr", "ar", 
    "blockchain", "cybersecurity", "law", "governance", "participatory democracy", 
    "politics", "public policy", "disaster preparedness", "emergency response", 
    "2032 olympics", "uap", "ufo", "aliens", "international relations", "international trade",
    "embassy", "consulate"
]

TARGET_UNIVERSITIES = ["uq", "university of queensland", "qut", "queensland university of technology", "griffith"]

def determine_tier(location_string, is_web_fallback=False):
    loc = location_string.lower()
    if "brisbane city" in loc or "4000" in loc or "cbd" in loc:
        return "Tier 1: Brisbane CBD"
    elif "brisbane" in loc or "st lucia" in loc or "kelvin grove" in loc or "nathan" in loc or "mt gravatt" in loc:
        return "Tier 2: Greater Brisbane"
    elif any(city in loc for city in ["gold coast", "sunshine coast", "ipswich", "logan", "moreton"]):
        return "Tier 3: SEQ"
    if is_web_fallback:
        return "Tier 3: SEQ (Area Assumed)"
    return "Unknown"

def process_event(event_data):
    if "online" in event_data['location'].lower() or "zoom" in event_data['location'].lower():
        return None
    is_web = event_data['host_organization'] == "Eventbrite/Meetup"
    tier = determine_tier(event_data['location'], is_web_fallback=is_web)
    if tier == "Unknown": return None
        
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

def fetch_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return BeautifulSoup(response.content, 'html.parser')
    except:
        return None

def scrape_uq():
    soup = fetch_soup("https://events.uq.edu.au/events")
    events = []
    if not soup: return events
    for link in soup.find_all('a', href=True):
        href = link['href']
        title = link.text.strip()
        if '/event' in href and len(title) > 10:
            events.append({
                "id": f"uq_{hash(title)}",
                "title": title,
                "description": "",
                "host_organization": "UQ",
                "location": "St Lucia, Brisbane",
                "date": datetime.now().isoformat(),
                "url": href if href.startswith('http') else "https://events.uq.edu.au" + href
            })
    return events

def scrape_platforms_via_search():
    events = []
    queries = ['site:eventbrite.com.au "Brisbane" "Artificial Intelligence"']
    try:
        with DDGS() as ddgs:
            for query in queries:
                results = ddgs.text(query, max_results=5)
                if not results: continue
                for r in results:
                    events.append({
                        "id": f"web_{hash(r['href'])}",
                        "title": r.get('title', '')[:100],
                        "description": r.get('body', ''),
                        "host_organization": "Eventbrite/Meetup",
                        "location": r.get('body', '') + " Brisbane", 
                        "date": datetime.now().isoformat(),
                        "url": r['href']
                    })
    except Exception as e:
        return [{"error": str(e)}] # Pass the error out to display it
    return events

def main():
    raw_events = []
    error_log = "None"
    
    # Run scrapers
    uq_events = scrape_uq()
    web_events = scrape_platforms_via_search()
    
    # Check if DDGS threw a block error
    if len(web_events) > 0 and "error" in web_events[0]:
        error_log = web_events[0]["error"]
        web_events = []
        
    raw_events.extend(uq_events)
    raw_events.extend(web_events)
    
    shortlisted_events = []
    for event in raw_events:
        processed = process_event(event)
        if processed:
            shortlisted_events.append(processed)
            
    # --- DIAGNOSTIC CARD INJECTION ---
    diagnostic_card = {
        "id": "diagnostic_1",
        "title": f"SYSTEM LOG: {len(raw_events)} Raw Pulled, {len(shortlisted_events)} Passed Filter",
        "description": f"UQ Scraped: {len(uq_events)} | Web Scraped: {len(web_events)} | Error Log: {error_log}",
        "host_organization": "System Diagnostic",
        "location": "Brisbane CBD", 
        "date": datetime.now().isoformat(),
        "url": "#",
        "tier": "Tier 1: Brisbane CBD",
        "matched_topics": ["Diagnostics"]
    }
    shortlisted_events.insert(0, diagnostic_card)
            
    os.makedirs('data', exist_ok=True)
    with open('data/events.json', 'w') as f:
        json.dump(shortlisted_events, f, indent=4)

if __name__ == "__main__":
    main()
