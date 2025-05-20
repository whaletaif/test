from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.databases import Databases 

client = Client()
client.set_endpoint('https://fra.cloud.appwrite.io/v1')
client.set_project('682c6eb5000182ea405a')
client.set_key('standard_b92cdf5a2cf7b3a22b3c08b75a127ffc213e8f606538fbc2c5fd8d6050ddc7475e692b32658ba890e353ae3fd9ab5e2e2c640ef3b2697632ff31980ff7c37e1d26faba98a82daff440b70ba289525025a1604f05bc602dfdbfad4d9c2ea1137d4a05e22aaa70a86a3804ae77761888b0fbf6730e9d6609ea2f12cfebc09ba500')

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from maps import maps_scraper
from flask_socketio import SocketIO, emit
import os
from urllib.parse import quote

#app
app = Flask(__name__)
socketio = SocketIO(app)
os.makedirs('outputs', exist_ok=True)

# API Token
API_TOKEN = "token123"

# Validate API token
def validate_token(request):
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized"}), 401

# Homepage
@app.route('/')
def index():
    return render_template('mainpage.html')

# Maps scraper page
@app.route("/scraper-maps")
def scraper():
    return render_template("scraper-maps.html")

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/settings')
def setting():
    return render_template('setting.html')

@app.route('/scraper-maps', methods=['POST'])
# Scraper function
def scrape_maps():
    # Get input data
    keyword = request.form['keyword'].strip()
    location = request.form['location'].strip()
    limit = request.form['limit'].strip()
    proxy = request.form.get('proxy', '').strip()

    # Convert limit to integer, or None if blank
    try:
        limit = int(limit)
    except ValueError:
        limit = None

    try:
        # Call scraper
        output_path = maps_scraper(keyword, location, limit, log_callback=log_message, proxy=proxy)
        json_file = os.path.basename(output_path["json"])
        return jsonify({"success": True, "json_file": json_file})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
# Logging function
def log_message(message):
    print(f"Log emitted: {message}")
    socketio.emit('log', {'message': message})

# Result for maps scraper
@app.route('/result-maps')
def result_maps():
    file = request.args.get('file')
    if not file:
        return "File parameter is missing", 400

    # Check if the file exists
    file_path = os.path.join('outputs', file)
    if not os.path.exists(file_path):
        return "File not found", 404

    return render_template('result-maps.html', file=file)

# For downloading files
@app.route('/outputs/<path:filename>')
def serve_output_file(filename):
    return send_from_directory('outputs', filename)

# API endpoint for maps scraper
# curl -X POST http://127.0.0.1:5000/api/scraper-maps ^
# -H "Authorization: Bearer token123" ^
# -H "Content-Type: application/json" ^
# -d "{\"keyword\": \"a\", \"location\": \"b\", \"limit\": \"c\", \"proxy\": \"d\"}" # customise letters
@app.route('/api/scraper-maps', methods=['POST'])
def api_scrape_maps():
    # Validate the token
    auth_response = validate_token(request)
    if auth_response:
        return auth_response

    # Get input data
    data = request.json
    keyword = data.get('keyword', '').strip()
    location = data.get('location', '').strip()
    limit = data.get('limit', '').strip()
    proxy = data.get('proxy', '').strip()

    # Convert limit to integer, or None if blank
    try:
        limit = int(limit) if limit else None
    except ValueError:
        return jsonify({"success": False, "error": "Limit must be a number"}), 400

    try:
        # Call scraper
        output_path = maps_scraper(keyword, location, limit, log_callback=log_message, proxy=proxy)
        filename_json = os.path.basename(output_path["json"])
        filename_excel = os.path.basename(output_path["excel"])
        encoded_filename_json = quote(filename_json)
        encoded_filename_excel = quote(filename_excel)
        return jsonify({"success": True, "json_file": encoded_filename_json, "excel_file": encoded_filename_excel})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Download file from API
# curl -X GET "http://127.0.0.1:5000/api/download?filename=filename.xlsx" ^
# -H "Authorization: Bearer token123" ^
# -o "any_file_name.xlsx"
@app.route('/api/download', methods=['GET'])
def api_download_file():
    # Validate the token
    auth_response = validate_token(request)
    if auth_response:
        return auth_response

    # Get the filename from the query parameters
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"success": False, "error": "Filename is required"}), 400

    # Construct the file path
    file_path = os.path.join('outputs', filename)
    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": "File not found"}), 404

    # Send the file to the client
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)