from flask import Flask, jsonify, render_template
import speedtest
import traceback

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speedtest")
def run_speed_test():
    log = []
    try:
        log.append("📡 Initializing speedtest...")
        st = speedtest.Speedtest()

        log.append("🌐 Finding best server...")
        best = st.get_best_server()
        log.append(f"✅ Best server: {best['host']} ({best['name']}, {best['country']})")

        log.append("📥 Measuring download speed...")
        download = st.download() / 1_000_000  # Mbps
        log.append(f"📥 Download: {round(download, 2)} Mbps")

        log.append("📤 Measuring upload speed...")
        upload = st.upload() / 1_000_000
        log.append(f"📤 Upload: {round(upload, 2)} Mbps")

        result = {
            "download_mbps": round(download, 2),
            "upload_mbps": round(upload, 2),
            "log": log
        }

        print("Speedtest completed:", result)  # Log to server console
        return jsonify(result)

    except Exception as e:
        error_trace = traceback.format_exc()
        log.append("❌ Error occurred:")
        log.append(str(e))
        log.append(error_trace)
        print("Speedtest failed:", error_trace)  # Log to server console
        return jsonify({"error": str(e), "log": log}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
