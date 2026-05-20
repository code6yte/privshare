# Privacy-Preserving File Sharing System

A no-signup, password-protected file sharing web app for a cybersecurity lab semester project.

The user opens the website, uploads a file, enters a password, and receives a unique share link. The system cleans metadata first, then encrypts the cleaned file with a key derived from the password. The receiver opens the link, enters the same password, and downloads the decrypted file.

## Core Idea

```text
Upload file + password
        ↓
Metadata sanitization
        ↓
Password-based AES-GCM encryption
        ↓
Encrypted file stored on server
        ↓
Unique share link generated
        ↓
Receiver enters password to decrypt
```

## Features

- No sign-up and no user accounts
- Unique random share links
- Password-based encryption
- AES-256-GCM authenticated encryption
- PBKDF2-HMAC-SHA256 key derivation
- Metadata cleaning before encryption
- SQLite file record database
- Link expiry support
- Download count tracking
- Optional ExifTool support
- CLI helper commands
- Docker-ready structure
- Deployment guide included

## Important Security Rule

The password is never placed inside the URL and is not stored in the database.

The link identifies the encrypted file. The password decrypts it.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env
python cli.py init-db
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Make It Shareable Over the Internet

For a live demo, deploy the app on a public host or run it through a secure tunnel. See [`DEPLOYMENT.md`](DEPLOYMENT.md).

## Project Documents

- [`PROJECT.md`](PROJECT.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`FEATURES.md`](FEATURES.md)
- [`SECURITY.md`](SECURITY.md)
- [`THREAT_MODEL.md`](THREAT_MODEL.md)
- [`API.md`](API.md)
- [`SETUP.md`](SETUP.md)
- [`DEPLOYMENT.md`](DEPLOYMENT.md)
- [`TESTING.md`](TESTING.md)
- [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)
- [`CLI_AGENTS.md`](CLI_AGENTS.md)

## Default Routes

| Route | Method | Purpose |
|---|---:|---|
| `/` | GET | Upload form |
| `/upload` | POST | Clean, encrypt, store, generate link |
| `/file/<token>` | GET | Password form for receiver |
| `/file/<token>` | POST | Decrypt and download |
| `/health` | GET | Health check |

## Recommended Demo File Types

- `.jpg`, `.jpeg`, `.png`
- `.pdf`
- `.txt`

Other files can still be encrypted and shared, but metadata cleaning may depend on ExifTool support.

## Educational Disclaimer

This is a semester project scaffold. It demonstrates secure design concepts, but production deployment needs hardened storage, malware scanning, rate limiting, HTTPS, monitoring, backups, and professional security review.
