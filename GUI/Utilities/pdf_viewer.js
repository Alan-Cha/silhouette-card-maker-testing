const { shell } = require('electron');
const path = require('path');
const { pathToFileURL } = require('url');
const { getOutputDir } = require('../shared/constants');

function getSelectedPdfFileName() {
    const params = new URLSearchParams(window.location.search);
    const requestedFile = params.get('file');
    if (!requestedFile) {
        return 'game.pdf';
    }

    const cleaned = path.basename(requestedFile);
    if (!cleaned.toLowerCase().endsWith('.pdf')) {
        return 'game.pdf';
    }

    return cleaned;
}

function openInFileExplorer() {
    const outputDir = getOutputDir();
    const pdfPath = path.join(outputDir, getSelectedPdfFileName());
    shell.showItemInFolder(pdfPath);
}

function setPdfSource() {
    const viewerFrame = document.getElementById('pdfFrame');
    if (!viewerFrame) {
        return;
    }

    const outputDir = getOutputDir();
    const pdfPath = path.join(outputDir, getSelectedPdfFileName());
    viewerFrame.src = pathToFileURL(pdfPath).href;
}

window.addEventListener('DOMContentLoaded', setPdfSource);
