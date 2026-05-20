import io
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, send_file, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from cleanup import cleanup_expired_files
from config import Config
from crypto_utils import InvalidPassword, encrypt_bytes, decrypt_bytes, generate_token
from db import get_file_by_token, increment_download_count, init_db, insert_file_record
from metadata_cleaner import clean_metadata
from storage import read_encrypted, save_encrypted

app = Flask(__name__)
app.config.from_object(Config)

if Config.TRUST_PROXY_HEADERS:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

Config.ensure_dirs()
init_db()


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in Config.ALLOWED_EXTENSIONS


def build_share_url(token: str) -> str:
    if Config.BASE_URL:
        return f"{Config.BASE_URL}/file/{token}"
    return url_for("download_page", token=token, _external=True)


@app.get("/")
def index():
    return render_template("upload.html", default_expiry=Config.DEFAULT_EXPIRY_HOURS, max_mb=Config.MAX_CONTENT_LENGTH_MB)


@app.post("/upload")
def upload_file():
    uploaded = request.files.get("file")
    password = request.form.get("password", "")
    expiry_hours_raw = request.form.get("expiry_hours", str(Config.DEFAULT_EXPIRY_HOURS))

    if not uploaded or uploaded.filename == "":
        flash("Please select a file.", "error")
        return redirect(url_for("index"))

    if not password or len(password) < 8:
        flash("Please enter a password with at least 8 characters.", "error")
        return redirect(url_for("index"))

    original_filename = secure_filename(uploaded.filename)
    if not original_filename or not allowed_file(original_filename):
        flash("This file type is not allowed for the demo.", "error")
        return redirect(url_for("index"))

    try:
        expiry_hours = max(1, min(int(expiry_hours_raw), 168))
    except ValueError:
        expiry_hours = Config.DEFAULT_EXPIRY_HOURS

    token = generate_token(24)
    tmp_path = Config.TMP_DIR / f"upload_{token}_{original_filename}"
    cleaned_dir = Config.TMP_DIR / f"cleaned_{token}"

    try:
        uploaded.save(tmp_path)
        clean_result = clean_metadata(tmp_path, cleaned_dir)
        cleaned_bytes = clean_result.output_path.read_bytes()

        encrypted = encrypt_bytes(cleaned_bytes, password, iterations=Config.PBKDF2_ITERATIONS)
        stored_filename = f"{token}.bin"
        save_encrypted(stored_filename, encrypted.ciphertext)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expiry_hours)

        insert_file_record({
            "token": token,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "content_type": uploaded.content_type or "application/octet-stream",
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "download_count": 0,
            "metadata_status": f"{clean_result.status} using {clean_result.cleaner_used}: {clean_result.details}",
            "size_bytes": len(encrypted.ciphertext),
        })

        share_url = build_share_url(token)
        return render_template(
            "success.html",
            share_url=share_url,
            token=token,
            expires_at=expires_at,
            metadata_status=f"{clean_result.status} using {clean_result.cleaner_used}",
        )
    except RuntimeError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    except Exception:
        flash("An unexpected error occurred while processing your file. Please try again.", "error")
        return redirect(url_for("index"))
    finally:
        _safe_unlink(tmp_path)
        _safe_rmtree(cleaned_dir)


@app.get("/file/<token>")
def download_page(token: str):
    record = get_file_by_token(token)
    if not record:
        abort(404)
    if _is_expired(record["expires_at"]):
        return render_template("expired.html"), 410
    return render_template("download.html", token=token, filename=record["original_filename"])


@app.post("/file/<token>")
def download_file(token: str):
    record = get_file_by_token(token)
    if not record:
        abort(404)
    if _is_expired(record["expires_at"]):
        return render_template("expired.html"), 410

    password = request.form.get("password", "")
    if not password:
        flash("Password is required.", "error")
        return redirect(url_for("download_page", token=token))

    ciphertext = read_encrypted(record["stored_filename"])
    try:
        plaintext = decrypt_bytes(
            ciphertext,
            password,
            salt=record["salt"],
            nonce=record["nonce"],
            iterations=Config.PBKDF2_ITERATIONS,
        )
    except InvalidPassword:
        flash("Invalid password or corrupted file.", "error")
        return redirect(url_for("download_page", token=token))

    increment_download_count(token)
    return send_file(
        io.BytesIO(plaintext),
        as_attachment=True,
        download_name=record["original_filename"],
        mimetype=record["content_type"] or "application/octet-stream",
    )


@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "privshare"})


@app.post("/maintenance/cleanup-expired")
def maintenance_cleanup():
    # For classroom/demo use only. In production, protect this endpoint or remove it.
    removed = cleanup_expired_files()
    return jsonify({"removed": removed})


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(_):
    flash("Something went wrong on our end. Please try again.", "error")
    return redirect(url_for("index"))


def _is_expired(expires_at: str | None) -> bool:
    if not expires_at:
        return False
    return datetime.fromisoformat(expires_at) < datetime.now(timezone.utc)


def _safe_unlink(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


def _safe_rmtree(path: Path) -> None:
    try:
        if path.exists():
            for item in path.iterdir():
                if item.is_file():
                    item.unlink()
            path.rmdir()
    except Exception:
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
