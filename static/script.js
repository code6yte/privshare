function copyShareLink() {
    const input = document.getElementById('shareLink');
    const btn = input.nextElementSibling;
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
        input.setSelectionRange(0, 99999);
        document.execCommand('copy');
    });
}
