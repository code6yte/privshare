# ARCHITECTURE.md

## High-Level Architecture

```text
Browser
  │
  │ Upload file + password
  ▼
Flask Web App
  │
  ├── Metadata Cleaner
  │       ├── ExifTool if available
  │       ├── Pillow for images
  │       └── pypdf for PDFs
  │
  ├── Encryption Engine
  │       ├── PBKDF2-HMAC-SHA256
  │       └── AES-256-GCM
  │
  ├── SQLite Database
  │       └── Stores token, salt, nonce, path, expiry
  │
  └── Encrypted File Storage
          └── Stores encrypted bytes only
```

## Component Breakdown

### 1. Web Layer

Files:

- `app.py`
- `templates/`
- `static/`

Responsibilities:

- Render upload page
- Receive uploaded file
- Validate file size and extension
- Return unique link
- Render password page for receiver
- Decrypt file after password submission

### 2. Metadata Cleaner

File:

- `metadata_cleaner.py`

Responsibilities:

- Create a sanitized copy of the uploaded file
- Remove metadata before encryption
- Return cleaning status for audit/display

### 3. Crypto Layer

File:

- `crypto_utils.py`

Responsibilities:

- Generate salt
- Generate AES-GCM nonce
- Derive key from password using PBKDF2
- Encrypt cleaned bytes
- Decrypt encrypted bytes
- Detect invalid password through authentication failure

### 4. Database Layer

File:

- `db.py`

Responsibilities:

- Initialize SQLite schema
- Insert file records
- Fetch records by token
- Increment download count
- Delete expired records

### 5. Storage Layer

File:

- `storage.py`

Responsibilities:

- Store encrypted files
- Read encrypted files
- Delete encrypted files
- Keep paths inside safe directories

## Upload Sequence

```text
POST /upload
  ↓
Validate password and file
  ↓
Save upload temporarily
  ↓
Clean metadata
  ↓
Read cleaned bytes
  ↓
Generate salt and nonce
  ↓
Derive key from password
  ↓
Encrypt with AES-GCM
  ↓
Store encrypted file
  ↓
Save SQLite record
  ↓
Delete temporary files
  ↓
Show unique share link
```

## Download Sequence

```text
GET /file/<token>
  ↓
Show password form

POST /file/<token>
  ↓
Load SQLite record
  ↓
Check expiry
  ↓
Read encrypted file
  ↓
Derive key from submitted password using stored salt
  ↓
Try AES-GCM decryption using stored nonce
  ↓
If success: return decrypted file
  ↓
If failure: show invalid password error
```

## Database Schema

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    content_type TEXT,
    salt BLOB NOT NULL,
    nonce BLOB NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    download_count INTEGER NOT NULL DEFAULT 0,
    metadata_status TEXT,
    size_bytes INTEGER NOT NULL
);
```

## Why Metadata Cleaning Happens Before Encryption

Metadata cleaning must happen before encryption because encrypted bytes are unreadable. If the system encrypts first, the metadata cleaner cannot safely inspect or rewrite the file.

Correct order:

```text
Clean metadata → Encrypt → Share
```

Incorrect order:

```text
Encrypt → Clean metadata
```
