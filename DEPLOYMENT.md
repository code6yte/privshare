# DEPLOYMENT.md

## Goal

Make the generated share links accessible over the internet.

The app already generates links using the current request host. This means:

- Running locally creates `http://127.0.0.1:5000/file/<token>` links.
- Running on a public domain creates `https://your-domain.com/file/<token>` links.

## Option 1: Local Demo with a Tunnel

Use a secure tunnel when you want to run the app on your laptop but share it with someone else.

General flow:

```text
Run Flask locally
        ↓
Start tunnel to port 5000
        ↓
Tunnel gives public HTTPS URL
        ↓
Open public URL and upload file
        ↓
Generated share link uses public URL
```

Example local command:

```bash
python app.py
```

Then tunnel port `5000` with your preferred tunneling tool.

## Option 2: Docker Deployment

Build image:

```bash
docker build -t privshare .
```

Run container:

```bash
docker run -p 8000:8000 --env-file .env privshare
```

Open:

```text
http://localhost:8000
```

For internet sharing, deploy this container on a VPS or cloud platform.

## Option 3: VPS Deployment

On a VPS:

```bash
git clone <your-repo-url>
cd privshare
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python cli.py init-db
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

Then use Nginx/Caddy as a reverse proxy with HTTPS.

## Required Production Environment Variables

```text
FLASK_ENV=production
SECRET_KEY=change-this-long-random-value
BASE_URL=https://your-domain.com
MAX_CONTENT_LENGTH_MB=32
DEFAULT_EXPIRY_HOURS=24
```

## Persistent Storage Warning

The app stores encrypted files on disk and file records in SQLite. If your hosting platform has ephemeral storage, uploaded files may disappear after restart.

For stable internet sharing, use one of these:

- VPS with persistent disk
- Docker volume
- Cloud persistent volume
- Object storage integration as future improvement

## HTTPS Requirement

Public deployments should use HTTPS. Without HTTPS, the upload password and file travel over the network in plaintext.

## Reverse Proxy Notes

When behind a reverse proxy, ensure forwarded headers are passed correctly so generated URLs use HTTPS.

The app uses `ProxyFix` when configured.

## Demo Recommendation

For class demo:

1. Run locally.
2. Start a tunnel to port 5000.
3. Open the public tunnel URL.
4. Upload image/PDF + password.
5. Share generated link with another device.
6. Enter password on second device.
7. Download file.
