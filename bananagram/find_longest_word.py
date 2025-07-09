#!/usr/bin/env python3
import sys
import sqlite3
import itertools
from collections import Counter
import concurrent.futures

DB_FILE = 'words.db'

if len(sys.argv) != 2:
    print("Usage: python find_longest_word.py LETTERS")
    sys.exit(1)

input_letters = sys.argv[1].strip().upper()
if not input_letters.isalpha():
    print("Please provide a string of alphabetic letters.")
    sys.exit(1)

letters = list(input_letters)
letter_count = Counter(letters)

# Helper to generate all unique multisets (sorted letter combinations) of a given length
def unique_multisets(letters, length):
    counter = Counter(letters)
    def helper(prefix, counter, length):
        if length == 0:
            yield prefix
            return
        for letter in sorted(counter):
            if counter[letter] > 0:
                counter[letter] -= 1
                yield from helper(prefix + letter, counter, length - 1)
                counter[letter] += 1
    return set(''.join(sorted(ms)) for ms in helper('', counter, length))

# Worker function for a single word length, using batch queries
def find_words_of_length(length):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    found = set()
    multisets = list(unique_multisets(letters, length))
    if not multisets:
        conn.close()
        return (length, found)
    # Batch query using IN clause
    placeholders = ','.join('?' for _ in multisets)
    query = f'SELECT word, sorted_letters FROM anagrams WHERE sorted_letters IN ({placeholders})'
    c.execute(query, multisets)
    results = c.fetchall()
    for word, sorted_letters in results:
        if len(word) == length:
            found.add(word)
    conn.close()
    return (length, found)

# Try all possible lengths in parallel, from longest to shortest
max_len = len(letters)
lengths = list(range(max_len, 0, -1))
found_words = set()
max_length = 0

with concurrent.futures.ProcessPoolExecutor() as executor:
    # Submit all lengths in parallel
    futures = {executor.submit(find_words_of_length, l): l for l in lengths}
    for future in concurrent.futures.as_completed(futures):
        length, words = future.result()
        if words and length > max_length:
            found_words = words
            max_length = length
        # Early exit: if we found the longest possible, break
        if max_length == max_len:
            break
    # If we didn't find the absolute max, check for the next longest
    if not found_words:
        for l in range(max_len - 1, 0, -1):
            for future in futures:
                length, words = future.result()
                if length == l and words:
                    found_words = words
                    max_length = l
                    break
            if found_words:
                break

if found_words:
    print(f"Longest valid word(s) of length {max_length} from '{input_letters}': {', '.join(sorted(found_words))}")
else:
    print(f"No valid word can be formed from '{input_letters}'.") 