const { BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const {
  getFrontDir,
  getBackDir,
  getOutputDir,
  getDecklistDir,
  getDoubleSidedDir
} = require('../shared/constants');
let watcher = null;

// Ensure all game directories exist on startup
function ensureDirectoriesExist() {
  const dirs = [getFrontDir(), getBackDir(), getOutputDir(), getDecklistDir(), getDoubleSidedDir()];
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`Created directory: ${dir}`);
    }
  });
}
ensureDirectoriesExist();

function startFrontDirWatcher() {
  if (watcher) return;
  const fs = require('fs');
  const frontDir = getFrontDir();
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
  const fs = require('fs');
  const frontDir = getFrontDir();
  try {
    const files = await fs.promises.readdir(frontDir);
    for (const file of files) {
      if (file.endsWith('.png')) {
        await fs.promises.unlink(require('path').join(frontDir, file));
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
    
  // Use platform-specific executable name in the packaged bin directory
  const executableName = process.platform === 'win32' ? 'create_pdf.exe' : 'create_pdf';
  // In production, use process.resourcesPath; in dev, use __dirname
  const isPackaged = require('electron').app.isPackaged;
  const baseDir = isPackaged
    ? require('path').join(process.resourcesPath, 'bin')
    : require('path').join(__dirname, '../bin');
  const exePath = require('path').join(baseDir, executableName);
  const cwd = baseDir;

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
      env: { 
        ...process.env,
        CARD_MAKER_FRONT_DIR: getFrontDir(),
        CARD_MAKER_BACK_DIR: getBackDir(),
        CARD_MAKER_OUTPUT_DIR: getOutputDir(),
        CARD_MAKER_DOUBLE_SIDED_DIR: getDoubleSidedDir()
      },
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

ipcMain.handle('run-md-to-pdf', async (event, options = {}) => {
  const markdownText = typeof options.markdownText === 'string' ? options.markdownText : '';
  const paperSize = options.paperSize || 'letter';
  const ppi = options.ppi || 300;
  const quality = options.quality || 75;
  const outputFileName = options.outputFileName || 'translatedTextBoxes.pdf';

  if (!markdownText.trim()) {
    throw new Error('Markdown input is empty.');
  }

  const inputPath = path.join(getDecklistDir(), 'entries.md');
  const outputPath = path.join(getOutputDir(), outputFileName);

  await fs.promises.mkdir(getDecklistDir(), { recursive: true });
  await fs.promises.mkdir(getOutputDir(), { recursive: true });
  await fs.promises.writeFile(inputPath, markdownText, 'utf8');

  const projectRoot = path.join(__dirname, '../..');
  const executableName = process.platform === 'win32'
    ? 'translated_text_boxes_to_pdf.exe'
    : 'translated_text_boxes_to_pdf';
  const isPackaged = require('electron').app.isPackaged;
  const baseDir = isPackaged
    ? path.join(process.resourcesPath, 'bin')
    : path.join(__dirname, '../bin');
  const exePath = path.join(baseDir, executableName);

  if (process.platform !== 'win32' && fs.existsSync(exePath)) {
    try {
      fs.chmodSync(exePath, '755');
    } catch (err) {
      console.error('Error setting executable permissions:', err);
    }
  }

  return new Promise((resolve, reject) => {
    const args = [
      '--input_path', inputPath,
      '--output_path', outputPath,
      '--paper_size', paperSize,
      '--ppi', String(ppi),
      '--quality', String(quality),
    ];

    let command = exePath;
    let commandArgs = args;
    let cwd = baseDir;

    // Fallback to Python script in development if the executable hasn't been built yet.
    if (!fs.existsSync(exePath)) {
      const scriptPath = path.join(projectRoot, 'translated_text_boxes_to_pdf.py');
      const pythonPath = process.platform === 'win32'
        ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
        : path.join(projectRoot, '.venv', 'bin', 'python');

      if (!fs.existsSync(scriptPath)) {
        reject(`Cannot find translated_text_boxes_to_pdf.py at ${scriptPath}`);
        return;
      }

      if (!fs.existsSync(pythonPath)) {
        reject(`Cannot find Python interpreter at ${pythonPath}`);
        return;
      }

      command = pythonPath;
      commandArgs = [scriptPath, ...args];
      cwd = projectRoot;
    }

    const mdProcess = spawn(command, commandArgs, {
      shell: false,
      cwd,
      env: {
        ...process.env,
        CARD_MAKER_DECKLIST_DIR: getDecklistDir(),
        CARD_MAKER_OUTPUT_DIR: getOutputDir(),
      },
    });

    let stdout = '';
    let stderr = '';
    mdProcess.stdout.on('data', data => { stdout += data.toString(); });
    mdProcess.stderr.on('data', data => { stderr += data.toString(); });
    mdProcess.on('error', (err) => {
      reject(`Failed to start markdown PDF process: ${err.message}`);
    });
    mdProcess.on('close', code => {
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
    const files = await fs.promises.readdir(getFrontDir());
    return files.filter(f => f.endsWith('.png'));
  } catch (err) {
    return [];
  }
});

// Example for other directories (add similar handlers as needed):
ipcMain.handle('get-back-images', async () => {
  try {
    const files = await fs.promises.readdir(getBackDir());
    return files.filter(f => f.endsWith('.png'));
  } catch (err) {
    return [];
  }
});
// Add similar logic for output, decklist, double_sided as needed
