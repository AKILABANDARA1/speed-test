from flask import Flask, jsonify, render_template, request
import subprocess
import threading
import time
import json

app = Flask(__name__)

speed_logs = []
log_lock = threading.Lock()

def perform_speed_test():
    try:
        print("⚡ Running speed test")
        output = subprocess.check_output(["librespeed-cli", "--json"], timeout=60)
        data = json.loads(output)
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "download_mbps": round(data["download"] / 1_000_000, 2),
            "upload_mbps": round(data["upload"] / 1_000_000, 2),
            "ping_ms": data.get("ping")
        }
        print(f"✅ Speed test result: {entry}")
    except Exception as e:
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }
        print(f"❌ Speed test failed: {entry['error']}")
    with log_lock:
        speed_logs.append(entry)

def schedule_speed_tests():
    while True:
        perform_speed_test()
        time.sleep(10)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def logs():
    with log_lock:
        return jsonify(speed_logs)

@app.route("/clear", methods=["POST"])
def clear():
    with log_lock:
        speed_logs.clear()
    return ("", 204)

if __name__ == "__main__":
    print("🚀 Starting background speed test thread")
    threading.Thread(target=schedule_speed_tests, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
