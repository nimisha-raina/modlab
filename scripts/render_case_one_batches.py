"""Resume cached pictures in short Blender processes, then encode both languages."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/01_compass_current/bilingual'
RANGES=[(start,min(start+192,1032)) for start in range(0,1032,192)]


def main(blender,languages):
    for language in languages:
        source=PART/f'case_one_{language}_source.blend'
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        cache=PART/'case_one_frames'/language
        # A stopped write must not be mistaken for a finished cached image.
        for path in cache.glob('*.png'):
            try:
                with Image.open(path) as image:image.verify()
            except (OSError,SyntaxError):
                path.rename(path.with_suffix('.invalid'))
        pieces=[]
        for start,end in RANGES:
            target=PART/f'{language}-frames-{start:04d}-{end:04d}.json'
            existing=json.loads(target.read_text()) if target.is_file() else None
            valid=existing and existing['source_sha256']==digest and all((PART/f['file']).is_file() for f in existing['frames'])
            if not valid:
                for attempt in range(3):
                    print(f'RENDER_BATCH={language} {start}:{end} attempt={attempt+1}',flush=True)
                    with (PART/f'render-{language}.log').open('a',encoding='utf-8') as log:
                        result=subprocess.run([blender,'--background',str(source),'--gpu-backend','opengl','--python-exit-code','1',
                            '--python',str(ROOT/'scripts/render_case_one_languages.py'),'--','--language',language,
                            '--start-frame',str(start),'--end-frame',str(end)],stdout=log,stderr=subprocess.STDOUT)
                    if result.returncode==0:break
                else:raise RuntimeError(f'Blender repeatedly failed in {language} frames {start}:{end}; inspect its render log.')
            piece=json.loads(target.read_text())
            assert piece['source_sha256']==digest
            assert len(piece['frames'])==end-start
            pieces.extend(piece['frames'])
        assert [f['time'] for f in pieces]==[i/12 for i in range(1032)]
        (PART/f'{language}-frames.json').write_text(json.dumps(dict(fps=12,frames=pieces,source_sha256=digest),indent=2)+'\n')
        subprocess.run([sys.executable,str(ROOT/'scripts/render_case_one_languages.py'),'--language',language,'--encode'],check=True)
    print('BILINGUAL_RENDER_COMPLETE',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender',default=shutil.which('blender'))
    parser.add_argument('--language',choices=('english','hinglish'),action='append')
    args=parser.parse_args()
    if not args.blender:parser.error('Provide the installed Blender executable using --blender.')
    main(args.blender,args.language or ('english','hinglish'))
