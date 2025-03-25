import socket
import threading
import requests
import json
from flask import Flask, request

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = "<YOUR-BOT-TOKEN>"
TELEGRAM_CHAT_ID = "<YOUR CHAT ID>"

app = Flask(__name__)

# Logging file
LOG_FILE = "honeybot_logs.txt"

# Function to send Telegram alerts
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

# Function to log and alert attacker data
def log_attacker(ip, data):
    log_message = f"ALERT: Possible Attack Detected!\nIP: {ip}\nDATA: {data}"
    
    with open(LOG_FILE, "a") as log:
        log.write(log_message + "\n")

    send_telegram_alert(log_message)

# Function to get geolocation
def get_geo_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        geo_data = response.json()
        if geo_data["status"] == "success":
            return f"Country: {geo_data['country']}, City: {geo_data['city']}, ISP: {geo_data['isp']}, Lat: {geo_data['lat']}, Lon: {geo_data['lon']}"
        return "Geolocation Failed"
    except Exception as e:
        return f"Error: {str(e)}"

# Fake vulnerable web endpoint
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    attacker_ip = request.remote_addr
    geo_info = get_geo_info(attacker_ip)

    log_attacker(attacker_ip, f"Geo Info: {geo_info}")

    return "Unauthorized Access", 403

# Fake vulnerable TCP service
def tcp_honeypot(port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"HoneyBot listening on port {port}...")

    while True:
        client, addr = server.accept()
        ip = addr[0]
        log_attacker(ip, "TCP Connection Attempt")

        geo_info = get_geo_info(ip)
        print(f"Attacker IP: {ip} | {geo_info}")

        client.send(b"Unauthorized access detected. Activity logged.\n")
        client.close()

# Start the HoneyBot
if __name__ == "__main__":
    threading.Thread(target=tcp_honeypot, args=(8080,), daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
