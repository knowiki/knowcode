#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');

const platform = os.platform(); // 'win32', 'darwin', 'linux'
const arch = os.arch();         // 'x64', 'arm64'

const packageMap = {
  'win32-x64': 'knowcode-win32-x64',
  'darwin-arm64': 'knowcode-darwin-arm64',
  'linux-x64': 'knowcode-linux-x64'
};

const key = `${platform}-${arch}`;
const targetPackageName = packageMap[key];

if (!targetPackageName) {
  console.error(`Unsupported platform/architecture: ${key}`);
  process.exit(1);
}

try {
  const binaryName = platform === 'win32' ? 'know.exe' : 'know';
  const binaryPath = require.resolve(`${targetPackageName}/bin/${binaryName}`);

  // Set the environment variable to identify npm install method
  process.env.KNOWCODE_INSTALL_METHOD = 'npm';

  const result = spawnSync(binaryPath, process.argv.slice(2), {
    stdio: 'inherit',
    windowsHide: true
  });

  process.exit(result.status ?? 0);
} catch (err) {
  console.error(`Error: Failed to execute KnowCode CLI binary.
Details: ${err.message}
Please ensure that the platform-specific dependency '${targetPackageName}' is installed correctly.`);
  process.exit(1);
}
