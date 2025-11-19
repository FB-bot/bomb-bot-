import os
import json
import requests
from flask import Flask, request, Response

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Render এ সেট করবেন
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN environment variable is required")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
WELCOME_TEXT = "Assalamu Alaikum! 👋\n\nEta demo Telegram bot. Kichu jiggasha korte /start likhun."

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Telegram demo bot is running."

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)
    # safety check
    if not update:
        return Response("ok", status=200)

    # message event handling
    message = update.get("message") or update.get("edited_message")
    if not message:
        return Response("ok", status=200)

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    # If user sent /start -> send welcome message
    if text and text.strip().lower().startswith("/start"):
        send_message(chat_id, WELCOME_TEXT)
    else:
        # optional: echo or ignore other messages
        send_message(chat_id, "Demo bot: ami shudhu /start handle kori. /start try korun.")

    return Response("ok", status=200)

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        # log to console (Render logs-এ দেখবেন)
        print("Failed to send message:", e)

if __name__ == "__main__":
    # Local run (for local testing)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
