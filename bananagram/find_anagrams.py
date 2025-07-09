#!/usr/bin/env python3
import sys
import sqlite3

DB_FILE = 'words.db'

if len(sys.argv) != 2:
    print("Usage: python find_anagrams.py WORD")
    sys.exit(1)

input_word = sys.argv[1].strip().upper()
if not input_word.isalpha():
    print("Please provide a single alphabetic word.")
    sys.exit(1)

# Alphabetize the letters in the input word
sorted_letters = ''.join(sorted(input_word))

# Connect to the database and search for anagrams
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('SELECT word FROM anagrams WHERE sorted_letters = ?', (sorted_letters,))
results = c.fetchall()
conn.close()

# Print the found anagrams (excluding the input word itself, if desired)
anagrams = [row[0] for row in results if row[0] != input_word]

if anagrams:
    print(f"Anagrams for '{input_word}': {', '.join(anagrams)}")
else:
    print(f"No anagrams found for '{input_word}'.") 