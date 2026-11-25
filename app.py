from flask import Flask, jsonify, send_from_directory
import time

import collector

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/metrics")
def metrics():
    return jsonify({
        "timestamp": int(time.time()),
        "system": collector.get_system(),
        "cpu": collector.get_cpu(),
        "memory": collector.get_memory(),
        "disk": collector.get_disk(),
        "network": collector.get_network(),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
