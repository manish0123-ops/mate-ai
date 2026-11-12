
import json
from pathlib import Path
from datetime import datetime

# Store reminders locally in the MATE folder
REMINDER_FILE = Path(__file__).with_name("reminders.json")


def load_reminders():
    if not REMINDER_FILE.exists():
        return []

    try:
        with open(REMINDER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read the reminders file.")
        return []


def save_reminders(reminders):
    with open(REMINDER_FILE, "w", encoding="utf-8") as file:
        json.dump(reminders, file, indent=4)


def add_reminder():
    title = input("What should I remind you about? ").strip()

    if not title:
        print("MATE: Reminder title cannot be empty.")
        return

    date_text = input(
        "Enter date and time (YYYY-MM-DD HH:MM): "
    ).strip()

    try:
        due_time = datetime.strptime(
            date_text, "%Y-%m-%d %H:%M"
        )

        if due_time <= datetime.now():
            print("MATE: Please enter a future date and time.")
            return

    except ValueError:
        print("MATE: Invalid date format.")
        print("Example: 2026-10-10 09:30")
        return

    reminders = load_reminders()

    reminders.append({
        "title": title,
        "due": due_time.strftime("%Y-%m-%d %H:%M"),
        "done": False
    })

    save_reminders(reminders)
    print("MATE: Reminder saved locally!")


def list_reminders():
    reminders = load_reminders()

    if not reminders:
        print("MATE: You have no saved reminders.")
        return

    now = datetime.now()
    print("\n--- Your Reminders ---")

    for number, reminder in enumerate(reminders, start=1):
        due_time = datetime.strptime(
            reminder["due"], "%Y-%m-%d %H:%M"
        )

        if reminder.get("done", False):
            status = "COMPLETED"
        elif due_time <= now:
            status = "DUE"
        else:
            status = "UPCOMING"

        print(
            f"{number}. {reminder['title']} | "
            f"{reminder['due']} | {status}"
        )


def main():
    while True:
        print("\n===== MATE REMINDERS =====")
        print("1. Add reminder")
        print("2. View reminders")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_reminder()
        elif choice == "2":
            list_reminders()
        elif choice == "3":
            print("MATE: Reminders saved. Goodbye!")
            break
        else:
            print("MATE: Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
