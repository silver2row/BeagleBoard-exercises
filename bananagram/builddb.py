#! /usr/bin/env python3
import sqlite3

# Path to the dictionary file
DICT_FILE = 'Collins Scrabble Words (2019).txt'
# Path to the SQLite database file
DB_FILE = 'words.db'

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Create the table: sorted_letters (TEXT), word (TEXT)
c.execute('''
CREATE TABLE IF NOT EXISTS anagrams (
    sorted_letters TEXT,
    word TEXT
)
''')

# Create an index on sorted_letters for fast lookups
c.execute('CREATE INDEX IF NOT EXISTS idx_sorted_letters ON anagrams(sorted_letters)')

# Read the dictionary and insert each word with its sorted letters
with open(DICT_FILE) as f:
    batch = []
    BATCH_SIZE = 1000
    for line in f:
        word = line.strip().upper()
        if word.isalpha():
            sorted_letters = ''.join(sorted(word))
            batch.append((sorted_letters, word))
            if len(batch) >= BATCH_SIZE:
                c.executemany('INSERT INTO anagrams (sorted_letters, word) VALUES (?, ?)', batch)
                batch = []
    # Insert any remaining rows
    if batch:
        c.executemany('INSERT INTO anagrams (sorted_letters, word) VALUES (?, ?)', batch)

# Commit and close
conn.commit()
conn.close()

print(f"Database '{DB_FILE}' built from '{DICT_FILE}' with index on sorted_letters.") 
