from flask import Flask, jsonify
import speedtest

app = Flask(__name__)

@app.route("/speedtest", methods=["GET"])
def run_speed_test():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()

        download = st.download() / 1_000_000  # Convert to Mbps
        upload = st.upload() / 1_000_000

        return jsonify({
            "download_mbps": round(download, 2),
            "upload_mbps": round(upload, 2),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return "Speedtest service is up!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
