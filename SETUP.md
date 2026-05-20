# SETUP.md

## Requirements

- Python 3.10+
- pip
- Optional: ExifTool installed on system

## Install Python Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed.

## Initialize Database

```bash
python cli.py init-db
```

## Run Locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Install ExifTool Optional

Linux:

```bash
sudo apt update
sudo apt install libimage-exiftool-perl
```

macOS:

```bash
brew install exiftool
```

Windows:

Download ExifTool from the official website and add it to PATH.

## Smoke Test

```bash
python cli.py smoke-test
```

## Reset Project Data

Stop the server, then delete:

```text
instance/privshare.db
storage/encrypted_files/*
storage/tmp/*
```

Then run:

```bash
python cli.py init-db
```
