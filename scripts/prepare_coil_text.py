"""Reuse shaped text rasterization with a separate Case 2 translation catalog."""
from pathlib import Path
import json
import re
import base64
import subprocess
from PIL import Image
import hashlib
ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/02_coil_reversal/bilingual'

def main():
    translations=json.loads((ROOT/'docs/coil-labels-hi.json').read_text(encoding='utf-8'))
    inventory=json.loads((PART/'text-inventory.json').read_text(encoding='utf-8'))
    folder=PART/'text'
    folder.mkdir(exist_ok=True)
    labels={};jobs=[]
    for body in sorted({o['text'] for o in inventory['coil']}):
        hindi=translations.get(body)
        if hindi is None:
            assert re.fullmatch(r'[+\-()\d.\sA°]+',body),f'Missing translation: {body}'
            hindi=body
        labels[body]={}
        for lang,text in (('english',body),('hinglish',hindi)):
            filename=hashlib.sha256(text.encode()).hexdigest()[:20]+'.png'
            labels[body][lang]={'text':text,'file':filename}
            if not (folder/filename).is_file() and not any(j['file']==filename for j in jobs):
                jobs.append(dict(text=text,file=filename))
    manifest=folder/'raster-jobs.json'
    manifest.write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
    if jobs:
        source=(ROOT/'scripts/rasterize_lesson_text.ps1').read_text(encoding='utf-8')
        command="& {\n"+source+"\n} -Manifest '"+str(manifest).replace("'","''")+"'"
        subprocess.run(['powershell.exe','-NoProfile','-STA','-EncodedCommand',base64.b64encode(command.encode('utf-16-le')).decode()],check=True)
    for variants in labels.values():
        for item in variants.values():
            path=folder/item['file']
            with Image.open(path) as picture:
                picture=picture.convert('RGBA')
                picture=picture.crop(picture.getchannel('A').getbbox())
                picture.save(path)
                item['width'],item['height']=picture.size
    (folder/'labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'COIL_LABELS_READY={len(labels)}')

if __name__=='__main__':main()
