from api import fujisan
import json
from flask import Flask, jsonify, render_template, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def main(request):
    sta = request.args.get('sta', default=None, type=str)
    if not sta:
        return 'test'
    response = jsonify(fujisan(sta))
    response.headers.add('Access-Control-Allow-Origin', 'https://psyaro.github.io')
    return response