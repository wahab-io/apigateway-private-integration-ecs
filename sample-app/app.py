from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello World!"


@app.route("/hello")
def hello():
    return jsonify({"name": "alice", "email": "alice@example.com"})


@app.route("/info")
def info():
    return jsonify(request.headers.to_wsgi_list())


@app.route("/flask-health-check")
def flask_health_check():
    return jsonify({"msg": "success"})
