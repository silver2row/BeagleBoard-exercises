#!/usr/bin/env python3
# This is for the web server that displays the temperature and humidity

# It's using a web server to display the data

# pip install flask requests

from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
import os
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")  # <-- Set your API key in the environment variable
if not OPENWEATHER_API_KEY:
    raise RuntimeError("Missing OPENWEATHER_API_KEY environment variable. Please set it before running the application.")
LOCATION = "Brazil, Indiana"  # <-- Replace with your city

@app.route("/api/forecast")
def forecast():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=imperial"
    r = requests.get(url)
    data = r.json()
    forecast_data = []
    for entry in data.get("list", [])[:16]:  # 16 x 3 hours = 48 hours
        forecast_data.append({
            "timestamp": entry["dt_txt"],
            "temperature": entry["main"]["temp"],
            "humidity": entry["main"]["humidity"]
        })
    return jsonify(forecast_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 