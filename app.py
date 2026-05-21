import io
import secrets

import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from cleanup import cleanup_expired_files
from config import Config
from crypto_utils import generate_token
from db import get_file_by_token, increment_download_count, init_db, insert_file_record
from storage import read_encrypted, save_encrypted

app = Flask(__name__)
app.config.from_object(Config)

if Config.TRUST_PROXY_HEADERS:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

Config.ensure_dirs()
init_db()


TOKEN_LENGTH_OPTIONS = {6, 8, 12, 16, 24, 32}


def generate_token_with_length(length: int) -> str:
    length = max(6, min(length, 32))
    return secrets.token_urlsafe(length).lower()


def resolve_token(length: int | None) -> str:
    if length is not None:
        return generate_token_with_length(length)
    return generate_token(24)


def build_share_url(token: str) -> str:
    if Config.BASE_URL:
        return f"{Config.BASE_URL}/file/{token}"
    return url_for("download_page", token=token, _external=True)


@app.get("/")
def index():
    return render_template("upload.html", default_expiry=Config.DEFAULT_EXPIRY_HOURS, max_mb=Config.MAX_CONTENT_LENGTH_MB)


@app.post("/upload")
def upload_file():
    ciphertext_file = request.files.get("file")
    salt_b64 = request.form.get("salt", "")
    nonce_b64 = request.form.get("nonce", "")
    original_filename = request.form.get("filename", "")
    content_type = request.form.get("content_type", "application/octet-stream")
    expiry_hours_raw = request.form.get("expiry_hours", str(Config.DEFAULT_EXPIRY_HOURS))
    token_length_raw = request.form.get("token_length", "24")

    if not ciphertext_file or not salt_b64 or not nonce_b64 or not original_filename:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        salt = base64.b64decode(salt_b64)
        nonce = base64.b64decode(nonce_b64)
    except Exception:
        return jsonify({"error": "Invalid salt or nonce encoding"}), 400

    if len(salt) != 16 or len(nonce) != 12:
        return jsonify({"error": "Invalid salt or nonce length"}), 400

    try:
        token_length = int(token_length_raw)
    except ValueError:
        token_length = 24

    token = resolve_token(token_length)

    try:
        expiry_hours = max(1, min(int(expiry_hours_raw), 168))
    except ValueError:
        expiry_hours = Config.DEFAULT_EXPIRY_HOURS

    stored_filename = f"{token}.bin"

    try:
        save_encrypted(stored_filename, ciphertext_file.read())

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expiry_hours)

        insert_file_record({
            "token": token,
            "original_filename": secure_filename(original_filename),
            "stored_filename": stored_filename,
            "content_type": content_type,
            "salt": salt,
            "nonce": nonce,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "download_count": 0,
            "metadata_status": "client-side-encrypted",
            "size_bytes": ciphertext_file.content_length or 0,
        })

        share_url = build_share_url(token)
        return jsonify({
            "share_url": share_url,
            "token": token,
            "expires_at": expires_at.isoformat(),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/file/<token>")
def download_page(token: str):
    token = token.lower()
    record = get_file_by_token(token)
    if not record:
        abort(404)
    if _is_expired(record["expires_at"]):
        return render_template("expired.html"), 410
    return render_template("download.html", token=token, filename=record["original_filename"])


@app.get("/api/file/<token>")
def file_metadata(token: str):
    token = token.lower()
    record = get_file_by_token(token)
    if not record:
        abort(404)
    if _is_expired(record["expires_at"]):
        return jsonify({"error": "Link expired"}), 410
    return jsonify({
        "filename": record["original_filename"],
        "content_type": record["content_type"],
        "salt": base64.b64encode(record["salt"]).decode(),
        "nonce": base64.b64encode(record["nonce"]).decode(),
        "size_bytes": record["size_bytes"],
    })


@app.get("/file/<token>/data")
def file_data(token: str):
    token = token.lower()
    record = get_file_by_token(token)
    if not record:
        abort(404)
    if _is_expired(record["expires_at"]):
        return jsonify({"error": "Link expired"}), 410
    increment_download_count(token)
    ciphertext = read_encrypted(record["stored_filename"])
    return send_file(
        io.BytesIO(ciphertext),
        mimetype="application/octet-stream",
        as_attachment=False,
    )


@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "privshare"})


@app.post("/maintenance/cleanup-expired")
def maintenance_cleanup():
    removed = cleanup_expired_files()
    return jsonify({"removed": removed})


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(_):
    return jsonify({"error": "Internal server error"}), 500


def _is_expired(expires_at: str | None) -> bool:
    if not expires_at:
        return False
    return datetime.fromisoformat(expires_at) < datetime.now(timezone.utc)
