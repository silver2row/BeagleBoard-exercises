#!/usr/bin/env python3

from flask import Flask, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "tmp101_data.db"

@app.route("/api/tmp101")
def get_temps():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, temp1, temp2 FROM readings ORDER BY timestamp")
    rows = c.fetchall()
    conn.close()
    data = [
        {"timestamp": row[0], "temp1": row[1], "temp2": row[2]}
        for row in rows
    ]
    return jsonify(data)

@app.route('/')
def serve_plot():
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static'),
        'tmp101_plot.html'
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0') 