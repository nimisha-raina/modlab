"""Prepare two natural-speed voices against one shared visual timeline."""
import hashlib
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import wave
import imageio_ffmpeg
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/02_coil_reversal/bilingual'
LANGUAGES=('english','hinglish')


def normalize(source,target,rate=44100):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-i',str(source),
        '-af','silenceremove=start_periods=1:start_duration=0.06:start_threshold=-55dB:start_silence=0.03,areverse,'
        'silenceremove=start_periods=1:start_duration=0.06:start_threshold=-55dB:start_silence=0.15,areverse,'
        'highpass=f=60,loudnorm=I=-18:TP=-2:LRA=7','-ar',str(rate),'-ac','1',str(target)],check=True)
    with wave.open(str(target),'rb') as f:
        data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)
    for n,start in ((round(.02*rate),True),(round(.10*rate),False)):
        envelope=(1-np.cos(np.linspace(0,np.pi,n)))/2
        if start:data[:n]*=envelope
        else:data[-n:]*=envelope[::-1]
    data=np.rint(np.clip(data,-32768,32767)).astype('<i2')
    save_wave(target,data,rate)
    return data


def save_wave(path,data,rate):
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'))
        f.writeframes(data.tobytes())


def main(keep_master=False):
    rate=44100
    lessons={language:json.loads((ROOT/f'docs/coil-narration-{language}.json').read_text(encoding='utf-8')) for language in LANGUAGES}
    samples={language:[] for language in LANGUAGES}
    for language,lesson in lessons.items():
        folder=ROOT/lesson['audio_directory']
        provenance=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
        for i,section in enumerate(lesson['segments']):
            source=folder/f'narration_{i:02}.mp3'
            digest=hashlib.sha256((section.get('speech_text',section['text'])+lesson['description']).encode()).hexdigest()
            assert provenance['clips'][source.name]['script_sha256']==digest
            assert provenance['clips'][source.name]['voice']==lesson['speaker']
            target=source.with_suffix('.wav')
            data=normalize(source,target)
            samples[language].append(data)
            section.update(audio=target.relative_to(ROOT).as_posix(),speech_seconds=len(data)/rate)
    assert lessons['english']['speaker']=='en-IN-PrabhatNeural'
    assert lessons['hinglish']['speaker']=='hi-IN-SwaraNeural'
    cursor=0.
    for i,source in enumerate(lessons['english']['segments']):
        window=math.ceil(max(source['end']-source['start'],
            *[lesson['segments'][i]['speech_seconds']+.8 for lesson in lessons.values()])*6)/6
        if source['id']=='applications':
            assert window<=11,'Shorten the applications line to fit 11 seconds.'
            window=11.
        for language,lesson in lessons.items():
            section=lesson['segments'][i]
            assert section['id']==source['id']
            section.update(target_start=cursor,target_end=cursor+window,speech_start=cursor+.25)
        print(f"{source['id']}: {window:.2f}s",flush=True)
        cursor+=window
    # Keep a longest-window master for rendering once. Each delivered language
    # has its own shorter holds; no speech is accelerated to fit the pictures.
    visual=copy.deepcopy(lessons['english'])
    visual.update(language='visual',audio_directory='output/parts/02_coil_reversal/bilingual/audio_visual')
    if not keep_master:
        lessons['visual']=visual
        samples['visual']=samples['english']
    else:
        saved=json.loads((PART/'audio_visual/narration-timing.json').read_text(encoding='utf-8'))
        assert [(s['id'],s['start'],s['end']) for s in saved['segments']]==[(s['id'],s['start'],s['end']) for s in visual['segments']], 'Changed storyboard needs a new visual master'
    for language,lesson in lessons.items():
        folder=ROOT/lesson['audio_directory']
        folder.mkdir(exist_ok=True)
        if language!='visual':
            cursor=0.
            for section in lesson['segments']:
                window=11 if section['id']=='applications' else math.ceil(max(section['end']-section['start'],section['speech_seconds']+.8)*6)/6
                section.update(target_start=cursor,target_end=cursor+window,speech_start=cursor+.25)
                cursor+=window
        else:
            cursor=lesson['segments'][-1]['target_end']
        lesson.update(duration=cursor,frames=round(cursor*24),fps=24,source_duration=136)
        track=np.zeros(round(cursor*rate),dtype='<i2')
        for section,data in zip(lesson['segments'],samples[language]):
            start=round(section['speech_start']*rate)
            track[start:start+len(data)]=data
        save_wave(folder/'narration.wav',track,rate)
        (folder/'narration-timing.json').write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'BILINGUAL_TIMELINE={language} {cursor:.3f}s')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keep-master',action='store_true',help='Retain the existing picture timeline for speech-only edits')
    main(parser.parse_args().keep_master)
