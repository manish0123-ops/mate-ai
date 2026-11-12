
import json
import time
from importlib import import_module
from pathlib import Path
from datetime import datetime

try:
    winotify = import_module("winotify")
except ImportError:
    winotify = None

REMINDER_FILE = Path(__file__).with_name("reminders.json")

# Check every 30 seconds
CHECK_INTERVAL = 30


def load_reminders():
    if not REMINDER_FILE.exists():
        return []

    try:
        with open(REMINDER_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_reminders(reminders):
    with open(REMINDER_FILE, "w", encoding="utf-8") as file:
        json.dump(reminders, file, indent=4)


def check_due_reminders():
    reminders = load_reminders()
    now = datetime.now()
    changed = False

    for reminder in reminders:
        if reminder.get("done", False):
            continue

        try:
            due_time = datetime.strptime(
                reminder["due"], "%Y-%m-%d %H:%M"
            )
        except (KeyError, ValueError):
            continue

        if due_time <= now:
            title = reminder.get("title", "Your reminder is due.")
            if winotify is None:
                print(f"MATE Reminder: {title}")
            else:
                notification = winotify.Notification(
                    app_id="Private AI Mate",
                    title="MATE Reminder",
                    msg=title,
                    duration="long"
                )
                notification.set_audio(winotify.audio.Default, loop=False)
                notification.show()

            reminder["done"] = True
            changed = True

    if changed:
        save_reminders(reminders)


def main():
    print("MATE reminder service started.")
    print("Keep this window open to receive notifications.")

    while True:
        check_due_reminders()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
