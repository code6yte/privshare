# THREAT_MODEL.md

## Assets

| Asset | Why It Matters |
|---|---|
| Original file content | Must remain private |
| File metadata | May reveal private identity/location |
| Password | Needed to decrypt file |
| Share link token | Identifies encrypted file |
| Salt/nonce | Needed for decryption but not secret |

## Threat Actors

| Threat Actor | Goal |
|---|---|
| Random internet user | Guess share links |
| Link recipient without password | Access file without authorization |
| Passive observer | Learn file contents or metadata |
| Server attacker | Read stored files |
| Malicious uploader | Upload harmful or oversized files |

## Threats and Mitigations

| Threat | Mitigation |
|---|---|
| Link guessing | Long secure random tokens |
| Link leaked | Password still required |
| Server storage compromise | Stored files are encrypted |
| Metadata leakage | Clean metadata before encryption |
| Wrong password guessing | AES-GCM fails; add rate limiting in production |
| Tampering with encrypted file | AES-GCM authentication detects it |
| Oversized upload | `MAX_CONTENT_LENGTH` limit |
| Path traversal | `secure_filename` and controlled storage paths |

## Trust Assumptions

- The Flask server is trusted during upload and download processing.
- The user shares the password through a separate secure channel.
- The deployment uses HTTPS in public environments.
- Temporary files are deleted after processing.

## Out of Scope Attacks

- Malware scanning bypass
- Browser compromise
- Host operating system compromise
- Password reuse attacks outside this system
- Side-channel attacks
- Traffic analysis

## Risk Rating

| Risk | Rating | Notes |
|---|---:|---|
| Weak user password | High | Add password strength guidance |
| Metadata cleaner misses complex metadata | Medium | Use ExifTool where possible |
| Public host storage loss | Medium | Use persistent storage |
| Brute force on download page | Medium | Add rate limiting in production |
| Token guessing | Low | Token length is high entropy |
