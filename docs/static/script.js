document.addEventListener("DOMContentLoaded", () => {
    const app = document.getElementById("app");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const conversation = document.getElementById("conversation");
    const errorMessage = document.getElementById("error-message");

    console.log("MATE initialized");

    if (!form || !input || !sendButton || !conversation) {
        console.error("MATE: Required HTML elements are missing.");
        return;
    }

    function addMessage(role, text) {
        const row = document.createElement("div");
        row.className = `message-row ${role}`;

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.textContent = text;

        row.appendChild(bubble);
        conversation.appendChild(row);

        if (app) {
            app.classList.add("has-messages");
        }

        conversation.scrollTop = conversation.scrollHeight;
        return bubble;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const message = input.value.trim();

        if (!message || sendButton.disabled) {
            return;
        }

        errorMessage.textContent = "";
        addMessage("user", message);

        input.value = "";
        sendButton.disabled = true;

        const waiting = addMessage("assistant", "Thinking...");

        
try {
    // Public demo response engine
    const userMessage = message.toLowerCase().trim();

    let aiResponse;

    if (userMessage.includes("hello") || userMessage.includes("hi")) {
        aiResponse = "Hello! I'm MATE, your personal AI workspace. How can I help you today?";
    } 
    else if (userMessage.includes("who are you") || userMessage.includes("what is mate")) {
        aiResponse = "I'm MATE — Metacognitive Adaptive Thinking Engine. I'm an experimental personal AI assistant designed around memory, contextual understanding, reflection and continuous improvement.";
    } 
    else if (userMessage.includes("memory")) {
        aiResponse = "Memory is an important part of MATE. My architecture explores persistent storage, semantic retrieval, memory relationships and contradiction detection.";
    } 
    else if (userMessage.includes("capabilities") || userMessage.includes("features")) {
        aiResponse = "My experimental capabilities include persistent memory, semantic search, self-reflection, capability evaluation, learning plans and local AI integration.";
    } 
    else if (userMessage.includes("project")) {
        aiResponse = "MATE is a personal AI research project built using Python, Flask, Ollama and SQLite. Its goal is to explore a more context-aware and adaptive personal assistant.";
    } 
    else {
        aiResponse = "That's interesting! I'm currently running in public demonstration mode. My full AI reasoning engine is not connected in this demo, but you can explore MATE's architecture and capabilities through this interface.";
    }

    waiting.textContent = aiResponse;

    // Make MATE speak the response
    mateSpeak(aiResponse);


        } catch (error) {
            waiting.textContent = "I couldn't complete that request.";
            errorMessage.textContent = error.message;
            console.error("MATE chat error:", error);
        } finally {
            sendButton.disabled = false;
            input.focus();
            conversation.scrollTop = conversation.scrollHeight;
        }
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            form.requestSubmit();
        }
    });
});
// ========================================
// MATE VOICE INPUT
// ========================================

const micButton = document.getElementById("mic-button");

if (micButton) {
    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        micButton.disabled = true;
        micButton.title =
            "Voice recognition is not supported by this browser.";

        console.warn(
            "MATE: Speech recognition is not supported."
        );
    } else {
        const recognition = new SpeechRecognition();

        recognition.lang = "en-IN";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            micButton.classList.add("listening");
            micButton.title = "Listening...";
        };

       
        recognition.onresult = (event) => {
           const transcript =
               event.results[0][0].transcript.trim();

           const input =
             document.getElementById("message-input");

          if (input && transcript) {
            input.value = transcript;

        // Automatically submit the recognized voice message.
        const form = input.closest("form");

        if (form) {
            if (typeof form.requestSubmit === "function") {
                form.requestSubmit();
            } else {
                form.dispatchEvent(
                    new Event("submit", {
                        bubbles: true,
                        cancelable: true
                    })
                );
            }
        }
    }
};


        recognition.onerror = (event) => {
            console.error(
                "MATE voice recognition error:",
                event.error
            );

            if (event.error === "not-allowed") {
                alert(
                    "Please allow microphone access in your browser."
                );
            }
        };

        recognition.onend = () => {
            micButton.classList.remove("listening");
            micButton.title = "Start voice input";
        };

        micButton.addEventListener("click", () => {
            try {
                recognition.start();
            } catch (error) {
                console.error(
                    "Could not start voice recognition:",
                    error
                );
            }
        });
    }
}

// ========================================
// MATE TEXT-TO-SPEECH
// ========================================


function mateSpeak(text) {
    if (!("speechSynthesis" in window)) {
        console.warn("Speech synthesis is not supported.");
        return;
    }

    // Stop any previous speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Dark Siren voice settings
    utterance.lang = "en-IN";
    utterance.rate = 0.82;   // Slow, deliberate speech
    utterance.pitch = 0.78;  // Lower, darker pitch
    utterance.volume = 1.0;

    function speakWithVoice() {
        const voices = window.speechSynthesis.getVoices();

        // Prefer a feminine-sounding English voice
        const preferredVoice = voices.find(voice =>
            /aria|jenny|samantha|zira|karen|moira|female/i.test(voice.name)
            && /^en(-|$)/i.test(voice.lang)
        );

        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        window.speechSynthesis.speak(utterance);
    }

    // Wait for browser voices to load if necessary
    if (window.speechSynthesis.getVoices().length > 0) {
        speakWithVoice();
    } else {
        window.speechSynthesis.onvoiceschanged = () => {
            window.speechSynthesis.onvoiceschanged = null;
            speakWithVoice();
        };
    }
}
