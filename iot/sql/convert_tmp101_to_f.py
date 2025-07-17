#! /usr/bin/env python3

import sqlite3

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

DB_PATH = "tmp101_data.db"

def convert_all_to_f():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT rowid, temp1, temp2 FROM readings")
    rows = c.fetchall()
    updated = 0
    for rowid, temp1, temp2 in rows:
        # Only convert if values are in Celsius (e.g., below 60C)
        if temp1 < 60 and temp2 < 60:
            f1 = c_to_f(temp1)
            f2 = c_to_f(temp2)
            c.execute("UPDATE readings SET temp1=?, temp2=? WHERE rowid=?", (f1, f2, rowid))
            updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} records to Fahrenheit.")

if __name__ == "__main__":
    convert_all_to_f() 