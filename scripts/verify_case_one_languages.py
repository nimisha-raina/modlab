"""Validate complete scripts, encoded sound, frame mapping and quiz pauses."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import av
import numpy as np
from PIL import Image
from verify_coil_languages import normalize

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/01_compass_current/bilingual'


def scene_matches_render(scene, rendered_digest):
    """Accept the exact source or its checksum-verified portable archive copy."""
    actual = hashlib.sha256(scene.read_bytes()).hexdigest()
    if actual == rendered_digest:
        return True
    archive_manifest = ROOT/'archive/manifest.json'
    if not archive_manifest.is_file():
        return False
    relative = scene.relative_to(ROOT/'output').as_posix()
    entries = json.loads(archive_manifest.read_text(encoding='utf-8'))['files']
    return any(entry['path'] == relative
               and entry['sha256'] == actual
               and entry['original_sha256'] == rendered_digest
               for entry in entries)


def main(speech_only=False):
    report={}
    for language in ('english','hinglish'):
        script=json.loads((ROOT/f'docs/case-one-{language}.json').read_text(encoding='utf-8'))
        folder=PART/f'audio_{language}'
        coverage=[]
        for i,section in enumerate(script['segments']):
            words=[json.loads(line)['text'] for line in (folder/f'narration_{i:02}.words.jsonl').read_text(encoding='utf-8').splitlines()]
            ratio=difflib.SequenceMatcher(None,normalize(section.get('speech_text',section['text'])),normalize(' '.join(words)),autojunk=False).ratio()
            assert ratio>.95,(language,i,'Speech-service word coverage',ratio)
            coverage.append(ratio)
        report[language]=dict(speaker=script['speaker'],minimum_script_coverage=min(coverage),sections=len(coverage))
        if speech_only:continue
        timing=json.loads((folder/'video-timing.json').read_text(encoding='utf-8'))
        prepared=json.loads((folder/'narration-timing.json').read_text(encoding='utf-8'))
        assert timing['speaker']==script['speaker'],('Encoded voice is stale',language)
        assert timing['segments']==prepared['segments'],('Encoded timing is stale',language)
        video=PART/timing['video_file']
        subprocess.run([sys.executable,str(ROOT/'scripts/verify_narrated_video.py'),'--timing',str(folder/'video-timing.json'),
            '--video',str(video),'--questions',str(ROOT/f'student-lesson/content/case-one/{language}.json')],check=True,stdout=subprocess.DEVNULL)
        manifest=json.loads((PART/f'{language}-frames.json').read_text())
        source_scene=PART/f'case_one_{language}_source.blend'
        if source_scene.is_file():
            assert scene_matches_render(source_scene,manifest['source_sha256']),('Rendered scene is stale',language)
        samples={round((s['target_start']+s['target_end'])/2*12) for s in timing['segments']}
        previous=-1;errors=[]
        with av.open(video) as movie:
            assert movie.streams.video[0].codec_context.name=='h264'
            assert movie.streams.audio[0].codec_context.name=='aac'
            for count,frame in enumerate(movie.decode(video=0),1):
                assert (frame.width,frame.height)==(1280,720)
                assert frame.pts>previous
                previous=frame.pts
                if count-1 not in samples:continue
                time=(count-1)/12
                section=next(s for s in timing['segments'] if time<s['target_end'])
                source=section['start']+(time-section['target_start'])/(section['target_end']-section['target_start'])*(section['end']-section['start'])
                index=min(len(manifest['frames'])-1,round(source*12))
                picture=PART/manifest['frames'][index]['file']
                if not picture.is_file():continue  # Reproducible caches are optional in a fresh checkout.
                with Image.open(picture) as image:expected=np.asarray(image.convert('RGB'),dtype=float)
                error=float(np.mean(np.abs(frame.to_ndarray(format='rgb24').astype(float)-expected)))
                assert error<6,(language,count,'Encoded picture differs',error)
                errors.append(error)
        assert count==timing['video_frames']
        report[language].update(duration=timing['duration'],frames=count,fps=12,picture_samples_checked=len(errors),
            maximum_picture_mean_error=max(errors) if errors else None,
            video_sha256=hashlib.sha256(video.read_bytes()).hexdigest())
    assert report['english']['speaker']=='en-IN-PrabhatNeural'
    assert report['hinglish']['speaker']=='hi-IN-SwaraNeural'
    (PART/('speech-verification.json' if speech_only else 'language-verification.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--speech-only',action='store_true')
    main(parser.parse_args().speech_only)
