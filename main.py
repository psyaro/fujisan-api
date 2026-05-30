import os

# dotenvの読み込み (ローカル環境にライブラリが無くても動作するようフォールバック処理)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from api import fujisan, get_stations_list
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_frontend_html():
    x = os.path.dirname(__file__)
    filepath = os.path.join(x, 'docs', 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def process_request(sta):
    if not sta:
        return 'test'
    response = jsonify(fujisan(staname=sta))
    response.headers.add('Access-Control-Allow-Origin', 'https://psyaro.github.io')
    return response

# === ローカルWebサーバー用ルート ===

# 1. フロントエンドホスト
@app.route("/", methods=["GET"])
def index():
    return get_frontend_html()

# 2. 富士山判定 API
@app.route("/api", methods=["GET"])
@app.route("/api/", methods=["GET"])
def api():
    sta = request.args.get('sta', default='追浜', type=str)
    return process_request(sta)

# 3. 駅名リスト API
@app.route("/api/stations", methods=["GET"])
@app.route("/api/stations/", methods=["GET"])
def api_stations():
    response = jsonify(get_stations_list())
    response.headers.add('Access-Control-Allow-Origin', 'https://psyaro.github.io')
    return response

# === Google Cloud Functions エントリーポイント ===
def main(request):
    path = request.path
    if path == "/api/stations" or path == "/api/stations/":
        response = jsonify(get_stations_list())
        response.headers.add('Access-Control-Allow-Origin', 'https://psyaro.github.io')
        return response
    elif path == "/api" or path == "/api/":
        sta = request.args.get('sta', default='追浜', type=str)
        return process_request(sta)
    else:
        # パスがそれ以外（ルート / など）ならフロントHTMLを返す
        return get_frontend_html()

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    
    app.run(debug=debug, host=host, port=port)