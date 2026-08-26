// app/static/app.js
document.getElementById('btn-search').addEventListener('click', async () => {
    const query = document.getElementById('query').value.trim();
    const limit = parseInt(document.getElementById('limit').value, 10) || 10;

    if (!query) {
        alert('กรุณากรอกคำค้น');
        return;
    }

    const payload = { query, limit };
    try {
        const resp = await fetch('/api/v1/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error(`Error ${resp.status}`);

        const data = await resp.json();
        document.getElementById('output').textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById('output').textContent = `❗️ ${err.message}`;
    }
});
