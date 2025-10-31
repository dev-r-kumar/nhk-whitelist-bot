from flask import Flask, request, jsonify
import os, time, json
from threading import Thread

app = Flask(__name__)

whitelist_db_path = os.path.join(os.path.dirname(__file__), "whitelist.json")


@app.route("/api/uid/check")
def check_uid():
    uid = request.args.get("uid")
    
    if not uid:
        return jsonify({"status": "error", "message": "uid is required"}), 400
    
    try:
        uid = int(uid)
    except ValueError:
        return jsonify({"status": "error", "message": "uid must be a number"}), 400

    # Load whitelist database
    try:
        with open(whitelist_db_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({"status": "error", "message": f"failed to load database: {str(e)}"}), 500

    current_time = int(time.time())
    
    # Check if UID exists in database
    for entry in data:
        if entry.get("uid") == uid:
            expiry = entry.get("expiry", 0)
            if expiry > current_time:
                return jsonify({"status": "success", "message": "UID is whitelisted", "uid": uid, "expiry": expiry})
            else:
                return jsonify({"status": "error", "message": "UID whitelist expired", "uid": uid, "expiry": expiry})
    
    # UID not found
    return jsonify({"status": "error", "message": "UID is not whitelisted"}), 404


def run():
    app.run(host="0.0.0.0", port=8080)




def keep_alive():
    Thread(target=run).start()

    