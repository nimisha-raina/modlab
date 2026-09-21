"""Prepare natural-speed narration and independent Case 1 language timelines."""
import json
import hashlib
import math
from pathlib import Path
import numpy as np
from prepare_coil_bilingual import normalize, save_wave

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/01_compass_current/bilingual'


def main():
    for language in ('english','hinglish'):
        lesson=json.loads((ROOT/f'docs/case-one-{language}.json').read_text(encoding='utf-8'))
        folder=PART/f'audio_{language}'
        provenance=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
        cursor=0
        clips=[]
        for i,section in enumerate(lesson['segments']):
            target=folder/f'narration_{i:02}.wav'
            record=provenance['clips'][target.with_suffix('.mp3').name]
            assert record['voice']==lesson['speaker']
            assert record['script_sha256']==hashlib.sha256((section.get('speech_text',section['text'])+lesson['description']).encode()).hexdigest()
            samples=normalize(target.with_suffix('.mp3'),target)
            seconds=len(samples)/44100
            window=math.ceil(max(section['end']-section['start'],seconds+.8)*12)/12
            section.update(target_start=cursor,target_end=cursor+window,speech_start=cursor+.2,
                           speech_seconds=seconds,audio=target.relative_to(ROOT).as_posix())
            cursor+=window
            clips.append(samples)
        lesson.update(duration=cursor,fps=24,frames=round(cursor*24),source_duration=86)
        track=np.zeros(round(cursor*44100),dtype='<i2')
        for section,samples in zip(lesson['segments'],clips):
            start=round(section['speech_start']*44100)
            track[start:start+len(samples)]=samples
        save_wave(folder/'narration.wav',track,44100)
        (folder/'narration-timing.json').write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{language}: {cursor:.3f} seconds',flush=True)


if __name__=='__main__':main()
