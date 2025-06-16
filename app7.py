from flask import Flask, jsonify, render_template, request
import threading
import time
import requests
import os

app = Flask(__name__)
speed_logs = []
log_lock = threading.Lock()

DOWNLOAD_URL = "https://speed.hetzner.de/10MB.bin"
UPLOAD_URL = "https://httpbin.org/post"  # public echo server for testing uploads

def download_speed_test():
    start = time.time()
    try:
        r = requests.get(DOWNLOAD_URL, stream=True, timeout=30)
        total_bytes = 0
        for chunk in r.iter_content(chunk_size=1024*1024):
            total_bytes += len(chunk)
        duration = time.time() - start
        mbps = (total_bytes * 8) / (duration * 1_000_000)  # Megabits per second
        return round(mbps, 2), duration
    except Exception as e:
        return None, str(e)

def upload_speed_test():
    # Generate 5 MB of random bytes
    data = os.urandom(5 * 1024 * 1024)
    start = time.time()
    try:
        r = requests.post(UPLOAD_URL, data=data, timeout=30)
        duration = time.time() - start
        mbps = (len(data) * 8) / (duration * 1_000_000)  # Megabits per second
        return round(mbps, 2), duration
    except Exception as e:
        return None, str(e)

def perform_speed_test():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    dl_speed, dl_info = download_speed_test()
    ul_speed, ul_info = upload_speed_test()

    entry = {"timestamp": timestamp}
    if dl_speed is not None:
        entry["download_mbps"] = dl_speed
        entry["download_duration_s"] = round(dl_info, 2)
    else:
        entry["download_error"] = dl_info

    if ul_speed is not None:
        entry["upload_mbps"] = ul_speed
        entry["upload_duration_s"] = round(ul_info, 2)
    else:
        entry["upload_error"] = ul_info

    with log_lock:
        speed_logs.append(entry)
    print(f"Logged speed test: {entry}")

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
    threading.Thread(target=schedule_speed_tests, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
