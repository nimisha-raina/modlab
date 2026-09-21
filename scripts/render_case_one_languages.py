"""Render localized Case 1 pictures once, then fit each natural-speed narration."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
PART=ROOT/'output/parts/01_compass_current/bilingual'
SCENES=('01 - Electricity makes magnetism','02 - Compass and current')
FPS=12


def render(language,stills=False,start=0,end=86*FPS,cache_folder=None):
    import bpy
    from render_complete_preview import visible_state
    folder=PART/'case_one_frames'/(cache_folder or language)
    folder.mkdir(parents=True,exist_ok=True)
    revision=hashlib.sha256((PART/f'case_one_{language}_source.blend').read_bytes()).hexdigest()
    frames=[]
    times=[0,5,20,24,28,30,36,55,66,78] if stills else [i/FPS for i in range(start,end)]
    rendered=0
    for count,seconds in enumerate(times):
        index=0 if seconds<48 else 1
        scene=bpy.data.scenes[SCENES[index]]
        bpy.context.window.scene=scene
        scene.render.engine='BLENDER_EEVEE'
        scene.render.use_sequencer=False
        scene.render.resolution_x,scene.render.resolution_y=1280,720
        scene.render.resolution_percentage=100
        scene.eevee.taa_render_samples=8
        scene.render.image_settings.file_format='PNG'
        scene.frame_set(round((seconds-(48 if index else 0))*24)+1)
        bpy.context.view_layer.update()
        digest=hashlib.sha256(repr((revision,index,visible_state(scene))).encode()).hexdigest()[:24]
        image=folder/f'{digest}.png'
        if not image.is_file():
            scene.render.filepath=str(image)
            bpy.ops.render.render(write_still=True)
            rendered+=1
        frames.append(dict(time=seconds,file=image.relative_to(PART).as_posix()))
        if count%12==0 or stills:print(f'CASE_ONE_FRAME={language} {count+1}/{len(times)} source={seconds:.2f} new={rendered}',flush=True)
    suffix='stills' if stills else 'frames' if start==0 and end==86*FPS else f'frames-{start:04d}-{end:04d}'
    (PART/f'{language}-{suffix}.json').write_text(json.dumps(dict(fps=FPS,frames=frames,source_sha256=revision),indent=2)+'\n')
    print(f'CASE_ONE_RENDER_READY={language}',flush=True)


def encode(language):
    import subprocess
    import imageio_ffmpeg
    from PIL import Image
    timing=json.loads((PART/f'audio_{language}/narration-timing.json').read_text(encoding='utf-8'))
    manifest=json.loads((PART/f'{language}-frames.json').read_text())
    video=PART/f'case_one_{language}_720p.mp4'
    command=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s','1280x720','-r',str(FPS),'-i','-','-i',str(PART/f'audio_{language}/narration.wav'),
        '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(video)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    previous=raw=None
    count=round(timing['duration']*FPS)
    for frame in range(count):
        time=frame/FPS
        clip=next(s for s in timing['segments'] if time<s['target_end'])
        source=clip['start']+(time-clip['target_start'])/(clip['target_end']-clip['target_start'])*(clip['end']-clip['start'])
        index=min(len(manifest['frames'])-1,max(0,round(source*FPS)))
        path=PART/manifest['frames'][index]['file']
        if path!=previous:
            with Image.open(path) as image:raw=image.convert('RGB').tobytes()
            previous=path
        process.stdin.write(raw)
    process.stdin.close()
    assert process.wait()==0
    timing.update(video_file=video.name,video_fps=FPS,video_frames=count)
    (PART/f'audio_{language}/video-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with Image.open(PART/manifest['frames'][0]['file']) as image:image.convert('RGB').save(PART/f'poster-{language}.jpg',quality=92)
    print(f'CASE_ONE_VIDEO_READY={language} seconds={timing["duration"]:.3f}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('english','hinglish'),required=True)
    parser.add_argument('--stills',action='store_true')
    parser.add_argument('--encode',action='store_true')
    parser.add_argument('--start-frame',type=int,default=0)
    parser.add_argument('--end-frame',type=int,default=86*FPS)
    parser.add_argument('--cache-folder',help='Optional isolated cache folder for a parallel frame range')
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    args=parser.parse_args(argv)
    assert 0<=args.start_frame<args.end_frame<=86*FPS
    encode(args.language) if args.encode else render(args.language,args.stills,args.start_frame,args.end_frame,args.cache_folder)
