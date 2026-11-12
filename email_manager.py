
from pathlib import Path
from datetime import datetime
from ai_brain import ask_mate

DRAFTS_FOLDER = Path(__file__).with_name("email_drafts")


def create_draft():
    print("\n===== CREATE EMAIL DRAFT =====")

    recipient = input("Recipient name or email (optional): ").strip()
    subject = input("Email subject: ").strip()
    purpose = input("What should the email say? ").strip()
    tone = input("Tone (professional/friendly/formal): ").strip()

    if not subject or not purpose:
        print("MATE: Subject and purpose are required.")
        return

    if not tone:
        tone = "professional"

    prompt = f"""
Write an email draft using the following details.

Recipient: {recipient or "Not specified"}
Subject: {subject}
Purpose: {purpose}
Tone: {tone}

Return the email body only.
Do not claim that the email has been sent.
"""

    print("\nMATE: Writing your draft with the local AI...")

    body = ask_mate(prompt)

    print("\n===== EMAIL PREVIEW =====")
    print("To:", recipient or "Not specified")
    print("Subject:", subject)
    print()
    print(body)

    confirm = input(
        "\nSave this draft locally? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("MATE: Draft not saved.")
        return

    DRAFTS_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = DRAFTS_FOLDER / f"draft_{timestamp}.txt"

    content = (
        f"To: {recipient or 'Not specified'}\n"
        f"Subject: {subject}\n"
        f"Created: {datetime.now().isoformat(timespec='seconds')}\n"
        f"\n{body}\n"
    )

    try:
        filename.write_text(content, encoding="utf-8")
        print(f"MATE: Draft saved locally at:\n{filename}")
    except OSError as error:
        print(f"MATE: Could not save the draft: {error}")


def list_drafts():
    if not DRAFTS_FOLDER.exists():
        print("MATE: You have no saved email drafts.")
        return

    drafts = sorted(DRAFTS_FOLDER.glob("draft_*.txt"))

    if not drafts:
        print("MATE: You have no saved email drafts.")
        return

    print("\n===== SAVED EMAIL DRAFTS =====")

    for number, draft in enumerate(drafts, start=1):
        print(f"{number}. {draft.name}")

    choice = input(
        "\nEnter a draft number to view it, or press Enter to return: "
    ).strip()

    if not choice:
        return

    if not choice.isdigit():
        print("MATE: Please enter a valid number.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(drafts):
        print("MATE: Draft number not found.")
        return

    try:
        print("\n" + drafts[index].read_text(encoding="utf-8"))
    except OSError as error:
        print(f"MATE: Could not read the draft: {error}")
