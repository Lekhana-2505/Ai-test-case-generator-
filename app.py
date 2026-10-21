"""Web UI for the test case generator. Run: python app.py, then open http://127.0.0.1:5000

Set APP_PASSWORD to require a login (any username, that password) - do this when hosting publicly,
otherwise anyone with the URL can spend your API credits.
"""
import hmac
import os

from flask import Flask, Response, jsonify, render_template, request

from testgen import GenerationError, generate_tests
from testgen.exporters import EXPORTERS
from testgen.models import TestSuite

app = Flask(__name__)
APP_PASSWORD = os.environ.get("APP_PASSWORD")
EFFORTS = {"low", "medium", "high", "xhigh"}


@app.before_request
def require_password():
    if not APP_PASSWORD:
        return None
    auth = request.authorization
    if auth and auth.password and hmac.compare_digest(auth.password, APP_PASSWORD):
        return None
    return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Test Case Generator"'})


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/generate")
def api_generate():
    body = request.get_json(force=True)
    try:
        suite = generate_tests(
            source=body.get("source", ""),
            categories=body.get("categories") or None,
            count=max(1, min(int(body.get("count", 10)), 50)),
            framework=(body.get("framework") or "").strip() or None,
            effort=body.get("effort") if body.get("effort") in EFFORTS else "medium",
        )
    except GenerationError as e:
        return jsonify(error=str(e)), 400
    return jsonify(suite.model_dump())


@app.post("/api/export/<fmt>")
def api_export(fmt):
    if fmt not in EXPORTERS:
        return jsonify(error="unknown format"), 400
    suite = TestSuite.model_validate(request.get_json(force=True))
    return EXPORTERS[fmt](suite), 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    app.run(debug=True)
