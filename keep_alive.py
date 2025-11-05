from flask import Flask, request, jsonify
import os, time, json
from threading import Thread
import aiohttp
import asyncio
import ssl
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # new avoid block cors

whitelist_db_path = os.path.join(os.path.dirname(__file__), "whitelist.json")


class DCPlugin:
    def __init__(self, url, title, message):
        self.url = url
        self.title = title
        self.messgae = message
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en",
            "Content-Type": "application/json",
            "Origin": "https://discord.org",
            "Referer": "https://discohook.org/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

    async def send(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": self.title,
                    "description": self.messgae,
                    "color": 16711680
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, headers=self.headers, json=payload, ssl=ssl_context) as response:
                return "message sent !" if response.status in (200, 204) else "error, failed to send message !"


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
                diff = expiry - int(time.time())
                days = diff // 86400
                hours = (diff % 86400) // 3600
                minutes = (diff % 3600) // 60
                seconds = diff % 60
                time_left = f'{days}:{hours}:{minutes}:{seconds}'
                return jsonify({"status": "success", "message": "UID is whitelisted", "uid": uid, "time_left": time_left})
            else:
                return jsonify({"status": "error", "message": "UID whitelist expired", "uid": uid, "expiry": expiry})
    
    # UID not found
    return jsonify({"status": "error", "message": "UID is not whitelisted"}), 404




@app.route("/api/uidbypass/extendlicense")
def extend_license():
    uid = request.args.get("uid")
    extend_type = request.args.get("type")

    if not uid:
        return jsonify({"status": "error", "message": "uid is required !"}), 400
    
    uid = int(uid)

    with open("whitelist.json", "r") as f:
        data = json.load(f)

    for entry in data:
        if entry["uid"] == uid:
            expiry = entry["expiry"]
            if extend_type == "week":
                extend = int(time.time()) + 7 * 24 * 60 * 60

                dcplugin = DCPlugin(
                    url="https://discord.com/api/webhooks/1433940108012163235/hGe2v3muvbxNFAIGpiLjrNO9bLiGqK6l56KM4qETI1hfEASm2ov9whRcnpy_bJrlmo5N",
                    title="UID Subscription",
                    message=f"**Thank you for purchasing uid bypass weekly subscription. Your subscription is now active.**\nUID: **{uid}**"
                )
                asyncio.run(dcplugin.send())

                return jsonify({"status": "success", "message": "subscription added successfully.."}), 200

            elif extend_type == "month":
                extend = int(time.time()) + 30 * 24 * 60 * 60

                dcplugin = DCPlugin(
                    url="https://discord.com/api/webhooks/1433940108012163235/hGe2v3muvbxNFAIGpiLjrNO9bLiGqK6l56KM4qETI1hfEASm2ov9whRcnpy_bJrlmo5N",
                    title="UID Subscription",
                    message=f"**Thank you for purchasing uid bypass monthly subscription. Your subscription is now active.**\nUID: **{uid}**"
                )

                asyncio.run(dcplugin.send())

                return jsonify({"status": "success", "message": "subscription added successfully.."}), 200
            
            entry["expiry"] = extend

    dcplugin = DCPlugin(
        url="https://discord.com/api/webhooks/1433940108012163235/hGe2v3muvbxNFAIGpiLjrNO9bLiGqK6l56KM4qETI1hfEASm2ov9whRcnpy_bJrlmo5N",
        title="Admin Portal",
        message=f"Dear admin seems like uid *{uid}* is not added to our record. Please whitelist the uid first to add subscription.\n\nUID: **{uid}**"
    )
    
    asyncio.run(dcplugin.send())

    with open("whitelist.json", "w") as f:
        json.dump(data, f, indent=2)


    return jsonify({"status": "error", "message": "uid not whitelisted"}), 200
    

def run():
    app.run(host="0.0.0.0", port=8080)




def keep_alive():
    Thread(target=run).start()

    