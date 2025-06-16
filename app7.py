from flask import Flask, jsonify, render_template, request
import requests
import threading
import time

app = Flask(__name__)
speed_logs = []
log_lock = threading.Lock()

def perform_speed_test():
    log_entry = {}
    try:
        # Download test
        download_start = time.time()
        res = requests.get("https://librespeed.org/files/10MB.bin", stream=True, timeout=30)
        size_bytes = 0
        for chunk in res.iter_content(chunk_size=1024 * 1024):
            size_bytes += len(chunk)
        download_end = time.time()
        download_time = download_end - download_start
        download_mbps = (size_bytes * 8) / (download_time * 1_000_000)

        # Upload test
        upload_start = time.time()
        payload = b"x" * (5 * 1024 * 1024)
        upload_res = requests.post(
            "https://librespeed.org/backend.php",
            files={"file": ("dummy.dat", payload)},
            timeout=30
        )
        upload_end = time.time()
        upload_time = upload_end - upload_start
        upload_mbps = (len(payload) * 8) / (upload_time * 1_000_000)

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "download_mbps": round(download_mbps, 2),
            "upload_mbps": round(upload_mbps, 2)
        }

    except Exception as e:
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

    with log_lock:
        speed_logs.append(log_entry)

def schedule_speed_tests():
    while True:
        perform_speed_test()
        print("✅ Speed test run. Logs so far:", speed_logs)
        time.sleep(10)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def get_logs():
    with log_lock:
        return jsonify(speed_logs)

@app.route("/clear", methods=["POST"])
def clear_logs():
    with log_lock:
        speed_logs.clear()
    return ("", 204)

if __name__ == "__main__":
    threading.Thread(target=schedule_speed_tests, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
