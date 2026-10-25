import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("fruit.db")

# Create cursor
cur = conn.cursor()

# Create prediction table
cur.execute("""
CREATE TABLE IF NOT EXISTS prediction(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fruit TEXT,
    condition TEXT,
    accuracy REAL
)
""")

# Save changes
conn.commit()

# Close database
conn.close()

print("Database Created Successfully!")