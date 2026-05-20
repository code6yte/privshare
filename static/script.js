function copyShareLink() {
    const input = document.getElementById('shareLink');
    if (!input) return;
    input.select();
    input.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(input.value).then(() => {
        alert('Share link copied. Send the password separately.');
    }).catch(() => {
        document.execCommand('copy');
        alert('Share link copied. Send the password separately.');
    });
}
