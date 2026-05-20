# SECURITY.md

## Security Design

This project uses three privacy/security layers:

```text
Metadata Cleaning + Password-Based Encryption + Unique Share Links
```

## 1. Password Handling

The user password is not stored in the database.

Instead:

```text
Password + random salt → PBKDF2-HMAC-SHA256 → AES key
```

The salt is stored because it is required to derive the same key during download. A salt is not secret.

## 2. Encryption

The cleaned file is encrypted using AES-256-GCM.

AES-GCM is useful because it provides:

- Confidentiality: hides file content
- Integrity: detects tampering
- Authentication: wrong password causes decryption failure

## 3. Nonce

Each file receives a random 96-bit nonce for AES-GCM.

Important rule:

```text
Never reuse the same key + nonce pair.
```

This project generates a new salt and nonce for every upload.

## 4. Metadata Sanitization

The system cleans metadata before encryption.

This protects against privacy leakage from:

- GPS coordinates
- Author fields
- Software fields
- Device model
- Timestamps

## 5. Link Security

The unique token is generated using secure randomness.

The link does not contain the password.

Good:

```text
https://example.com/file/random-token
```

Bad:

```text
https://example.com/file/random-token?password=mysecret
```

## 6. Why Link + Password Is Better Than Link Alone

If someone accidentally receives the link, they still cannot decrypt the file without the password.

## 7. What the Server Stores

The server stores:

- Encrypted file
- Random token
- Salt
- Nonce
- Original filename
- Expiry time
- Download count

The server does not store:

- Plain file content
- User password
- User account data

## 8. Recommended Production Hardening

For a real production system, add:

- HTTPS only
- File type validation
- Antivirus/malware scanning
- Rate limiting
- CAPTCHA or abuse control
- Object storage with private buckets
- Secure deletion strategy
- Strong logging without sensitive data
- CSRF protection
- Content Security Policy
- Password strength hints
- Maximum failed password attempts

## 9. Known Limitations

- Server receives the plaintext file before encryption, so server-side trust is required.
- Metadata removal is best-effort, especially for complex formats.
- The demo uses local file storage.
- Decryption is memory-based and intended for moderate file sizes.
- No user identity means no account-based revocation.

## 10. Presentation Line

> Our system does not rely only on secure links. It combines metadata cleaning and password-based encryption, so both hidden file information and actual file content are protected before sharing.
