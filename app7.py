from flask import Flask, jsonify, render_template
import subprocess, threading, json, time

app = Flask(__name__)
speed_logs, log_lock = [], threading.Lock()

def perform_speed_test():
    try:
        cmd = ["librespeed-cli", "--json"]
        output = subprocess.check_output(cmd, timeout=60)
        data = json.loads(output)
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "download_mbps": round(data["download"]/1e6, 2),
            "upload_mbps": round(data["upload"]/1e6, 2),
            "ping_ms": data.get("ping", None)
        }
    except Exception as e:
        entry = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "error": str(e)}
    with log_lock:
        speed_logs.append(entry)

def schedule_speed_tests():
    while True:
        perform_speed_test()
        time.sleep(10)

@app.route("/")
def index(): return render_template("index.html")

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
