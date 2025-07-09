#!/usr/bin/env python3
import sys
import itertools
from collections import Counter
import multiprocessing

# Load dictionary from the system word list.
# Only include words that are purely alphabetic (no hyphens, apostrophes, etc.) and convert them to uppercase for uniformity.
with open('Collins Scrabble Words (2019).txt') as f:
    WORDS = set(word.strip().upper() for word in f if word.strip().isalpha())

# Build a set of all valid prefixes from the dictionary for early pruning
PREFIXES = set()
for word in WORDS:
    for i in range(2, len(word)+1):  # Only prefixes of length >=2
        PREFIXES.add(word[:i])

# Check if a word is valid (exists in the dictionary)
def is_valid_word(word):
    return word in WORDS

# Check if a string is a valid prefix of any word in the dictionary
def is_valid_prefix(prefix):
    return prefix in PREFIXES

# Generate all valid words that can be made from the given letters
def get_all_words(letters):
    letter_counts = Counter(letters)  # Count available letters
    valid_words = set()
    for word in WORDS:
        wc = Counter(word)
        # Only include the word if it can be formed from the available letters
        if all(wc[c] <= letter_counts[c] for c in wc):
            valid_words.add(word)
    return valid_words

# Check if a word can be placed at a given position in the grid
def can_place_word(grid, word, row, col, direction):
    # direction: 'across' (horizontal) or 'down' (vertical)
    if direction == 'across':
        # Check if the word fits horizontally
        if col + len(word) > len(grid[0]):
            return False
        for i, c in enumerate(word):
            cell = grid[row][col + i]
            # The cell must be empty or match the letter being placed
            if cell != '.' and cell != c:
                return False
        return True
    else:
        # Check if the word fits vertically
        if row + len(word) > len(grid):
            return False
        for i, c in enumerate(word):
            cell = grid[row + i][col]
            if cell != '.' and cell != c:
                return False
        return True

# Place a word on the grid and return a new grid (does not modify the original)
def place_word(grid, word, row, col, direction):
    new_grid = [list(r) for r in grid]  # Deep copy of the grid
    if direction == 'across':
        for i, c in enumerate(word):
            new_grid[row][col + i] = c
    else:
        for i, c in enumerate(word):
            new_grid[row + i][col] = c
    return new_grid

# Get a list of all letters currently used in the grid
def used_letters(grid):
    return [c for row in grid for c in row if c != '.']

# Early pruning: check all 2+ letter sequences in rows and columns are valid words or prefixes
def is_grid_partial_valid(grid):
    size = len(grid)
    # Check all horizontal (across) sequences
    for r in range(size):
        c = 0
        while c < size:
            if grid[r][c] != '.':
                start = c
                while c < size and grid[r][c] != '.':
                    c += 1
                word = ''.join(grid[r][start:c])
                if len(word) > 1 and not (is_valid_word(word) or is_valid_prefix(word)):
                    return False
            else:
                c += 1
    # Check all vertical (down) sequences
    for c in range(size):
        r = 0
        while r < size:
            if grid[r][c] != '.':
                start = r
                while r < size and grid[r][c] != '.':
                    r += 1
                word = ''.join(grid[i][c] for i in range(start, r))
                if len(word) > 1 and not (is_valid_word(word) or is_valid_prefix(word)):
                    return False
            else:
                r += 1
    return True

# Check that all words in the grid (across and down) are valid
def is_grid_valid(grid):
    size = len(grid)
    # Check all horizontal (across) words
    for r in range(size):
        c = 0
        while c < size:
            if grid[r][c] != '.':
                start = c
                while c < size and grid[r][c] != '.':
                    c += 1
                word = ''.join(grid[r][start:c])
                # Only check words longer than 1 letter
                if len(word) > 1 and not is_valid_word(word):
                    return False
            else:
                c += 1
    # Check all vertical (down) words
    for c in range(size):
        r = 0
        while r < size:
            if grid[r][c] != '.':
                start = r
                while r < size and grid[r][c] != '.':
                    r += 1
                word = ''.join(grid[i][c] for i in range(start, r))
                if len(word) > 1 and not is_valid_word(word):
                    return False
            else:
                r += 1
    return True

# Recursive backtracking solver to fill the grid with all letters
def solve(letters, size, grid=None):
    if grid is None:
        # Start with an empty grid filled with '.'
        grid = [['.' for _ in range(size)] for _ in range(size)]
    used = used_letters(grid)
    remaining = list(letters)
    # Remove already used letters from the list of available letters
    for c in used:
        if c in remaining:
            remaining.remove(c)
    # If all letters are used, check if the grid is valid
    if not remaining:
        if is_grid_valid(grid):
            return grid
        return None
    # Try to place a word using the remaining letters
    words = get_all_words(remaining)
    # Try longer words first for efficiency
    words = sorted(words, key=lambda w: -len(w))
    for word in words:
        for r in range(size):
            for c in range(size):
                for direction in ['across', 'down']:
                    if can_place_word(grid, word, r, c, direction):
                        new_grid = place_word(grid, word, r, c, direction)
                        # Early pruning: check if the grid is still potentially valid
                        if not is_grid_partial_valid(new_grid):
                            continue  # Prune this branch
                        result = solve(letters, size, new_grid)
                        if result:
                            return result
    return None  # No valid arrangement found

# Print the grid to the console
def print_grid(grid):
    for row in grid:
        print(' '.join(row))

# Helper for multiprocessing: solve for a specific grid size
def solve_for_size(args):
    letters, size = args
    grid = solve(letters, size)
    return (size, grid)

# Interactive mode: prompt user to add one letter at a time and show the grid after each addition, using multicore solving
def interactive_mode():
    print("Interactive Bananagrams mode. Enter one letter at a time. Type 'quit' to exit.")
    letters = []
    while True:
        print(f"Current letters: {''.join(letters)}")
        inp = input("Enter a letter (or 'quit' to finish): ").strip().upper()
        if inp == 'QUIT':
            print("Exiting interactive mode.")
            break
        if len(inp) != 1 or not inp.isalpha():
            print("Please enter a single alphabetic letter.")
            continue
        letters.append(inp)
        n = len(letters)
        import math
        min_size = int(math.ceil(n ** 0.5))
        sizes = list(range(min_size, n+1))
        found = False
        try:
            with multiprocessing.Pool() as pool:
                for size, grid in pool.imap_unordered(solve_for_size, [(letters, s) for s in sizes]):
                    if grid:
                        print("Possible grid:")
                        print_grid(grid)
                        found = True
                        break
            if not found:
                print("No valid Bananagram could be formed with the given letters.")
        except KeyboardInterrupt:
            # Allow user to interrupt a long solve and continue
            print("\nSolve interrupted. You can enter another letter or 'quit' to exit.")
            continue

# Main entry point: choose batch or interactive mode, both using multicore solving
def main():
    if len(sys.argv) == 2:
        # Batch mode: all letters at once, use multicore
        letters = sys.argv[1].upper()
        n = len(letters)
        import math
        min_size = int(math.ceil(n ** 0.5))
        sizes = list(range(min_size, n+1))
        found = False
        with multiprocessing.Pool() as pool:
            for size, grid in pool.imap_unordered(solve_for_size, [(letters, s) for s in sizes]):
                if grid:
                    print_grid(grid)
                    found = True
                    break
        if not found:
            print("No valid Bananagram could be formed with the given letters.")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main() 