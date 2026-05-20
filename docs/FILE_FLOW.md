# File Flow

## Upload

```text
Raw file lands in temporary folder
        ↓
Metadata-cleaned copy is created
        ↓
Cleaned bytes are encrypted
        ↓
Encrypted bytes are saved permanently
        ↓
Temporary raw and cleaned files are deleted
```

## Download

```text
Encrypted bytes are read from storage
        ↓
Password derives key using stored salt
        ↓
AES-GCM decrypts bytes using stored nonce
        ↓
Plain file is streamed to receiver
```

## Storage Principle

Permanent storage contains encrypted files only.
