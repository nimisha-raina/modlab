"""Prepare reusable shaped labels; English/Hindi share the same 3D anchors."""
import hashlib
import base64
import json
import re
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/01_compass_current/bilingual'


def main():
    translations=json.loads((ROOT/'docs/case-one-labels-hi.json').read_text(encoding='utf-8'))
    inventory=json.loads((PART/'text-inventory.json').read_text(encoding='utf-8'))
    bodies={o['text'] for entries in inventory.values() for o in entries}
    bodies.update(('Battery','Switch','Copper Wire','Resistor','Series Ammeter'))
    folder=PART/'text'
    folder.mkdir(exist_ok=True)
    jobs=[];labels={}
    for body in sorted(bodies):
        hindi=translations.get(body)
        if body.startswith('Deflection:'):hindi=body.replace('Deflection:','विक्षेप:')
        if hindi is None:
            assert re.fullmatch(r'[+\-()\d.\sA°]+',body),f'Missing translation: {body}'
            hindi=body
        labels[body]={}
        for lang,text in (('english',body),('hinglish',hindi)):
            filename=hashlib.sha256(text.encode()).hexdigest()[:20]+'.png'
            labels[body][lang]={'text':text,'file':filename}
            if not (folder/filename).is_file() and not any(j['file']==filename for j in jobs):
                jobs.append({'text':text,'file':filename})
    manifest=folder/'raster-jobs.json'
    manifest.write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
    if jobs:
        # Run this local, authored command without changing machine script policy.
        source=(ROOT/'scripts/rasterize_lesson_text.ps1').read_text(encoding='utf-8')
        command="& {\n"+source+"\n} -Manifest '"+str(manifest).replace("'","''")+"'"
        encoded=base64.b64encode(command.encode('utf-16-le')).decode('ascii')
        subprocess.run(['powershell.exe','-NoProfile','-STA','-EncodedCommand',encoded],check=True)
    for variants in labels.values():
        for item in variants.values():
            path=folder/item['file']
            with Image.open(path) as image:
                image=image.convert('RGBA')
                bounds=image.getchannel('A').getbbox()
                assert bounds,item['text']
                image=image.crop(bounds)
                image.save(path)
                item['width'],item['height']=image.size
    (folder/'labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'BILINGUAL_LABELS={len(labels)}')


if __name__=='__main__':main()
