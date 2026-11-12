
import json
from pathlib import Path
from datetime import datetime

CALENDAR_FILE = Path(__file__).with_name("calendar.json")


def load_events():
    if not CALENDAR_FILE.exists():
        return []

    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
        return events if isinstance(events, list) else []
    except (OSError, json.JSONDecodeError):
        print("MATE: Could not read the calendar file.")
        return []


def save_events(events):
    with open(CALENDAR_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4)


def add_event():
    title = input("Event name: ").strip()

    if not title:
        print("MATE: Event name cannot be empty.")
        return

    date_text = input(
        "Date and time (YYYY-MM-DD HH:MM): "
    ).strip()

    try:
        event_time = datetime.strptime(
            date_text, "%Y-%m-%d %H:%M"
        )
    except ValueError:
        print("MATE: Invalid date format.")
        print("Example: 2026-10-15 14:30")
        return

    events = load_events()

    events.append({
        "title": title,
        "start": event_time.strftime("%Y-%m-%d %H:%M")
    })

    events.sort(key=lambda event: event["start"])
    save_events(events)

    print("MATE: Calendar event saved locally!")


def list_events():
    events = load_events()

    if not events:
        print("MATE: Your calendar is empty.")
        return

    now = datetime.now()

    print("\n===== YOUR LOCAL CALENDAR =====")

    for number, event in enumerate(events, start=1):
        event_time = datetime.strptime(
            event["start"], "%Y-%m-%d %H:%M"
        )

        if event_time < now:
            status = "PAST"
        else:
            status = "UPCOMING"

        print(
            f"{number}. {event['title']} | "
            f"{event['start']} | {status}"
        )
