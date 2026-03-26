"""URL Shortener API — lightweight Flask-based URL shortener with in-memory storage."""

import string
import random
import re
from urllib.parse import urlparse

try:
    from flask import Flask, request, jsonify, redirect
except ImportError:
    raise SystemExit("Flask required: pip install flask")

app = Flask(__name__)

url_store: dict[str, str] = {}
reverse_store: dict[str, str] = {}

CODE_LENGTH = 6
CODE_CHARS = string.ascii_letters + string.digits


def generate_code(length: int = CODE_LENGTH) -> str:
    while True:
        code = "".join(random.choices(CODE_CHARS, k=length))
        if code not in url_store:
            return code


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    url = data["url"].strip()
    if not url:
        return jsonify({"error": "URL cannot be empty"}), 400
    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL. Must be http:// or https://"}), 400
    if len(url) > 2048:
        return jsonify({"error": "URL too long (max 2048 characters)"}), 400

    if url in reverse_store:
        code = reverse_store[url]
        return jsonify({"short_code": code, "short_url": request.host_url + code, "original_url": url})

    code = generate_code()
    url_store[code] = url
    reverse_store[url] = code

    return jsonify({"short_code": code, "short_url": request.host_url + code, "original_url": url}), 201


@app.route("/<code>")
def resolve(code: str):
    if not re.match(r"^[A-Za-z0-9]+$", code):
        return jsonify({"error": "Invalid short code format"}), 400
    if code not in url_store:
        return jsonify({"error": "Short code not found"}), 404
    return redirect(url_store[code], code=302)


@app.route("/stats/<code>")
def stats(code: str):
    if code not in url_store:
        return jsonify({"error": "Short code not found"}), 404
    return jsonify({"short_code": code, "original_url": url_store[code]})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "urls_stored": len(url_store)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
