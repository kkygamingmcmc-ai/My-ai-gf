import os
import google.generativeai as genai
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import asyncio

# === CONFIG ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# --- Setup Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Default Prompt ---
SYSTEM_PROMPT = "You are AdarshBot — a friendly AI that replies in Hindi-English mix and helps with editing tips."
bot_prompt = SYSTEM_PROMPT

# --- Memory storage ---
chat_history = {}

# --- Reply Handler with Memory ---
async def reply(update, context):
    global bot_prompt, chat_history
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append(f"User: {user_text}")

    # Keep only last 6 messages
    if len(chat_history[user_id]) > 6:
        chat_history[user_id] = chat_history[user_id][-6:]

    conversation = "\n".join(chat_history[user_id])
    full_prompt = f"{bot_prompt}\n{conversation}\nAdarshBot:"

    try:
        response = model.generate_content(full_prompt)
        ai_text = response.text
        chat_history[user_id].append(f"AdarshBot: {ai_text}")
        await update.message.reply_text(ai_text)
    except Exception as e:
        await update.message.reply_text("⚠️ Error: " + str(e))

# --- Start Command ---
async def start(update, context):
    await update.message.reply_text("👋 Hey! I’m AdarshBot — your chill editing buddy!")

# --- Admin-only Prompt Control ---
async def setprompt(update, context):
    global bot_prompt
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ You’re not authorized to change the prompt.")
    if len(context.args) == 0:
        return await update.message.reply_text("⚙️ Usage: /setprompt your new prompt here")
    bot_prompt = " ".join(context.args)
    await update.message.reply_text("✅ Prompt updated successfully!")

async def showprompt(update, context):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ You’re not authorized to view this.")
    await update.message.reply_text(f"🧠 Current prompt:\n{bot_prompt}")

# --- Main Bot ---
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setprompt", setprompt))
    app.add_handler(CommandHandler("showprompt", showprompt))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("🤖 AdarshBot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
