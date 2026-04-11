const { ipcRenderer } = require('electron');

window.addEventListener('DOMContentLoaded', () => {
    const mdForm = document.getElementById('mdForm');
    const mdTextInput = document.getElementById('mdText');
    const paperSizeInput = document.getElementById('paperSize');
    const ppiInput = document.getElementById('ppi');
    const qualityInput = document.getElementById('quality');
    const generatePdfBtn = document.getElementById('generatePdfBtn');
    const spinner = document.getElementById('spinner');

    const savedText = sessionStorage.getItem('mtg-md-text');
    if (savedText) {
        mdTextInput.value = savedText;
    }

    mdTextInput.addEventListener('input', () => {
        sessionStorage.setItem('mtg-md-text', mdTextInput.value);
    });

    mdForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const markdownText = mdTextInput.value.trim();
        if (!markdownText) {
            alert('Please paste markdown content before generating a PDF.');
            return;
        }

        const ppi = Number.parseInt(ppiInput.value, 10);
        const quality = Number.parseInt(qualityInput.value, 10);
        if (!Number.isInteger(ppi) || ppi < 1) {
            alert('PPI must be a whole number greater than 0.');
            return;
        }
        if (!Number.isInteger(quality) || quality < 0 || quality > 100) {
            alert('Quality must be a whole number between 0 and 100.');
            return;
        }

        generatePdfBtn.disabled = true;
        spinner.classList.remove('hidden');
        spinner.classList.add('flex');

        try {
            await ipcRenderer.invoke('run-md-to-pdf', {
                markdownText,
                paperSize: paperSizeInput.value,
                ppi,
                quality,
                outputFileName: 'translatedTextBoxes.pdf',
            });

            location.href = '../Utilities/pdf_viewer.html?file=translatedTextBoxes.pdf';
        } catch (error) {
            alert('Error creating PDF:\n' + error);
        } finally {
            spinner.classList.remove('flex');
            spinner.classList.add('hidden');
            generatePdfBtn.disabled = false;
        }
    });
});
