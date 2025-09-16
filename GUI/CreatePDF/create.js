// Create PDF page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const frontImagesGrid = document.getElementById('frontImagesGrid');
    const clearFrontBtn = document.getElementById('clearFrontBtn');
    const createPdfBtn = document.getElementById('createPdfBtn');
    const onlyFrontsCheckbox = document.getElementById('onlyFrontsCheckbox');
    const skip4Checkbox = document.getElementById('skip4Checkbox');
    const pdfArgs = document.getElementById('pdfArgs');

    // Load front images
    function loadFrontImages() {
        // Using Node.js fs module (Electron only)
        const fs = window.require ? window.require('fs') : require('fs');
        const path = window.require ? window.require('path') : require('path');
        
        const frontDir = path.resolve(__dirname, '../game/front');
        if (!fs.existsSync(frontDir)) {
            frontImagesGrid.innerHTML = '<p class="text-content-light/50 text-center p-4">No images found in front folder</p>';
            return;
        }

        const files = fs.readdirSync(frontDir).filter(file => 
            file.toLowerCase().endsWith('.png') || 
            file.toLowerCase().endsWith('.jpg') || 
            file.toLowerCase().endsWith('.jpeg')
        );

        if (files.length === 0) {
            frontImagesGrid.innerHTML = '<p class="text-content-light/50 text-center p-4">No images found in front folder</p>';
            return;
        }

        frontImagesGrid.innerHTML = files.map(file => {
            const filePath = `file://${path.join(frontDir, file)}`;
            return `
                <div class="card-grid-item">
                    <img src="${filePath}" alt="${file}" loading="lazy" />
                </div>
            `;
        }).join('');
    }

    // Clear front images
    clearFrontBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear all front images?')) {
            const fs = window.require ? window.require('fs') : require('fs');
            const path = window.require ? window.require('path') : require('path');
            const frontDir = path.resolve(__dirname, '../game/front');
            
            if (fs.existsSync(frontDir)) {
                const files = fs.readdirSync(frontDir);
                for (const file of files) {
                    if (file !== 'EMPTY.md') {
                        fs.unlinkSync(path.join(frontDir, file));
                    }
                }
            }
            loadFrontImages();
        }
    });

    // Create PDF
    createPdfBtn.addEventListener('click', function() {
        const args = [];
        if (onlyFrontsCheckbox.checked) args.push('--only_fronts');
        if (skip4Checkbox.checked) args.push('--skip', '4');
        if (pdfArgs.value.trim()) args.push(...pdfArgs.value.trim().split(' '));
        
        // Execute create_pdf.py with the arguments
        const { spawn } = window.require ? window.require('child_process') : require('child_process');
        const pythonProcess = spawn('python', ['create_pdf.py', ...args]);

        pythonProcess.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                alert('PDF created successfully!');
            } else {
                alert('Error creating PDF. Check the console for details.');
            }
        });
    });

    // Initial load
    loadFrontImages();
});