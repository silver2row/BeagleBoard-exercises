#!/usr/bin/env python3

from flask import Flask, jsonify
import sqlite3

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

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0') 