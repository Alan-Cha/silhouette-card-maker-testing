const { BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const frontDir = require('path').join(__dirname, '../game/front');
let watcher = null;

function startFrontDirWatcher() {
  if (watcher) return;
  const fs = require('fs');
  watcher = fs.watch(frontDir, { persistent: true }, (eventType, filename) => {
    if (filename && filename.endsWith('.png')) {
      BrowserWindow.getAllWindows().forEach(win => {
        win.webContents.send('front-images-changed');
      });
    }
  });
}
startFrontDirWatcher();
ipcMain.handle('clear-front-images', async () => {
  const dir = require('path').join(__dirname, '../game/front');
  const fs = require('fs');
  try {
    const files = await fs.promises.readdir(dir);
    for (const file of files) {
      if (file.endsWith('.png')) {
        await fs.promises.unlink(require('path').join(dir, file));
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
  const exePath = require('path').join(__dirname, '../create_pdf.exe');
  const cwd = require('path').join(__dirname, '..');
  const pyProcess = spawn(exePath, args, { shell: true, cwd });
    let stdout = '';
    let stderr = '';
    pyProcess.stdout.on('data', data => { stdout += data.toString(); });
    pyProcess.stderr.on('data', data => { stderr += data.toString(); });
    pyProcess.on('close', code => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(stderr || `Exited with code ${code}`);
      }
    });
  });
});

ipcMain.handle('get-front-images', async () => {
  const dir = path.join(__dirname, '../game/front');
  try {
    const files = await fs.promises.readdir(dir);
    return files.filter(f => f.endsWith('.png'));
  } catch (err) {
    return [];
  }
});
