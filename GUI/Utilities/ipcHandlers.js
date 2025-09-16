const { BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { FRONT_DIR } = require('../shared/constants');
let watcher = null;

function startFrontDirWatcher() {
  if (watcher) return;
  const fs = require('fs');
  watcher = fs.watch(FRONT_DIR, { persistent: true }, (eventType, filename) => {
    if (filename && filename.endsWith('.png')) {
      BrowserWindow.getAllWindows().forEach(win => {
        win.webContents.send('front-images-changed');
      });
    }
  });
}
startFrontDirWatcher();
ipcMain.handle('clear-front-images', async () => {
  const fs = require('fs');
  try {
    const files = await fs.promises.readdir(FRONT_DIR);
    for (const file of files) {
      if (file.endsWith('.png')) {
        await fs.promises.unlink(require('path').join(FRONT_DIR, file));
      }
    }
    return 'Front images cleared.';
  } catch (err) {
    return 'Error clearing images: ' + err;
  }
});
ipcMain.handle('run-create-pdf', async (event, argsString) => {
  return new Promise((resolve, reject) => {
    // Split argsString into array, respecting quotes
    const args = argsString.match(/(?:[^"\s]+|"[^"]*")+/g) || [];
    
    // Use platform-specific executable name
    const executableName = process.platform === 'win32' ? 'create_pdf.exe' : 'create_pdf';
    const exePath = require('path').join(__dirname, '../../', executableName);
    const cwd = require('path').join(__dirname, '../../');

    // Ensure the executable has proper permissions on Unix-like systems
    if (process.platform !== 'win32') {
      try {
        fs.chmodSync(exePath, '755');
      } catch (err) {
        console.error('Error setting executable permissions:', err);
      }
    }

    const pdfProcess = spawn(exePath, args, { 
      shell: false, // Set to false for better security
      cwd,
      env: { ...process.env }, // Pass through environment variables
    });

    let stdout = '';
    let stderr = '';
    pdfProcess.stdout.on('data', data => { stdout += data.toString(); });
    pdfProcess.stderr.on('data', data => { stderr += data.toString(); });
    pdfProcess.on('error', (err) => {
      reject(`Failed to start PDF process: ${err.message}`);
    });
    pdfProcess.on('close', code => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(stderr || `Exited with code ${code}`);
      }
    });
  });
});

ipcMain.handle('get-front-images', async () => {
  try {
    const files = await fs.promises.readdir(FRONT_DIR);
    return files.filter(f => f.endsWith('.png'));
  } catch (err) {
    return [];
  }
});
