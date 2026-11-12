
from app_control import open_app, list_apps
from ai_brain import ask_mate, choose_app_name
from app_control import open_app, list_apps
import reminders
import calendar_manager
import email_manager

print("MATE: Your private AI Mate is ready!")
print("Try: open calculator, show reminders, add reminder")
print("Type 'exit' to quit.")

while True:
    message = input("\nYou: ").strip()

    if not message:
        continue

    command = message.lower()

    if command == "exit":
        print("MATE: Goodbye!")
        break

    
    elif command.startswith("open "):
        app_name = message[5:].strip()
        print("MATE:", open_app(app_name))

    elif command in ("list apps", "show apps", "list applications"):
        apps = sorted(
            set(list_apps() + ["Notepad", "Calculator"]),
            key=str.casefold
        )

        print(f"MATE found {len(apps)} application names:")
        for number, name in enumerate(apps, start=1):
            print(f"{number}. {name}")

    elif command.startswith(("open ", "launch ", "start ", "run ")):
        request_text = message.split(" ", 1)[1].strip()

        apps = sorted(
            set(list_apps() + ["Notepad", "Calculator"]),
            key=str.casefold
        )

        selected_app = choose_app_name(request_text, apps)

        if selected_app == "AMBIGUOUS":
            print("MATE: Please give me a more specific app name.")
        elif selected_app == "NONE":
            print("MATE: I couldn't find a suitable app.")
        elif selected_app:
            print("MATE:", open_app(selected_app))
        else:
            print(
                "MATE: I couldn't identify the app. "
                "Try 'list apps' to see available names."
            )

    elif command in ("show reminders", "list reminders"):
        reminders.list_reminders()

    elif command == "add reminder":
        reminders.add_reminder()

    
    elif command in ("add event", "create event"):
        calendar_manager.add_event()

    elif command in ("show calendar", "list events"):
        calendar_manager.list_events()
    

    
    elif command in ("create email", "draft email", "write email"):
        email_manager.create_draft()

    elif command in ("show drafts", "list drafts", "view email drafts"):
        email_manager.list_drafts()

    else:
        print("MATE:", ask_mate(message))
