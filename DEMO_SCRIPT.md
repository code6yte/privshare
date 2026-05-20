# DEMO_SCRIPT.md

## 2-Minute Presentation Script

Good morning. Our project is called **Anonymous Privacy-Preserving File Sharing System**.

The goal is simple: a user should be able to open a website, upload a file, enter a password, and get a unique link that can be shared with another person.

The privacy protection happens in two layers. First, the system removes hidden metadata from the file. For example, images may contain GPS location, camera model, and timestamps. PDFs may contain author name and software information. Second, after metadata cleaning, the system encrypts the file using a key derived from the password entered by the user.

There is no sign-up and no login. The password is not an account password. It is used only for encryption and decryption. The server does not store the password. The server stores only the encrypted file, a random token, salt, nonce, and basic file record.

The sharing link alone is not enough to access the file. The receiver must have both the unique link and the correct password. If the wrong password is entered, AES-GCM authentication fails and the file is not decrypted.

The correct order is metadata cleaning first, then encryption. If we encrypt first, the system cannot read or remove metadata.

Now I will demonstrate the system. I will upload a file, enter a password, generate a share link, open that link in another browser, enter the same password, and download the protected file.

## Demo Steps

1. Open website.
2. Select a JPG or PDF.
3. Enter password.
4. Click upload.
5. Copy generated link.
6. Open link in another browser/device.
7. Enter wrong password first to show failure.
8. Enter correct password to show download.
9. Explain encrypted storage folder and database record.

## Closing Line

This project protects both visible file content and hidden metadata, making file sharing more privacy-preserving than ordinary link-based sharing.
