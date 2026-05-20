# PROJECT.md

## Project Title

**Anonymous Privacy-Preserving File Sharing System Using Metadata Sanitization and Password-Based Encryption**

## Problem Statement

Many file sharing systems protect file transfer using HTTPS but still expose hidden privacy risks. Files can contain sensitive metadata such as author names, device identifiers, GPS coordinates, creation time, editing software, and revision information. Also, if files are stored without encryption, a server compromise can expose uploaded content.

This project solves both problems in a single upload flow:

1. Remove metadata before sharing.
2. Encrypt the cleaned file using a password chosen by the uploader.
3. Generate a unique link that can be shared with a receiver.

## Goal

Build a no-signup web-based file sharing system where users can upload a file, enter a password, and get a unique share link. Anyone with the link still needs the password to decrypt the file.

## Main Privacy Concepts

### 1. Metadata Privacy

Files can leak private information through hidden metadata. The system attempts to sanitize metadata before encryption.

Examples:

- Image GPS location
- Camera model
- Device name
- PDF author
- Creation date
- Editing software
- Revision history

### 2. Content Privacy

After metadata cleaning, the file is encrypted using a key derived from the user password. The server stores only encrypted data.

## Single-Shot Flow

```text
User opens website
        ↓
Uploads file
        ↓
Enters password
        ↓
System cleans metadata
        ↓
System derives encryption key from password
        ↓
System encrypts cleaned file
        ↓
System stores encrypted file
        ↓
System generates unique share link
        ↓
Receiver opens link and enters password
        ↓
System decrypts and returns file
```

## Scope

### In Scope

- Anonymous upload
- Password-based encryption
- Unique share links
- Metadata cleaning
- SQLite record storage
- Expiry time
- Local encrypted file storage
- CLI maintenance commands
- Deployment guide

### Out of Scope

- User accounts
- Email verification
- Cloud object storage integration
- End-to-end browser-only encryption
- Malware scanning
- Enterprise access control

## Technologies

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python Flask |
| Database | SQLite |
| Encryption | Python cryptography library |
| Metadata Cleaning | ExifTool, Pillow, pypdf |
| Deployment | Docker/Gunicorn-compatible |

## Expected Deliverables

- Working web application
- Documentation
- Presentation explanation
- Demo script
- Source code
- CLI helper agents
- Security design notes
