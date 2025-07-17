#!/usr/bin/env python3

import sqlite3
from tabulate import tabulate
from datetime import datetime

DB_PATH = "tmp101_data.db"

def show_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, temp1, temp2 FROM readings ORDER BY timestamp")
    rows = c.fetchall()
    conn.close()
    # Format timestamp to nearest second
    formatted_rows = []
    for row in rows:
        ts = row[0]
        try:
            ts = datetime.fromisoformat(ts).replace(microsecond=0).isoformat(sep=' ')
        except Exception:
            pass  # If parsing fails, use as is
        formatted_rows.append((ts, row[1], row[2]))
    if formatted_rows:
        print(tabulate(formatted_rows, headers=["Timestamp", "Temp1 (F)", "Temp2 (F)"], tablefmt="github"))
    else:
        print("No data found.")

if __name__ == "__main__":
    show_data() 