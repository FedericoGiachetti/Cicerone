import requests
import os

def get_events(city="Milano"):
    key = os.getenv("EVENTBRITE_API_KEY")
    url = f"https://www.eventbriteapi.com/v3/events/search/?location.address={city}&sort_by=date"
    headers = {"Authorization": f"Bearer {key}"}
    r = requests.get(url, headers=headers).json()
    events = []
    for e in r.get("events", []):
        name = e["name"]["text"]
        start = e["start"]["local"]
        events.append(f"{name} alle ore {start}")
    return "; ".join(events) if events else "Nessun evento trovato."
