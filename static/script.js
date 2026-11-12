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
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Request failed.");
            }

            
            const aiResponse = data.reply || "No response received.";

            waiting.textContent = aiResponse;

// Make MATE speak the AI response.
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
