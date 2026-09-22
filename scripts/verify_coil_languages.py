"""Check speech coverage, localized exported pictures and silent H5P pauses."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unicodedata
import av
import numpy as np

from verify_narrated_video import decode_audio,SAMPLE_RATE
ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/02_coil_reversal/bilingual'


def normalize(text):
    return ''.join(c for c in text.lower() if unicodedata.category(c)[0] in 'LMN')


def main(speech_only=False):
    report={}
    for language in ('english','hinglish'):
        script=json.loads((ROOT/f'docs/coil-narration-{language}.json').read_text(encoding='utf-8'))
        folder=PART/f'audio_{language}'
        coverage=[]
        for i,section in enumerate(script['segments']):
            words=[json.loads(line)['text'] for line in (folder/f'narration_{i:02}.words.jsonl').read_text(encoding='utf-8').splitlines()]
            ratio=difflib.SequenceMatcher(None,normalize(section.get('speech_text',section['text'])),normalize(' '.join(words)),autojunk=False).ratio()
            assert ratio>.95,(language,i,'Speech service omitted script words',ratio)
            coverage.append(ratio)
        report[language]=dict(speaker=script['speaker'],minimum_text_coverage=min(coverage),sections=len(coverage))
        if speech_only:continue
        timing=json.loads((folder/'video-timing.json').read_text(encoding='utf-8'))
        video=PART/timing['video_file']
        subprocess.run([sys.executable,str(ROOT/'scripts/verify_narrated_video.py'),'--timing',str(folder/'video-timing.json'),
            '--video',str(video),'--no-questions'],check=True,stdout=subprocess.DEVNULL)
        mapping=json.loads((folder/'picture-mapping.json').read_text(encoding='utf-8'))
        master=json.loads((PART/mapping['localized_manifest']).read_text())
        assert mapping['master_scene_sha256']==master['source_sha256']
        assert hashlib.sha256((PART/f'coil_{language}_source.blend').read_bytes()).hexdigest()==master['source_sha256']
        assert len(mapping['indices'])==timing['frames']
        samples={round((s['target_start']+s['target_end'])/2*timing['fps']) for s in timing['segments']}
        picture_errors=[]
        previous=-1
        with av.open(video) as movie:
            assert movie.streams.video[0].codec_context.name=='h264'
            assert movie.streams.audio[0].codec_context.name=='aac'
            for count,frame in enumerate(movie.decode(video=0),1):
                assert (frame.width,frame.height)==(1280,720)
                assert frame.pts>previous
                previous=frame.pts
                if count-1 in samples:
                    from PIL import Image
                    name=master['frames'][mapping['indices'][count-1]]['file']
                    with Image.open(PART/name) as picture:
                        expected=np.asarray(picture.convert('RGB'),dtype=float)
                    error=float(np.mean(np.abs(frame.to_ndarray(format='rgb24').astype(float)-expected)))
                    assert error<6,(language,count,'Encoded picture differs from mapped master',error)
                    picture_errors.append(error)
        assert count==timing['frames']
        audio=decode_audio(video)
        questions=json.loads((ROOT/f'student-lesson/content/coil/{language}.json').read_text(encoding='utf-8'))
        segments={s['id']:s for s in timing['segments']}
        pauses=[]
        for question in questions:
            segment=segments[question['after_id']]
            pause=segment['target_end']-.3
            assert pause>segment['speech_start']+segment['speech_seconds']+.1
            samples=audio[round((pause-.05)*SAMPLE_RATE):round((pause+.05)*SAMPLE_RATE)]
            assert np.sqrt(np.mean(samples**2))<.003
            pauses.append(round(pause,3))
        report[language].update(frames=count,duration=timing['duration'],fps=timing['fps'],pauses=pauses,
            maximum_picture_mean_error=max(picture_errors),
            video_sha256=hashlib.sha256(video.read_bytes()).hexdigest())
    assert report['english']['speaker']=='en-IN-PrabhatNeural'
    assert report['hinglish']['speaker']=='hi-IN-SwaraNeural'
    (PART/('speech-verification.json' if speech_only else 'media-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--speech-only',action='store_true')
    main(parser.parse_args().speech_only)
