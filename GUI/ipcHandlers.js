const { ipcMain } = require('electron');
const { spawn } = require('child_process');
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
const fs = require('fs');
const path = require('path');

ipcMain.handle('get-front-images', async () => {
  const dir = path.join(__dirname, '../game/front');
  try {
    const files = await fs.promises.readdir(dir);
    return files.filter(f => f.endsWith('.png'));
  } catch (err) {
    return [];
  }
});
