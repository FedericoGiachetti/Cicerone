import os
import datetime as dt
from typing import Optional, List, Dict

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def _get_credentials() -> Credentials:
    """Carica o crea nuove credenziali OAuth per Google Calendar."""
    client_secrets_path = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secrets.json")
    token_path = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def _format_event(event: Dict) -> str:
    """Formatta un evento in stringa leggibile."""
    start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
    title = event.get("summary", "Senza titolo")
    location = event.get("location", "")
    return f"{title} — {start}{f' — {location}' if location else ''}"

def get_calendar_events(days_ahead: int = 14, max_results: int = 5) -> str:
    """Ritorna una stringa con i prossimi eventi del calendario personale."""
    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = dt.datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + dt.timedelta(days=days_ahead)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return "Nessun evento in calendario nel periodo."

    return "; ".join([_format_event(e) for e in events])
