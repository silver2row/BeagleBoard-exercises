#!/usr/bin/env python3
import sys
import itertools
from collections import Counter
import multiprocessing
import sqlite3

# Database file path
DB_FILE = 'words.db'

# Global database connection (will be initialized when needed)
db_conn = None

def get_db_connection():
    """Get a database connection, creating it if needed"""
    global db_conn
    if db_conn is None:
        db_conn = sqlite3.connect(DB_FILE)
    return db_conn

def close_db_connection():
    """Close the database connection"""
    global db_conn
    if db_conn:
        db_conn.close()
        db_conn = None

# Check if a word is valid (exists in the dictionary)
def is_valid_word(word):
    conn = get_db_connection()
    c = conn.cursor()
    sorted_letters = ''.join(sorted(word.upper()))
    c.execute('SELECT word FROM anagrams WHERE sorted_letters = ? AND word = ?', 
             (sorted_letters, word.upper()))
    result = c.fetchone()
    return result is not None

# Check if a string is a valid prefix of any word in the dictionary
def is_valid_prefix(prefix):
    conn = get_db_connection()
    c = conn.cursor()
    # Check if there are any words that start with this prefix
    c.execute('SELECT word FROM anagrams WHERE word LIKE ? LIMIT 1', (prefix.upper() + '%',))
    result = c.fetchone()
    return result is not None

# Generate all valid words that can be made from the given letters
def get_all_words(letters):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Generate all possible sorted letter combinations
    letter_combos = set()
    for length in range(1, len(letters) + 1):
        for combo in itertools.combinations(letters, length):
            sorted_combo = ''.join(sorted(combo))
            letter_combos.add(sorted_combo)
    
    # Query database for all valid words
    if not letter_combos:
        return set()
    
    placeholders = ','.join('?' for _ in letter_combos)
    query = f'SELECT word FROM anagrams WHERE sorted_letters IN ({placeholders})'
    c.execute(query, list(letter_combos))
    
    words = {row[0] for row in c.fetchall()}
    return words

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

# Check if a word placement connects to existing words (required for Bananagrams)
def is_word_connected(grid, word, row, col, direction):
    """Check if a word placement connects to existing words on the grid"""
    size = len(grid)
    
    if direction == 'across':
        # Check if any letter in the word connects to existing letters
        for i, c in enumerate(word):
            r, c_pos = row, col + i
            
            # Check adjacent cells (up, down, left, right)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c_pos + dc
                if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] != '.':
                    return True
            
            # Check if this position already has a letter (crossing)
            if grid[r][c_pos] != '.':
                return True
    else:
        # Check if any letter in the word connects to existing letters
        for i, c in enumerate(word):
            r, c_pos = row + i, col
            
            # Check adjacent cells (up, down, left, right)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c_pos + dc
                if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] != '.':
                    return True
            
            # Check if this position already has a letter (crossing)
            if grid[r][c_pos] != '.':
                return True
    
    return False

# Check if the grid has any isolated words (not connected to the main grid)
def is_grid_connected(grid):
    """Check if all words in the grid are connected to form a single crossword"""
    size = len(grid)
    if size == 0:
        return True
    
    # Find the first letter in the grid
    start_pos = None
    for r in range(size):
        for c in range(size):
            if grid[r][c] != '.':
                start_pos = (r, c)
                break
        if start_pos:
            break
    
    if not start_pos:
        return True  # Empty grid is considered connected
    
    # Use flood fill to mark all connected letters
    visited = set()
    stack = [start_pos]
    
    while stack:
        r, c = stack.pop()
        if (r, c) in visited or grid[r][c] == '.':
            continue
        
        visited.add((r, c))
        
        # Add adjacent letters to the stack
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] != '.':
                stack.append((nr, nc))
    
    # Check if all letters are visited (connected)
    total_letters = sum(1 for r in range(size) for c in range(size) if grid[r][c] != '.')
    return len(visited) == total_letters

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
    # If all letters are used, check if the grid is valid and connected
    if not remaining:
        if is_grid_valid(grid) and is_grid_connected(grid):
            return grid
        return None
    
    # Check if this is the first word (no letters used yet)
    is_first_word = len(used) == 0
    
    # Try to place a word using the remaining letters
    words = get_all_words(remaining)
    # Try longer words first for efficiency
    words = sorted(words, key=lambda w: -len(w))
    for word in words:
        for r in range(size):
            for c in range(size):
                for direction in ['across', 'down']:
                    if can_place_word(grid, word, r, c, direction):
                        # For Bananagrams: first word can be placed anywhere,
                        # subsequent words must connect to existing words
                        if not is_first_word and not is_word_connected(grid, word, r, c, direction):
                            continue
                        
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
    print("Interactive Bananagrams mode. Enter letters (single or multiple). Type 'quit' to exit.")
    print("Solver will timeout after 60 seconds if no solution is found.")
    letters = []
    while True:
        print(f"Current letters: {''.join(letters)}")
        inp = input("Enter letter(s) (or 'quit' to finish): ").strip().upper()
        if inp == 'QUIT':
            print("Exiting interactive mode.")
            break
        if not inp.isalpha():
            print("Please enter alphabetic letters only.")
            continue
        
        # Add all letters from the input
        new_letters = list(inp)
        letters.extend(new_letters)
        print(f"Added letters: {', '.join(new_letters)}")
        
        n = len(letters)
        import math
        min_size = int(math.ceil(n ** 0.5))
        # Try from maximum size down to minimum for better success rate
        sizes = list(range(n, min_size - 1, -1))
        found = False
        try:
            import time
            start_time = time.time()
            timeout_seconds = 60  # 60 second timeout
            
            with multiprocessing.Pool() as pool:
                # Submit all sizes for parallel processing
                futures = {pool.apply_async(solve_for_size, [(letters, s)]): s for s in sizes}
                
                # Check for completion with timeout
                for future in futures:
                    try:
                        # Wait for result with timeout
                        remaining_time = max(0, timeout_seconds - (time.time() - start_time))
                        if remaining_time <= 0:
                            print(f"\nSolver timed out after {timeout_seconds} seconds.")
                            print("Try adding a different letter or fewer letters.")
                            break
                        
                        size, grid = future.get(timeout=remaining_time)
                        if grid:
                            elapsed = time.time() - start_time
                            print(f"Solution found in {elapsed:.2f} seconds:")
                            print("Possible grid:")
                            print_grid(grid)
                            found = True
                            break
                    except multiprocessing.TimeoutError:
                        print(f"\nSolver timed out after {timeout_seconds} seconds.")
                        print("Try adding a different letter or fewer letters.")
                        break
                    except Exception as e:
                        print(f"Error during solving: {e}")
                        continue
            
            if not found:
                elapsed = time.time() - start_time
                if elapsed >= timeout_seconds:
                    print(f"No solution found within {timeout_seconds} seconds.")
                    print("Try adding a different letter or fewer letters.")
                else:
                    print("No valid Bananagram could be formed with the given letters.")
                    
        except KeyboardInterrupt:
            # Allow user to interrupt a long solve and continue
            print("\nSolve interrupted. You can enter another letter or 'quit' to exit.")
            continue

# Main entry point: choose batch or interactive mode, both using multicore solving
def main():
    try:
        if len(sys.argv) == 2:
            # Batch mode: all letters at once, use multicore
            letters = sys.argv[1].upper()
            n = len(letters)
            import math
            min_size = int(math.ceil(n ** 0.5))
            # Try from maximum size down to minimum for better success rate
            sizes = list(range(n, min_size - 1, -1))
            found = False
            
            import time
            start_time = time.time()
            
            with multiprocessing.Pool() as pool:
                for size, grid in pool.imap_unordered(solve_for_size, [(letters, s) for s in sizes]):
                    if grid:
                        elapsed = time.time() - start_time
                        print(f"Solution found in {elapsed:.2f} seconds:")
                        print_grid(grid)
                        found = True
                        break
            
            if not found:
                elapsed = time.time() - start_time
                print(f"No valid Bananagram could be formed with the given letters.")
                print(f"Search completed in {elapsed:.2f} seconds.")
        else:
            # Interactive mode
            interactive_mode()
    finally:
        # Always close the database connection
        close_db_connection()

if __name__ == "__main__":
    main() 