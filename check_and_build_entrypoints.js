const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const HASH_FILE = '.python_build_hash';

function getPythonFiles() {
  return fs.readdirSync('.')
    .filter(file => file.endsWith('.py'))
    .sort();
}

function hasMainEntrypoint(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return /if\s+__name__\s*==\s*['\"]__main__['\"]\s*:/.test(content);
  } catch (e) {
    return false;
  }
}

function getBuildTargets() {
  return getPythonFiles().filter(hasMainEntrypoint);
}

function executableNameFromScript(scriptName, windows) {
  const baseName = path.basename(scriptName, '.py');
  return windows ? `${baseName}.exe` : baseName;
}

function getFileHash(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return crypto.createHash('md5').update(content).digest('hex');
  } catch (e) {
    return null;
  }
}

function getCurrentHash() {
  const hashes = getPythonFiles().map(file => {
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
  console.log('Python entrypoint files changed. Building entrypoint executables...');
  
  const buildCmd = process.platform === 'win32' 
    ? 'build_entrypoints.bat' 
    : './build_entrypoints.sh';
  
  execSync(buildCmd, { stdio: 'inherit' });
  
  // Copy files
  const binDir = path.join('GUI', 'bin');
  fs.mkdirSync(binDir, { recursive: true });

  const targetScripts = getBuildTargets();
  const targetFiles = targetScripts.flatMap(script => {
    const baseName = path.basename(script, '.py');
    return [baseName, `${baseName}.exe`];
  });

  targetFiles.forEach(file => {
    try {
      fs.copyFileSync(file, path.join(binDir, file));
      console.log(`Copied ${file} to GUI/bin/`);
    } catch (e) {
      // File might not exist (e.g., .exe on Mac, no extension on Windows)
    }
  });
}

function main() {
  const targetScripts = getBuildTargets();
  if (targetScripts.length === 0) {
    console.log('No top-level Python entrypoint scripts found to build.');
    return;
  }

  const currentHash = getCurrentHash();
  const savedHash = getSavedHash();
  
  // Check if executables exist
  const exeNames = targetScripts.map(script => executableNameFromScript(script, process.platform === 'win32'));
  const exesExist = exeNames.every(file => fs.existsSync(file));
  
  if (!exesExist) {
    console.log('One or more executables not found. Building...');
    buildAndCopy();
    saveHash(currentHash);
  } else if (currentHash !== savedHash) {
    buildAndCopy();
    saveHash(currentHash);
  } else {
    console.log('Python files unchanged. Skipping build.');
    console.log('Using existing Python executables.');
  }
}

main();
