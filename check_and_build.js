const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const HASH_FILE = '.python_build_hash';
const PYTHON_FILES = [
  'create_pdf.py',
  'utilities.py',
  'offset_pdf.py',
  'calibration.py',
  'clean_up.py'
];

function getFileHash(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return crypto.createHash('md5').update(content).digest('hex');
  } catch (e) {
    return null;
  }
}

function getCurrentHash() {
  const hashes = PYTHON_FILES.map(file => {
    const hash = getFileHash(file);
    return `${file}:${hash}`;
  }).join('|');
  return crypto.createHash('md5').update(hashes).digest('hex');
}

function getSavedHash() {
  try {
    return fs.readFileSync(HASH_FILE, 'utf8').trim();
  } catch (e) {
    return null;
  }
}

function saveHash(hash) {
  fs.writeFileSync(HASH_FILE, hash);
}

function buildAndCopy() {
  console.log('Python files changed. Building create_pdf...');
  
  const buildCmd = process.platform === 'win32' 
    ? 'build_create_pdf.bat' 
    : './build_create_pdf.sh';
  
  execSync(buildCmd, { stdio: 'inherit' });
  
  // Copy files
  const binDir = path.join('GUI', 'bin');
  fs.mkdirSync(binDir, { recursive: true });
  
  ['create_pdf', 'create_pdf.exe'].forEach(file => {
    try {
      fs.copyFileSync(file, path.join(binDir, file));
      console.log(`Copied ${file} to GUI/bin/`);
    } catch (e) {
      // File might not exist (e.g., .exe on Mac, no extension on Windows)
    }
  });
}

function main() {
  const currentHash = getCurrentHash();
  const savedHash = getSavedHash();
  
  // Check if executable exists
  const exeName = process.platform === 'win32' ? 'create_pdf.exe' : 'create_pdf';
  const exeExists = fs.existsSync(exeName);
  
  if (!exeExists) {
    console.log('Executable not found. Building...');
    buildAndCopy();
    saveHash(currentHash);
  } else if (currentHash !== savedHash) {
    buildAndCopy();
    saveHash(currentHash);
  } else {
    console.log('Python files unchanged. Skipping build.');
    console.log('Using existing create_pdf executable.');
  }
}

main();
