from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import sqlite3
import asyncio

# ✅ Create SQLite Database and Tables (Run this once)
conn = sqlite3.connect("trendspark.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    social_handle TEXT,
    viral_content TEXT,
    challenge_started INTEGER DEFAULT 0,
    current_day INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    day INTEGER,
    post_link TEXT,
    views INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

conn.commit()
conn.close()

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu when bot starts."""
    keyboard = [
        [InlineKeyboardButton("📚 Guide to Content Creation", callback_data='guide')],
        [InlineKeyboardButton("🚀 How to be Creator in 2025", callback_data='creator_2025')],
        [InlineKeyboardButton("🎯 Start 21 Days Challenge", callback_data='challenge')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to TrendSpark! 👋\n\n"
        "Please choose an option from the menu below:",
        reply_markup=reply_markup
    )

# ✅ Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Answer callback

    if query.data == 'guide':
        await query.message.reply_text("📚 Content Creation Guide:\n\n1. Choose a niche...\nMore content coming!")
    
    elif query.data == 'creator_2025':
        await query.message.reply_text("🚀 Guide on being a content creator in 2025 coming soon!")
    
    elif query.data == 'challenge':
        await query.message.reply_text(
            "🎯 Ready for the 21-Day Challenge?\n\n"
            "Type /startchallenge when you're ready to begin!"
        )

# ✅ Start 21-Day Challenge & Store in SQLite
async def start_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the 21-day challenge and store progress in SQLite."""
    user_id = update.message.from_user.id

    conn = sqlite3.connect("trendspark.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, challenge_started, current_day) VALUES (?, ?, ?)", (user_id, 1, 1))
    else:
        cursor.execute("UPDATE users SET challenge_started = ?, current_day = ? WHERE user_id = ?", (1, 1, user_id))

    conn.commit()
    conn.close()

    await update.message.reply_text(
        "🚀 21-Day Challenge started!\n\n"
        "Please share your first content link!"
    )

    asyncio.create_task(send_daily_reminders(update, context, user_id))

# ✅ Send daily reminders & track progress in SQLite
async def send_daily_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send daily reminders and update progress in SQLite."""
    for day in range(1, 22):  # 21 days
        await asyncio.sleep(5)  # Testing with 5 seconds instead of 24 hours

        conn = sqlite3.connect("trendspark.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if user and user[3] == 1:  # Challenge started
            cursor.execute("UPDATE users SET current_day = ? WHERE user_id = ?", (day, user_id))
            conn.commit()

            await context.bot.send_message(
                chat_id=user_id,
                text=f"📅 Day {day} of your 21-Day Challenge!\n\n"
                     "Time to post your content. Send the link below!"
            )
        else:
            break  # Stop reminders if the challenge is no longer active

        conn.close()

# ✅ Handle user messages & save daily posts in SQLite
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and store daily posts in SQLite."""
    user_id = update.message.from_user.id
    user_input = update.message.text

    conn = sqlite3.connect("trendspark.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user and user[3] == 1:  # Challenge started
        current_day = user[4]  # Get current day

        # Save post link
        cursor.execute(
            "INSERT INTO daily_posts (user_id, day, post_link, views) VALUES (?, ?, ?, ?)",
            (user_id, current_day, user_input, None)
        )
        conn.commit()

        await update.message.reply_text(
            f"✅ Post saved for Day {current_day}! Now, enter the number of views."
        )

    conn.close()

# ✅ Main function
def main():
    application = Application.builder().token("7732444052:AAGNTQh_YLpL3U9XcAkHFNPq0PNQme9nJOQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("startchallenge", start_challenge))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
