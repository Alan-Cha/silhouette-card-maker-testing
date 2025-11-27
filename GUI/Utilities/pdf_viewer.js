const { shell } = require('electron');
const path = require('path');
const { getOutputDir } = require('../shared/constants');

function openInFileExplorer() {
    const outputDir = getOutputDir();
    const pdfPath = path.join(outputDir, 'game.pdf');
    shell.showItemInFolder(pdfPath);
}
