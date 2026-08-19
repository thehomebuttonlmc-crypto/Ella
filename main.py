import os
import sys
from threading import Thread
import telebot
from flask import Flask
from google import genai
from google.genai import types

# --- SECURE CREDENTIAL ROUTING MODULE ---
TELEGRAM_TOKEN = "8725890129:AAEDVpchrkS2vd54fquwZmbINzzDZ5Gr8qk"
GEMINI_API_KEY = "AQ.Ab8RN6IPcUnMitd2F-BCNxh50F2CCQwxmoRWAmeYwiHjYDLWpw"

# Initialize standard clients natively using the modern GenAI library
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)
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

generation_config = types.GenerateContentConfig(
    temperature=0.9,
    max_output_tokens=100,
    system_instruction=SYSTEM_PROMPT
)

user_chats = {}

# This web layout gives an online address to ping so the server stays active
@app.route('/')
def home():
    return "Bot is online!", 200

# --- BOT CORE PROCESSING ROUTINE ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        
        # Open continuous chat loops natively with the modern SDK framework
        if user_id not in user_chats:
            user_chats[user_id] = client.chats.create(
                model='gemini-2.5-flash',
                config=generation_config
            )

        chat = user_chats[user_id]
        response = chat.send_message(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"DESKTOP RUNTIME ERROR: {e}", file=sys.stderr)
        bot.reply_to(message, "hey sorry, my phone is acting up rn...")

def run_flask_bridge():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    bot.remove_webhook()
    
    # Fire up the background port helper
    Thread(target=run_flask_bridge).start()
    
    print("Bot is successfully polling on Render cloud infrastructure...")
    bot.infinity_polling()
