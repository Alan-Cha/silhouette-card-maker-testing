const { ipcRenderer } = require('electron');

function loadImages() {
    ipcRenderer.invoke('get-front-images').then(files => {
        const grid = document.getElementById('frontImagesGrid');
        grid.innerHTML = '';
        files.forEach(f => {
            const div = document.createElement('div');
            div.style.textAlign = 'center';
            div.style.wordBreak = 'break-all';
            const img = document.createElement('img');
            img.src = `../game/front/${f}`;
            img.alt = f;
            img.style.width = '100px';
            img.style.height = '140px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '6px';
            img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.12)';
            div.appendChild(img);
            const label = document.createElement('div');
            label.textContent = f;
            label.style.fontSize = '0.8em';
            label.style.marginTop = '0.5em';
            div.appendChild(label);
            grid.appendChild(div);
        });
    });
}

window.addEventListener('DOMContentLoaded', () => {
    loadImages();
    document.getElementById('createPdfBtn').onclick = async function() {
        const args = document.getElementById('pdfArgs').value;
        try {
            const result = await ipcRenderer.invoke('run-create-pdf', args);
            alert('PDF created!\n' + result);
        } catch (err) {
            alert('Error creating PDF:\n' + err);
        }
    }
});
