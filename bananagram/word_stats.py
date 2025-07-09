#!/usr/bin/env python3
import sqlite3
from collections import Counter
import matplotlib.pyplot as plt

DB_FILE = 'words.db'

def get_database_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get total word count
    c.execute('SELECT COUNT(*) FROM anagrams')
    total_words = c.fetchone()[0]
    
    # Get word length distribution
    c.execute('SELECT LENGTH(word) as word_length, COUNT(*) as count FROM anagrams GROUP BY LENGTH(word) ORDER BY word_length')
    length_dist = dict(c.fetchall())
    
    # Get average word length
    c.execute('SELECT AVG(LENGTH(word)) FROM anagrams')
    avg_length = c.fetchone()[0]
    
    # Get sorted_letters frequency (most common anagram groups)
    c.execute('SELECT sorted_letters, COUNT(*) as count FROM anagrams GROUP BY sorted_letters ORDER BY count DESC LIMIT 10')
    common_anagrams = c.fetchall()
    
    # Get words by length
    c.execute('SELECT word FROM anagrams ORDER BY LENGTH(word) DESC LIMIT 10')
    longest_words = [row[0] for row in c.fetchall()]
    
    # Get letter frequency
    c.execute('SELECT word FROM anagrams')
    all_words = [row[0] for row in c.fetchall()]
    letter_freq = Counter()
    for word in all_words:
        letter_freq.update(word)
    
    conn.close()
    
    return {
        'total_words': total_words,
        'length_distribution': length_dist,
        'average_length': avg_length,
        'common_anagrams': common_anagrams,
        'longest_words': longest_words,
        'letter_frequency': letter_freq
    }

def print_stats(stats):
    print("=== WORD DATABASE STATISTICS ===\n")
    
    print(f"Total words: {stats['total_words']:,}")
    print(f"Average word length: {stats['average_length']:.2f} letters")
    
    print(f"\nLongest words:")
    for i, word in enumerate(stats['longest_words'], 1):
        print(f"  {i}. {word} ({len(word)} letters)")
    
    print(f"\nMost common anagram groups:")
    for sorted_letters, count in stats['common_anagrams']:
        print(f"  {sorted_letters}: {count} words")
    
    print(f"\nWord length distribution:")
    for length in sorted(stats['length_distribution'].keys()):
        count = stats['length_distribution'][length]
        percentage = (count / stats['total_words']) * 100
        print(f"  {length} letters: {count:,} words ({percentage:.1f}%)")
    
    print(f"\nLetter frequency (top 10):")
    for letter, count in stats['letter_frequency'].most_common(10):
        percentage = (count / sum(stats['letter_frequency'].values())) * 100
        print(f"  {letter}: {count:,} occurrences ({percentage:.1f}%)")

def plot_stats(stats):
    """Create visualizations of the statistics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Word length distribution
    lengths = sorted(stats['length_distribution'].keys())
    counts = [stats['length_distribution'][l] for l in lengths]
    ax1.bar(lengths, counts)
    ax1.set_title('Word Length Distribution')
    ax1.set_xlabel('Word Length')
    ax1.set_ylabel('Number of Words')
    
    # Letter frequency
    letters, freqs = zip(*stats['letter_frequency'].most_common(10))
    ax2.bar(letters, freqs)
    ax2.set_title('Letter Frequency (Top 10)')
    ax2.set_xlabel('Letter')
    ax2.set_ylabel('Frequency')
    
    # Anagram group sizes
    anagram_groups, group_counts = zip(*stats['common_anagrams'])
    ax3.bar(range(len(anagram_groups)), group_counts)
    ax3.set_title('Most Common Anagram Groups')
    ax3.set_xlabel('Anagram Group')
    ax3.set_ylabel('Number of Words')
    ax3.set_xticks(range(len(anagram_groups)))
    ax3.set_xticklabels(anagram_groups, rotation=45)
    
    # Cumulative word count by length
    cumulative = []
    total = 0
    for length in sorted(stats['length_distribution'].keys()):
        total += stats['length_distribution'][length]
        cumulative.append(total)
    
    ax4.plot(sorted(stats['length_distribution'].keys()), cumulative)
    ax4.set_title('Cumulative Word Count by Length')
    ax4.set_xlabel('Word Length')
    ax4.set_ylabel('Cumulative Word Count')
    
    plt.tight_layout()
    plt.savefig('word_stats.png')
    print("\nStatistics plot saved as 'word_stats.png'")

def main():
    print("Analyzing word database...")
    stats = get_database_stats()
    print_stats(stats)
    
    try:
        plot_stats(stats)
    except ImportError:
        print("\nMatplotlib not available. Skipping plot generation.")

if __name__ == "__main__":
    main() 