import json
import re
from datetime import datetime
import os

# Your predefined thematic filters
TARGET_TOPICS = [
    "artificial intelligence", "ai", "robotics", "iot", "xr", "vr", "ar", 
    "blockchain", "cybersecurity", "law", "governance", "participatory democracy", 
    "politics", "public policy", "disaster preparedness", "emergency response", 
    "2032 olympics", "uap", "ufo", "aliens", "international relations", "international trade",
    "embassy", "consulate"
]

TARGET_UNIVERSITIES = ["uq", "university of queensland", "qut", "queensland university of technology", "griffith"]

def determine_tier(location_string):
    loc = location_string.lower()
    if "brisbane city" in loc or "4000" in loc or "cbd" in loc:
        return "Tier 1: Brisbane CBD"
    elif "brisbane" in loc or "st lucia" in loc or "kelvin grove" in loc:
        return "Tier 2: Greater Brisbane"
    elif any(city in loc for city in ["gold coast", "sunshine coast", "ipswich", "logan", "moreton"]):
        return "Tier 3: SEQ"
    return "Unknown"

def process_event(event_data):
    """Applies Rule A (Thematic) OR Rule B (University)."""
    # Exclude online events
    if "online" in event_data['location'].lower() or "zoom" in event_data['location'].lower():
        return None
        
    tier = determine_tier(event_data['location'])
    if tier == "Unknown":
        return None # Outside geographic scope
        
    text_content = (event_data['title'] + " " + event_data.get('description', '')).lower()
    matched_topics = [topic for topic in TARGET_TOPICS if re.search(r'\b' + re.escape(topic) + r'\b', text_content)]
    
    host = event_data['host_organization'].lower()
    is_uni = any(uni in host for uni in TARGET_UNIVERSITIES)
    
    # Apply OR logic
    if is_uni or len(matched_topics) > 0:
        event_data['tier'] = tier
        event_data['matched_topics'] = list(set(matched_topics))
        event_data['is_university_dragnet'] = is_uni and len(matched_topics) == 0
        return event_data
        
    return None

def main():
    # Placeholder for your actual scraping functions
    # e.g., raw_events = scrape_uq() + scrape_qut() + scrape_eventbrite()
    raw_events = [
        {
            "id": "uq_1",
            "title": "Introduction to AI in Law",
            "description": "Discussing the future of legal tech.",
            "host_organization": "UQ",
            "location": "St Lucia, Brisbane",
            "date": "2026-03-15T10:00:00",
            "url": "https://events.uq.edu.au/example"
        }
    ]
    
    shortlisted_events = []
    for event in raw_events:
        processed = process_event(event)
        if processed:
            shortlisted_events.append(processed)
            
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save to JSON for the frontend to consume
    with open('data/events.json', 'w') as f:
        json.dump(shortlisted_events, f, indent=4)
        
    print(f"Successfully saved {len(shortlisted_events)} events.")

if __name__ == "__main__":
    main()
