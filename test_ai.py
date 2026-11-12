
from ai_brain import ask_mate

print("MATE: Hello! I am your private AI Mate.")
print("MATE: Type 'exit' to stop.\n")

while True:
    message = input("You: ").strip()

    if message.lower() == "exit":
        print("MATE: Goodbye!")
        break

    if message:
        response = ask_mate(message)
        print("MATE:", response)
