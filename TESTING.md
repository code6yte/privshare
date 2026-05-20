# TESTING.md

## Manual Test Plan

## Test 1: Upload and Download TXT

1. Create `hello.txt`.
2. Upload it with password `test12345`.
3. Copy share link.
4. Open link.
5. Enter password.
6. Confirm file downloads.

Expected result:

- Downloaded content matches original.

## Test 2: Wrong Password

1. Open a valid share link.
2. Enter wrong password.

Expected result:

- System shows invalid password message.
- File does not download.

## Test 3: Metadata Cleaning for Image

1. Upload a JPG with EXIF data.
2. Download decrypted file.
3. Check metadata using ExifTool.

Expected result:

- Most EXIF fields are removed.

## Test 4: Link Expiry

1. Upload file with expiry set to `1` hour.
2. Manually adjust database expiry time to a past time or wait.
3. Try download.

Expected result:

- System refuses access after expiry.

## Test 5: Token Guessing

Open a fake token URL:

```text
/file/fake-token
```

Expected result:

- 404 or file not found page.

## Automated Tests

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
pytest
```

## Smoke Test

```bash
python cli.py smoke-test
```

The smoke test checks:

- Encryption/decryption works
- Wrong password fails
- Token generation works
