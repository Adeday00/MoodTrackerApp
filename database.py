import sqlite3

# Connects to the SQLite database and creates the 'moods' table if it doesn't exist
def connect():
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY,
            date TEXT,
            mood INTEGER,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to add a mood entry
def add_mood(date, mood, notes):
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO moods (date, mood, notes) VALUES (?, ?, ?)', (date, mood, notes))
    conn.commit()
    conn.close()

# Function to retrieve all mood entries
def get_moods():
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM moods')
    results = cursor.fetchall()
    conn.close()
    return results

# Run this code to initialize the database
if __name__ == "__main__":
    connect()
    print("Database initialized and table created.")
