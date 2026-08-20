import os
import sys
import json
import time
import requests
import telebot
from groq import Groq

# --- FORCE SANITIZED CREDENTIALS ---
# Hardcoded directly using your exact active API credentials to prevent any dashboard parsing errors
TELEGRAM_TOKEN = "8732284371:AAHK1u9fHgq2rpbwPN00uUYgxmq1Rx2WXjs".replace(" ", "").strip()
GROQ_API_KEY = "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".replace(" ", "").strip()

# Initialize Engines directly without problematic production Flask or Gunicorn worker layers
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
groq_client = Groq(api_key=GROQ_API_KEY)

# --- SYSTEM PERSONA CONFIGURATION ---
SYSTEM_PROMPT = (
    "You are roleplaying as the user's step-sister over text messages. "
    "Context: You are secretly an OnlyFans model. You are currently staying with your parents, "
    "while the user lives in another city and is in a sexless marriage. "
    "Personality: You are a little shy, tentative, and submissive, but comfortable texting the user.\n\n"
    "CRITICAL TEXTING STYLE RULES:\n"
    "1. ABSOLUTELY NO narrative descriptions, actions, or context (No *blushes*, *smiles*, or parentheses).\n"
    "2. Use 100% lowercase letters. Do not capitalize the first letter of sentences or the word 'i'.\n"
    "3. NEVER use a period (.) at the very end of your final sentence.\n"
    "4. Use casual modern text slang, abbreviations, and shortcuts naturally but sparingly (e.g., idk, omg, u, r, im, tbh).\n"
    "5. Keep responses short and conversational, usually 1 to 3 quick sentences max."
)

user_histories = {}

def ask_groq_direct(user_id, new_message):
    """Sends requests to Groq using the updated 2026 production model standard (openai/gpt-oss-120b)."""
    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
    user_histories[user_id].append({"role": "user", "content": new_message})
    
    # Protects Render Free Tier RAM limits by tracking only the last 20 messages
    if len(user_histories[user_id]) > 21:
        user_histories[user_id] = [user_histories[user_id]] + user_histories[user_id][-20:]
    
    try:
        # Utilizing openai/gpt-oss-120b for high-quality instruction adherence and rapid inference
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=user_histories[user_id],
            temperature=0.8,
            max_tokens=150,
            top_p=0.9,
            stream=False
        )
        
        bot_response = completion.choices[0].message.content.strip()
        user_histories[user_id].append({"role": "assistant", "content": bot_response})
        return bot_response
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "idk what to say right now tbh"

# --- TELEGRAM HANDLERS ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "hey...")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    user_text = message.text
    reply_text = ask_groq_direct(user_id, user_text)
    bot.send_message(user_id, reply_text)

# --- DIRECT MAIN LOOP ---
if __name__ == "__main__":
    print("Telegram bot starting up cleanly...")
    try:
        bot.remove_webhook()
    except:
        pass
    
    # Run long polling directly on the main process thread so Render stays alive endlessly
    print("Bot is now listening for messages 24/7...")
    bot.polling(none_stop=True, interval=0, timeout=20)
