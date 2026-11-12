
from ai_brain import (
    ask_mate,
    initialize_cognitive_core,
    get_conversation_history,
    reset_conversation,
    build_cognitive_context
)

print("\n=== MATE COGNITIVE AI BRAIN TEST ===")

# 1. Initialize cognitive architecture
initialize_cognitive_core()

print("\n[1] Cognitive architecture initialized.")

# 2. Retrieve cognitive context
context = build_cognitive_context(
    "MATE project and memory"
)

print("\n[2] Cognitive context retrieved:")
print(context)

# 3. Send a message to local Ollama
reply = ask_mate(
    "What do you know about my MATE project?"
)

print("\n[3] MATE response:")
print(reply)

# 4. Check conversation history
history = get_conversation_history()

print("\n[4] Conversation messages:", len(history))

# 5. Test conversation reset
reset_conversation()

history = get_conversation_history()

print("[5] Conversation reset:", len(history) == 0)

print("\n=== TEST COMPLETED ===")
