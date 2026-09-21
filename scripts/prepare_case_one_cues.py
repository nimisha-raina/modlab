"""Align apparatus highlights with measured words in each language."""
import json
import subprocess
import wave
from pathlib import Path
import imageio_ffmpeg
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/01_compass_current/bilingual'
for language in ('english','hinglish'):
    folder=PART/f'audio_{language}'
    timing=json.loads((folder/'narration-timing.json').read_text(encoding='utf-8'))
    section=timing['segments'][1]
    source=folder/'narration_01.mp3'
    raw=np.frombuffer(subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),
        '-ar','44100','-ac','1','-f','s16le','-']),dtype='<i2').astype(float)[::8]
    with wave.open(str(source.with_suffix('.wav'))) as audio:
        prepared=np.frombuffer(audio.readframes(audio.getnframes()),dtype='<i2').astype(float)[::8]
    probe=prepared[:44100//8]
    trim=int(np.argmax(np.correlate(raw[:len(probe)+44100//16],probe,mode='valid')))*8/44100
    words=[json.loads(line) for line in source.with_suffix('.words.jsonl').read_text().splitlines()]
    cues=[]
    names = [('battery','battery'),('switch','switch'),('copper wire','copper'),('resistor','resistor'),('series ammeter','ammeter')]
    if language=='hinglish':
        names = [('battery','बैटरी'),('switch','स्विच'),('copper wire','तांबे'),('resistor','प्रतिरोधक'),('series ammeter','ऐमीटर')]
    for component,keyword in names:
        word=next(w for w in words if w['text'].lower()==keyword)
        start=section['speech_start']+word['offset']/1e7-trim-.05
        source_start=3+(start-section['target_start'])/(section['target_end']-section['target_start'])*7
        cues.append(dict(component=component,start=source_start))
    for i,cue in enumerate(cues):
        cue['end']=cues[i+1]['start'] if i+1<len(cues) else 10
    (folder/'apparatus-cues.json').write_text(json.dumps(cues,indent=2)+'\n')
    print(f'APPARATUS_CUES_READY={language}')
