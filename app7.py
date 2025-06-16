from flask import Flask, jsonify, render_template
import requests
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speedtest")
def run_speed_test():
    log = []
    try:
        log.append("🚀 Starting LibreSpeed test...")

        # Download test (dummy data)
        start = time.time()
        res = requests.get("https://librespeed.org/files/10MB.bin", stream=True, timeout=20)
        size_bytes = 0
        for chunk in res.iter_content(chunk_size=1024*1024):
            size_bytes += len(chunk)
        download_time = time.time() - start
        download_mbps = (size_bytes * 8) / (download_time * 1_000_000)
        log.append(f"📥 Download: {round(download_mbps, 2)} Mbps")

        # Upload test — simulate 5MB upload
        start = time.time()
        payload = b"x" * (5 * 1024 * 1024)  # 5MB
        upload_res = requests.post(
            "https://librespeed.org/backend.php",
            files={"file": ("dummy.dat", payload)},
            timeout=20
        )
        upload_time = time.time() - start
        upload_mbps = (len(payload) * 8) / (upload_time * 1_000_000)
        log.append(f"📤 Upload: {round(upload_mbps, 2)} Mbps")

        return jsonify({
            "download_mbps": round(download_mbps, 2),
            "upload_mbps": round(upload_mbps, 2),
            "log": log
        })

    except Exception as e:
        log.append(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e), "log": log}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
