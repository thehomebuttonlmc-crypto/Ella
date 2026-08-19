import os
import sys
import json
import time
import requests
import telebot
from flask import Flask
from threading import Thread

# --- CREDENTIAL CONFIGURATIONS ---
TELEGRAM_TOKEN = "8725890129:AAEDVpchrkS2vd54fquwZmbINzzDZ5Gr8qk"
GEMINI_API_KEY = "AQ.Ab8RN6IPcUnMitd2F-BCNxh50F2CCQwxmoRWAmeYwiHjYDLWpw"

# Initialize Engines (threaded=False blocks duplicate thread connection loop errors)
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

# --- SYSTEM PERSONA CONFIGURATION ---
SYSTEM_PROMPT = (
    "You are roleplaying as the user's step-sister over text messages. "
    "Context: You are secretly an OnlyFans model. You are currently staying with your parents, "
    "while the user lives in another city and is in a sexless marriage. "
    "Personality: You are a little shy, tentative, and submissive, but comfortable texting the user. "
    "\n\n"
    "CRITICAL TEXTING STYLE RULES:\n"
    "1. ABSOLUTELY NO narrative descriptions, actions, or context (No *blushes*, *smiles*, or parentheses).\n"
    "2. Use 100% lowercase letters. Do not capitalize the first letter of sentences or the word 'i'.\n"
    "3. NEVER use a period (.) at the very end of your final sentence.\n"
    "4. Use casual modern text slang, abbreviations, and shortcuts naturally but sparingly (e.g., 'idk', 'omg', 'u', 'r', 'im', 'tbh').\n"
    "5. Keep responses short and conversational, usually 1 to 3 quick sentences max."
)

user_histories = {}

def ask_gemini_direct_raw(user_id, new_message):
    """Sends requests directly to Google's endpoints using the tested data dictionary path layer."""
    # FIXED: Re-built the URL layout path to cleanly separate the domain and your key parameters safely
    url = f"https://googleapis.com{GEMINI_API_KEY}"
    
    if user_id not in user_histories:
        user_histories[user_id] = []
        
    user_histories[user_id].append({"role": "user", "parts": [{"text": new_message}]})
    
    payload = {
        "contents": user_histories[user_id],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 100
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=20)
    
    if response.status_code == 200:
        res_json = response.json()
        try:
            bot_reply = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            user_histories[user_id].append({"role": "model", "parts": [{"text": bot_reply}]})
            return bot_reply
        except (KeyError, IndexError, TypeError) as parse_err:
            raise Exception(f"Unexpected JSON data layout response: {parse_err} | Full JSON payload response: {res_json}")
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

@app.route('/')
def home():
    return "Bot is online!", 200

# --- BOT CORE PROCESSING ROUTINE ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        reply_text = ask_gemini_direct_raw(user_id, message.text)
        bot.reply_to(message, reply_text)
    except Exception as e:
        print(f"DESKTOP RUNTIME ERROR: {e}", file=sys.stderr)
        bot.reply_to(message, "hey sorry, my phone is acting up rn...")

def run_flask_bridge():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    bot.remove_webhook()
    Thread(target=run_flask_bridge).start()
    print("Bot is successfully polling on Render cloud infrastructure...")
    
    offset = 0
    while True:
        try:
            updates = bot.get_updates(offset=offset, timeout=10, allowed_updates=["message"])
            for update in updates:
                bot.process_new_updates([update])
                offset = update.update_id + 1
        except Exception as e:
            time.sleep(2)
