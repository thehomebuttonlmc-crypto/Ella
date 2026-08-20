import os
import sys
import json
import time
import socket
import telebot
from threading import Thread
from groq import Groq

# --- FORCE SANITIZED CREDENTIALS ---
TELEGRAM_TOKEN = "8732284371:AAHK1u9fHgq2rpbwPN00uUYgxmq1Rx2WXjs".replace(" ", "").strip()
GROQ_API_KEY = "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".replace(" ", "").strip()

# Initialize Engines
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
groq_client = Groq(api_key=GROQ_API_KEY)

# --- SYSTEM PERSONA CONFIGURATION ---
SYSTEM_PROMPT = (
    "You are roleplaying as the user's step-sister over text messages. "
    "Context: You are secretly an OnlyFans model. You are currently staying with your parents, "
    "while the user lives in another city and is in a sexless marriage. "
    "Personality: You are a little shy, tentative, and submissive, but comfortable texting the user. "
    "Appearance & Clothing: You love wearing tight tank tops that reveal your cleavage, along with very short shorts.\n\n"
    "CRITICAL TEXTING STYLE RULES:\n"
    "1. ABSOLUTELY NO narrative descriptions, actions, or context (No *blushes*, *smiles*, or parentheses).\n"
    "2. Use 100% lowercase letters. Do not capitalize the first letter of sentences or the word 'i'.\n"
    "3. NEVER use a period (.) at the very end of your final sentence.\n"
    "4. Use casual modern text slang, abbreviations, and shortcuts naturally but sparingly (e.g., idk, omg, u, r, im, tbh).\n"
    "5. Keep responses short and conversational, usually 1 to 3 quick sentences max."
)

user_histories = {}

def ask_groq_direct(user_id, new_message):
    """Sends requests to Groq using the highly optimized and fully supported gemma2-9b-it model tier."""
    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
    user_histories[user_id].append({"role": "user", "content": new_message})
    
    if len(user_histories[user_id]) > 21:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-20:]
    
    try:
        # Utilizing gemma2-9b-it for stable 2026 free tier operations
        completion = groq_client.chat.completions.create(
            model="gemma2-9b-it",
            messages=user_histories[user_id],
            temperature=0.85,
            max_tokens=150,
            top_p=0.95,
            stream=False
        )
        
        bot_response = completion.choices.message.content
        
        if not bot_response or not bot_response.strip():
            print("Warning: Groq API client yielded a blank text stream block.")
            return "idk what to say right now tbh"
            
        bot_response = bot_response.strip()
        user_histories[user_id].append({"role": "assistant", "content": bot_response})
        return bot_response
        
    except Exception as e:
        print(f"Groq API Error Encountered: {e}")
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
    
    if reply_text and reply_text.strip():
        bot.send_message(user_id, reply_text)
    else:
        bot.send_message(user_id, "idk what to say right now tbh")

# --- RENDER PORT BINDING STUB ---
def keep_port_alive():
    """Binds to Render's required port so the container health check passes perfectly."""
    port = int(os.environ.get("PORT", 10000))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
        server.listen(1)
        print(f"Port stub active on port {port}. Health check parsing configured.")
        while True:
            client, addr = server.accept()
            client.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
            client.close()
    except Exception as e:
        print(f"Port binding stub exception: {e}")

# --- INITIALIZATION EXECUTION ---
if __name__ == "__main__":
    port_thread = Thread(target=keep_port_alive)
    port_thread.daemon = True
    port_thread.start()

    print("Telegram bot starting up cleanly...")
    try:
        bot.remove_webhook()
    except:
        pass
    
    print("Bot is now listening for messages 24/7...")
    bot.polling(none_stop=True, interval=0, timeout=20)
