# app.py
import os
import json
import requests
from flask import Flask, request, Response

# === অবশ্যই environment variable এ TELEGRAM_TOKEN রাখবেন ===
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN environment variable is required")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ==========================
# Developer info (আপনি এখানে আপনার তথ্য লিখে বদলাবেন)
# আপনি চাইলে এগুলো Environment variables-ও ব্যবহার করতে পারেন।
DEVELOPER_NAME = "Rahim Uddin"
DEVELOPER_ROLE = "Bot Developer • Python Engineer"
DEVELOPER_BIO = "আমি সুন্দর, দ্রুত ও maintainable কোডে বিশ্বাস করি। Bot, API ও DevOps-এ অভিজ্ঞ।"
DEVELOPER_GITHUB = "https://github.com/your-gh"
DEVELOPER_LINKEDIN = "https://linkedin.com/in/your-profile"
DEVELOPER_TELEGRAM_URL = "https://t.me/noobxvau"
DEVELOPER_WEBSITE = "https://your-site.example.com"
GROUP_INVITE_LINK = "https://t.me/joinchat/XXXX"  # আপনার গ্রুপ invite link
BOT_NAME = "BombBot"
# ==========================

app = Flask(__name__)

# Pretty HTML templates
WELCOME_TEMPLATE = """
<b>👋 স্বাগতম, {first_name}!</b>

আপনি <b>{bot_name}</b>-এ এসে পৌঁছেছেন — স্বল্প কিন্তু মার্জিত একটি ডেমো বট।  
নীচের বাটনগুলো ব্যবহার করে ডেভেলপারকে কনট্যাক্ট করুন, গ্রুপে যোগ দিন বা ডেভেলপারের বিবরণ দেখুন।

<i>কমান্ড / ফিচার চান? বলুন — আমি যোগ করে দিব।</i>
"""

DEV_INFO_HTML = """
<b>🧑‍💻 {name}</b>
<i>{role}</i>

{bio}

<u>🔗 প্রোফাইল ও যোগাযোগ</u>
• Website: <a href="{website}">{website}</a>
• GitHub: <a href="{github}">{github}</a>
• LinkedIn: <a href="{linkedin}">{linkedin}</a>
• Telegram: <a href="{tlink}">{tlink}</a>

<b>🛠️ দক্ষতা</b>
• Python • Bots • APIs • Docker • CI/CD

<i>প্রোজেক্ট/কাস্টম কাজ চান? উপরের "Contact Developer" বাটনে ক্লিক করে মেসেজ পাঠান।</i>
""".strip()

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("send_message error:", e)
        return None

def answer_callback(callback_id, text=None, show_alert=False):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id, "show_alert": show_alert}
    if text:
        payload["text"] = text
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("answer_callback error:", e)

@app.route("/", methods=["GET"])
def index():
    return f"{BOT_NAME} is running."

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)

    # Logging (Render logs-এ দেখবেন)
    try:
        print("INCOMING UPDATE:", json.dumps(update, ensure_ascii=False))
    except Exception:
        pass

    # Handle callback_query (button press)
    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq.get("data", "")
        callback_id = cq.get("id")
        # get chat id (if present)
        chat_id = None
        if cq.get("message") and cq["message"].get("chat"):
            chat_id = cq["message"]["chat"]["id"]
        # Acknowledge callback (silent)
        answer_callback(callback_id)
        if data == "dev_info":
            html = DEV_INFO_HTML.format(
                name=DEVELOPER_NAME,
                role=DEVELOPER_ROLE,
                bio=DEVELOPER_BIO,
                website=DEVELOPER_WEBSITE,
                github=DEVELOPER_GITHUB,
                linkedin=DEVELOPER_LINKEDIN,
                tlink=DEVELOPER_TELEGRAM_URL
            )
            send_message(chat_id, html, parse_mode="HTML")
        else:
            send_message(chat_id, "অজানা কাজ।")
        return Response("ok", status=200)

    # Handle normal messages
    message = update.get("message") or update.get("edited_message")
    if not message:
        return Response("ok", status=200)

    text = (message.get("text") or "").strip()
    chat = message.get("chat", {}) or {}
    chat_id = chat.get("id")
    user = message.get("from", {}) or {}
    first_name = user.get("first_name") or user.get("username") or "বন্ধু"

    if text.lower().startswith("/start"):
        welcome = WELCOME_TEMPLATE.format(first_name=first_name, bot_name=BOT_NAME)

        keyboard = {
            "inline_keyboard": [
                [{"text": "🧾 Developer Info", "callback_data": "dev_info"}],
                [
                    {"text": "💬 Contact Developer", "url": DEVELOPER_TELEGRAM_URL},
                    {"text": "👥 Join Group", "url": GROUP_INVITE_LINK}
                ],
                [
                    {"text": "🌐 Website", "url": DEVELOPER_WEBSITE},
                    {"text": "🐙 GitHub", "url": DEVELOPER_GITHUB}
                ]
            ]
        }
        send_message(chat_id, welcome, reply_markup=keyboard, parse_mode="HTML")
    else:
        send_message(chat_id, "আমি মূলত /start কমান্ড handle করি — অনুগ্রহ করে /start পাঠান।")

    return Response("ok", status=200)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
