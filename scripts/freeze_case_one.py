"""Preserve the approved first-case movie and editable scene before later cases."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/parts/01_compass_current'
FROZEN = ROOT / 'output/parts/frozen_case_01'


def freeze():
    FROZEN.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ('opening_and_compass_narrated_720p.mp4', 'opening_and_compass_tutor.blend'):
        source, target = SOURCE / name, FROZEN / name
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise SystemExit(f'Frozen Case 1 differs; preserve its existing snapshot: {target.name}')
        else:
            shutil.copy2(source, target)
        files[name] = digest
    script = FROZEN / 'narration.json'
    if not script.exists():
        shutil.copy2(ROOT / 'docs/first-case-narration.json', script)
    manifest = {'case': 1, 'status': 'frozen', 'duration_seconds': 86,
                'fps': 12, 'files_sha256': files}
    (FROZEN / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('CASE_01_FROZEN: movie, editable scene and narration script preserved.')


if __name__ == '__main__':
    freeze()
