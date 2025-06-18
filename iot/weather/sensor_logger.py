#!/usr/bin/env python3
# This is for logging the temperature and humidity to a database
# It's using the iio interface to read the temperature and humidity
# It's using a si7021 sensor
# It's using a sqlite database
# It's using a cron job to run every minute
# It's using a web server to display the data

import time
import sqlite3
from datetime import datetime
import os

DB = "sensor_data.db"
IIO_PATH = "/sys/class/i2c-adapter/i2c-1/1-0040/iio:device1/"

def read_sensor():
    try:
        with open(os.path.join(IIO_PATH, "in_temp_raw")) as f:
            temp_raw = float(f.read().strip())
        with open(os.path.join(IIO_PATH, "in_temp_scale")) as f:
            temp_scale = float(f.read().strip())
        with open(os.path.join(IIO_PATH, "in_temp_offset")) as f:
            temp_offset = float(f.read().strip())
        temp = ((temp_raw * temp_scale) + temp_offset) / 1000
        with open(os.path.join(IIO_PATH, "in_humidityrelative_raw")) as f:
            humid_raw = float(f.read().strip())
        with open(os.path.join(IIO_PATH, "in_humidityrelative_scale")) as f:
            humid_scale = float(f.read().strip())
        with open(os.path.join(IIO_PATH, "in_humidityrelative_offset")) as f:
            humid_offset = float(f.read().strip())
        humid = ((humid_raw + humid_offset) * humid_scale) / 1000
        return temp, humid
    except Exception as e:
        print(f"Sensor read error: {e}")
        return None, None

def log_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (timestamp TEXT, temperature REAL, humidity REAL)''')
    temp, humid = read_sensor()
    if temp is not None and humid is not None:
        c.execute("INSERT INTO readings VALUES (?, ?, ?)", (datetime.now().isoformat(), temp, humid))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    log_data() 