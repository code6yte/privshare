# Presentation Points

## Key Selling Points

- No account required
- Password is for encryption, not login
- Link and password are separate secrets
- Metadata is cleaned before encryption
- Server stores encrypted files only
- Wrong password fails due to AES-GCM authentication

## Strong Sentence

> Our system protects privacy twice: it removes hidden metadata and encrypts the actual file content before generating a shareable link.

## Diagram

```text
Upload + Password
       ↓
Metadata Cleaner
       ↓
Password-Based Key Derivation
       ↓
AES-GCM Encryption
       ↓
Encrypted Storage
       ↓
Unique Share Link
```
