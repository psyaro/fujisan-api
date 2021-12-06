from api import fujisan
import json
from flask import Flask, jsonify, render_template, redirect

app = Flask(__name__)

@app.route("/", methods=["GET"])
def main(request):
    sta = request.args.get('sta', default=None, type=str)
    if not sta:
        return 'test'
    response = jsonify(fujisan(sta))
    response.headers.add('Access-Control-Allow-Origin', 'https://psyaro.github.io')
    return response