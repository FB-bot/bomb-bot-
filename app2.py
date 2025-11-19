# app.py
import os
from flask import Flask, request, abort
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Dispatcher, CommandHandler

# Environment variables (set these in Render or local env)
TOKEN = os.environ.get("8592092723:AAENndcv24gscZCqBPys42rl0udNSbVKRVY")
CHANNEL_URL = os.environ.get("https://t.me/mysmartearn_bot/mysmartearn?startapp=ref1849126202", "https://t.me/your_channel")  # পরিবর্তন করুন
DEV_USERNAME = os.environ.get("noobxvau", "your_dev_username")        # পরিবর্তন করুন (বিনা @)
WEBHOOK_URL = os.environ.get("https://bomb-bot.onrender.com")  # Optional: https://<your-domain>/webhook

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required.")

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

app = Flask(__name__)

# -------------------------
# Command handler: /start
# -------------------------
def start(update, context):
    user = update.effective_user
    name = user.first_name if user and user.first_name else "Guest"

    welcome_text = (
        f"👋 <b>Welcome, {name}!</b>\n\n"
        f"Welcome to <b>NOOB HACKER BD</b> — official bot .\n"
        f"Welcome to <b>Sms bombing এ যাওয়ার জন্য নিচের Open Bomb বাটনে ক্লিক করুন ✅</b>\n\n"
        f"Developer Info:\n"
        f"• Name: <b>NOOBXVAU</b>\n"
        f"• Role: Developer / Contact\n\n"
        f"Choose an option below to join the channel or contact the developer."
    )

    keyboard = [
        [
            InlineKeyboardButton("Join Channel", url=CHANNEL_URL),
            InlineKeyboardButton("Contact Developer", url=f"tg://resolve?domain={DEV_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send as reply to /start
    if update.message:
        update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# Register handler
dispatcher.add_handler(CommandHandler("start", start))

# -------------------------
# Flask route for Telegram webhook
# -------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), bot)
            dispatcher.process_update(update)
        except Exception as e:
            # logging optional
            print("Error processing update:", e)
            abort(400)
        return "OK"
    else:
        abort(405)

# Simple root route to test service is up
@app.route("/", methods=["GET"])
def index():
    return "Telegram bot is running."

# Optionally set webhook when starting (if WEBHOOK_URL env provided)
if __name__ == "__main__":
    if WEBHOOK_URL:
        # ensure webhook endpoint ends with /webhook
        hook = WEBHOOK_URL if WEBHOOK_URL.endswith("/webhook") else WEBHOOK_URL.rstrip("/") + "/webhook"
        res = bot.set_webhook(hook)
        print("set_webhook result:", res)
    # For local dev you might run: python app.py (but Render uses gunicorn)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
