const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const lessonRoot = path.resolve(__dirname, '..');
const projectRoot = path.resolve(lessonRoot, '..');
const buildScript = path.join(__dirname, 'build_h5p.py');
const candidates = [];

if (process.env.PYTHON) {
  candidates.push([process.env.PYTHON, []]);
}
if (process.platform === 'win32') {
  candidates.push(
    [path.join(projectRoot, '.venv-media', 'Scripts', 'python.exe'), []],
    ['py', ['-3']],
    ['python', []],
    ['python3', []],
  );
} else {
  candidates.push(
    [path.join(projectRoot, '.venv-media', 'bin', 'python'), []],
    ['python3', []],
    ['python', []],
  );
}

for (const [command, prefix] of candidates) {
  if (path.isAbsolute(command) && !fs.existsSync(command)) continue;
  const result = spawnSync(command, [...prefix, buildScript], {
    cwd: lessonRoot,
    stdio: 'inherit',
  });
  if (!result.error) {
    if (result.status !== 0) process.exit(result.status ?? 1);
    const coil = spawnSync(command, [...prefix, path.join(__dirname, 'build_coil_h5p.py')], {
      cwd: lessonRoot, stdio: 'inherit',
    });
    if (coil.error) throw coil.error;
    process.exit(coil.status ?? 1);
  }
  if (!['ENOENT', 'EACCES', 'EPERM'].includes(result.error.code)) throw result.error;
}

console.error('Python 3 was not found. Set PYTHON or create the project media environment.');
process.exit(1);
