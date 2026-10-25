import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("users.db")

# Create cursor
cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Save changes
conn.commit()

# Close database
conn.close()

print("Database Created Successfully!")