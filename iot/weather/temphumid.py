#!/usr/bin/env python3
# This is for the web server that displays the temperature and humidity
# It's using a sqlite database to store the data
# It's using a cron job to run every minute
# It's using a web server to display the data

# pip install flask requests

from flask import Flask, jsonify
import sqlite3
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
DB = "sensor_data.db"
import os
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")  # <-- Set your API key in the environment variable
if not OPENWEATHER_API_KEY:
    raise RuntimeError("Missing OPENWEATHER_API_KEY environment variable. Please set it before running the application.")
LOCATION = "Brazil, Indiana"  # <-- Replace with your city

@app.route("/api/history")
def history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    since = (datetime.now() - timedelta(hours=24)).isoformat()
    c.execute("SELECT timestamp, temperature, humidity FROM readings WHERE timestamp > ?", (since,))
    data = [{"timestamp": row[0], "temperature": row[1], "humidity": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route("/api/forecast")
def forecast():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=metric"
    r = requests.get(url)
    data = r.json()
    # Extract next 24 hours (8*3=24, as data is every 3 hours)
    forecast_data = []
    for entry in data.get("list", [])[:8]:
        temp_c = entry["main"]["temp"]
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        forecast_data.append({
            "timestamp": entry["dt_txt"],
            "temperature": temp_f,
            "humidity": entry["main"]["humidity"]
        })
    return jsonify(forecast_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 