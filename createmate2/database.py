import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("CreateMate_bot.db")
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    social_handle TEXT,
    viral_content TEXT,
    challenge_started INTEGER DEFAULT 0,
    current_day INTEGER DEFAULT 0
)
""")

# Create the daily_posts table to track progress
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
