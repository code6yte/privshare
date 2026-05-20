# FEATURES.md

## Feature List

## 1. Anonymous Upload

Users do not create accounts. They simply open the website and upload a file.

Benefits:

- No sign-up friction
- No stored user identity
- Easier demo

## 2. Password-Based File Protection

The uploader enters a password during upload. The same password is required during download.

Important:

- Password is not stored
- Password is not added to the URL
- Password is used to derive the encryption key

## 3. Unique Share Link

Each upload receives a random token-based link.

Example:

```text
https://your-domain.com/file/Vq3mA9kX0BdqTfZ9L2pQGA
```

The token is generated using cryptographically secure randomness.

## 4. Metadata Cleaning

The system attempts to remove metadata before encryption.

Supported demo formats:

- Images: `.jpg`, `.jpeg`, `.png`
- PDFs: `.pdf`
- Text files: `.txt` have no complex metadata and are copied safely

Optional ExifTool support improves coverage for many more formats.

## 5. AES-GCM Encryption

AES-GCM provides confidentiality and integrity. If the wrong password is entered or the ciphertext is modified, decryption fails.

## 6. Link Expiry

Uploaded files can automatically expire after a configured number of hours.

Default:

```text
24 hours
```

Configurable in `.env`:

```text
DEFAULT_EXPIRY_HOURS=24
```

## 7. Download Tracking

The database tracks how many times a file has been successfully downloaded.

## 8. Health Check Endpoint

`/health` returns a JSON status useful for deployment monitoring.

## 9. CLI Agents

The project includes helper commands:

```bash
python cli.py init-db
python cli.py cleanup-expired
python cli.py list-files
python cli.py smoke-test
```

## 10. Internet Sharing Ready

The generated share URL uses the active request domain. If the app is deployed on a public domain, generated links are public internet links.

For local demo, use a secure tunnel or deploy to a public host.
