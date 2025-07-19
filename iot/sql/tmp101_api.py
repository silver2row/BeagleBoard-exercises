#!/usr/bin/env python3

# This script provides a simple Flask web API for accessing TMP101 temperature readings.
# It also serves a static HTML file for plotting or displaying the data.

from flask import Flask, jsonify, send_from_directory, request, abort
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "tmp101_data.db"

# Restrict access to only allow requests from the 10.0.5.* subnet
HOME_SUBNET = "10.0.5."

@app.before_request
def limit_remote_addr():
    if not request.remote_addr.startswith(HOME_SUBNET):
        abort(403)  # Forbidden

@app.route("/api/tmp101")
def get_temps():
    """API endpoint: Return all temperature readings as a JSON array."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, temp1, temp2 FROM readings ORDER BY timestamp")
    rows = c.fetchall()
    conn.close()
    # Convert each row to a dictionary for JSON output
    data = [
        {"timestamp": row[0], "temp1": row[1], "temp2": row[2]}
        for row in rows
    ]
    return jsonify(data)

@app.route('/')
def serve_plot():
    """Serve the static HTML file for plotting or displaying temperature data."""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static'),
        'tmp101_plot.html'
    )

if __name__ == "__main__":
    # Listen on all interfaces, but only allow requests from 10.0.5.*
    app.run(debug=True, port=5001, host='0.0.0.0') 