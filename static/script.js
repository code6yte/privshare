const PBKDF2_ITERATIONS = 390000;
const SALT_BYTES = 16;
const NONCE_BYTES = 12;
const KEY_BYTES = 32;

const MEMORABLE_WORDS = [
    "apple","brave","cloud","delta","eagle","flame","ghost","harbor","ivory","jewel",
    "karma","lunar","maple","noble","oasis","pearl","quiet","river","stone","tiger",
    "ultra","vivid","whale","xenon","yield","zebra","atlas","blaze","crest","drift",
    "ember","frost","globe","haven","iron","jade","kite","leaf","moon","nest",
    "orbit","pulse","quest","rain","spark","tide","umbra","vine","wave","zephyr"
];

function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

function base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

async function deriveKey(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        'raw',
        enc.encode(password),
        'PBKDF2',
        false,
        ['deriveKey']
    );
    return crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: PBKDF2_ITERATIONS,
            hash: 'SHA-256',
        },
        keyMaterial,
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt', 'decrypt']
    );
}

async function encryptFile(file, password) {
    const salt = crypto.getRandomValues(new Uint8Array(SALT_BYTES));
    const nonce = crypto.getRandomValues(new Uint8Array(NONCE_BYTES));
    const key = await deriveKey(password, salt);

    const fileBuffer = await file.arrayBuffer();
    const encrypted = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv: nonce },
        key,
        fileBuffer
    );

    return {
        ciphertext: new Blob([encrypted], { type: 'application/octet-stream' }),
        salt: arrayBufferToBase64(salt),
        nonce: arrayBufferToBase64(nonce),
    };
}

async function decryptFile(ciphertext, password, saltB64, nonceB64) {
    const salt = base64ToArrayBuffer(saltB64);
    const nonce = base64ToArrayBuffer(nonceB64);
    const key = await deriveKey(password, salt);

    try {
        const decrypted = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: new Uint8Array(nonce) },
            key,
            ciphertext
        );
        return decrypted;
    } catch {
        throw new Error('Invalid password or corrupted file');
    }
}

function triggerDownload(data, filename) {
    const blob = new Blob([data]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function generateMemorableToken() {
    const words = [];
    const count = 3 + Math.floor(Math.random() * 2);
    for (let i = 0; i < count; i++) {
        words.push(MEMORABLE_WORDS[Math.floor(Math.random() * MEMORABLE_WORDS.length)]);
    }
    return words.join('-');
}

function copyShareLink() {
    const input = document.getElementById('shareLink');
    const btn = input?.nextElementSibling;
    if (!input || !btn) return;

    navigator.clipboard.writeText(input.value).then(() => {
        const original = btn.textContent;
        btn.textContent = 'Copied';
        btn.style.color = 'var(--success)';
        btn.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        setTimeout(() => {
            btn.textContent = original;
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 2000);
    }).catch(() => {
        input.select();
        document.execCommand('copy');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateToken');
    const tokenLengthInput = document.getElementById('tokenLength');
    const tokenPreview = document.getElementById('tokenPreview');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const successResult = document.getElementById('successResult');

    if (generateBtn && tokenLengthInput) {
        const showPreview = () => {
            const len = parseInt(tokenLengthInput.value) || 24;
            const clamped = Math.max(6, Math.min(len, 32));
            const token = generateMemorableToken().replace(/-/g, '').substring(0, clamped);
            tokenPreview.textContent = `Example: ${token}`;
        };
        generateBtn.addEventListener('click', showPreview);
        tokenLengthInput.addEventListener('input', showPreview);
        showPreview();
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fileInput = document.getElementById('fileInput');
            const passwordInput = document.getElementById('passwordInput');
            const file = fileInput.files[0];
            const password = passwordInput.value;

            if (!file || !password || password.length < 8) {
                return;
            }

            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Encrypting...';
            progressDiv.style.display = 'block';
            progressBar.style.width = '10%';
            progressText.textContent = 'Encrypting in browser...';

            try {
                const encrypted = await encryptFile(file, password);
                progressBar.style.width = '60%';
                progressText.textContent = 'Uploading to server...';

                const formData = new FormData();
                formData.append('file', encrypted.ciphertext, file.name + '.enc');
                formData.append('salt', encrypted.salt);
                formData.append('nonce', encrypted.nonce);
                formData.append('filename', file.name);
                formData.append('content_type', file.type || 'application/octet-stream');
                formData.append('expiry_hours', uploadForm.querySelector('[name="expiry_hours"]').value);
                formData.append('token_length', tokenLengthInput?.value || '24');

                const resp = await fetch('/upload', { method: 'POST', body: formData });
                const data = await resp.json();

                if (!resp.ok) {
                    throw new Error(data.error || 'Upload failed');
                }

                progressBar.style.width = '100%';
                progressText.textContent = 'Done!';

                uploadForm.style.display = 'none';
                successResult.style.display = 'block';
                document.getElementById('shareLink').value = data.share_url;
                document.getElementById('resultExpires').textContent = data.expires_at;
            } catch (err) {
                alert('Error: ' + err.message);
                uploadBtn.disabled = false;
                uploadBtn.textContent = 'Encrypt & Upload';
                progressDiv.style.display = 'none';
            }
        });
    }

    const receiveForm = document.getElementById('receiveForm');
    if (receiveForm) {
        receiveForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = document.getElementById('receiveInput').value.trim();
            if (!input) return;

            let token = input;
            if (input.includes('/file/')) {
                token = input.split('/file/')[1].split('?')[0].split('#')[0];
            }
            if (token) {
                window.location.href = `/file/${token}`;
            }
        });
    }
});
