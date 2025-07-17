#! /usr/bin/env python3

import os
import sqlite3
from datetime import datetime

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

db_path = "tmp101_data.db"
# Paths for the two TMP101 sensors
sensor_paths = [
    "/sys/class/hwmon/hwmon0/temp1_input",
    "/sys/class/hwmon/hwmon1/temp1_input"
]

def read_temp(sensor_path):
    try:
        with open(sensor_path) as f:
            # TMP101 reports temp in millidegrees Celsius
            temp_c = float(f.read().strip()) / 1000.0
        return temp_c
    except Exception as e:
        print(f"Error reading {sensor_path}: {e}")
        return None

def log_data():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (timestamp TEXT, temp1 REAL, temp2 REAL)''')
    temp1 = read_temp(sensor_paths[0])
    temp2 = read_temp(sensor_paths[1])
    if temp1 is not None and temp2 is not None:
        temp1_f = c_to_f(temp1)
        temp2_f = c_to_f(temp2)
        c.execute("INSERT INTO readings VALUES (?, ?, ?)", (datetime.now().isoformat(), temp1_f, temp2_f))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    log_data() 