#!/usr/bin/env python3

import sqlite3
from tabulate import tabulate

DB_PATH = "tmp101_data.db"

def show_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, temp1, temp2 FROM readings ORDER BY timestamp")
    rows = c.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["Timestamp", "Temp1 (F)", "Temp2 (F)"], tablefmt="github"))
    else:
        print("No data found.")

if __name__ == "__main__":
    show_data() 