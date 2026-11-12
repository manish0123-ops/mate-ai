
from flask import Flask, jsonify, request, render_template
from ai_brain import ask_mate

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "application": "MATE",
        "ai_backend": "local Ollama"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a message."}), 400

    try:
        reply = ask_mate(message.strip())
        return jsonify({
            "reply": str(reply or "I couldn't generate a response.")
        })
    except Exception:
        app.logger.exception("MATE AI request failed")
        return jsonify({
            "error": "Couldn't connect to the local AI. Check Ollama."
        }), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

