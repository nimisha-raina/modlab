"""Render localized source pictures in resumable batches and mux natural speech."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/02_coil_reversal/bilingual'
FPS=12

def render(language,start,end,stills=False):
    import bpy
    sys.path.insert(0,str(ROOT/'scripts'))
    from render_coil_review import fingerprint
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.use_sequencer=False
    scene.render.resolution_x,scene.render.resolution_y=1280,720
    scene.render.resolution_percentage=100
    scene.eevee.taa_render_samples=8
    scene.render.image_settings.file_format='PNG'
    revision=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    folder=PART/'localized_frames'/language
    folder.mkdir(parents=True,exist_ok=True)
    times=[0,8,24,34,61,76,88,94,108,120,130] if stills else [i/FPS for i in range(start,end)]
    frames=[]
    for i,seconds in enumerate(times):
        scene.frame_set(round(seconds*24)+1)
        bpy.context.view_layer.update()
        digest=fingerprint(scene,revision)
        image=folder/f'{digest}.png'
        if not image.is_file():
            scene.render.filepath=str(image)
            bpy.ops.render.render(write_still=True)
        frames.append(dict(time=seconds,file=image.relative_to(PART).as_posix()))
        if i%12==0 or stills:print(f'COIL_FRAME={language} {i+1}/{len(times)} source={seconds:.2f}',flush=True)
    suffix='stills' if stills else f'frames-{start:04d}-{end:04d}'
    (PART/f'{language}-{suffix}.json').write_text(json.dumps(dict(fps=FPS,frames=frames,source_sha256=revision),indent=2)+'\n')

def encode(language):
    import imageio_ffmpeg
    from PIL import Image
    timing=json.loads((PART/f'audio_{language}/narration-timing.json').read_text(encoding='utf-8'))
    manifest=json.loads((PART/f'{language}-frames.json').read_text())
    target=PART/f'coil_{language}_720p.mp4'
    temporary=target.with_name('encoding_'+target.name)
    process=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s','1280x720','-r',str(FPS),'-i','-','-i',str(PART/f'audio_{language}/narration.wav'),
        '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(temporary)],stdin=subprocess.PIPE)
    indices=[];previous=raw=None
    for frame in range(round(timing['duration']*FPS)):
        time=frame/FPS
        clip=next(s for s in timing['segments'] if time<s['target_end'])
        source=clip['start']+(time-clip['target_start'])/(clip['target_end']-clip['target_start'])*(clip['end']-clip['start'])
        index=min(len(manifest['frames'])-1,max(0,round(source*FPS)))
        indices.append(index)
        path=PART/manifest['frames'][index]['file']
        if path!=previous:
            with Image.open(path) as picture:raw=picture.convert('RGB').tobytes()
            previous=path
        process.stdin.write(raw)
    process.stdin.close()
    if process.wait():raise RuntimeError('Encoding failed')
    temporary.replace(target)
    timing.update(fps=FPS,frames=len(indices),video_file=target.name)
    folder=PART/f'audio_{language}'
    (folder/'video-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'picture-mapping.json').write_text(json.dumps(dict(master_scene_sha256=manifest['source_sha256'],
        master_fps=FPS,indices=indices,localized_manifest=f'{language}-frames.json'),indent=2)+'\n')
    with Image.open(PART/manifest['frames'][0]['file']) as picture:
        picture.convert('RGB').save(PART/f'poster-{language}.jpg',quality=92)
        if language=='english':picture.convert('RGB').save(PART/'poster.jpg',quality=92)
    print(f'COIL_VIDEO_READY={language} {timing["duration"]:.2f}s',flush=True)

def batches(blender,language):
    from PIL import Image
    source=PART/f'coil_{language}_source.blend'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    for path in (PART/'localized_frames'/language).glob('*.png'):
        try:
            with Image.open(path) as image:image.verify()
        except (OSError,SyntaxError):path.rename(path.with_suffix('.invalid'))
    complete=[]
    for start in range(0,136*FPS,192):
        end=min(start+192,136*FPS)
        manifest=PART/f'{language}-frames-{start:04d}-{end:04d}.json'
        saved=json.loads(manifest.read_text()) if manifest.is_file() else None
        if not(saved and saved['source_sha256']==digest and all((PART/f['file']).is_file() for f in saved['frames'])):
            with (PART/f'render-{language}.log').open('a',encoding='utf-8') as log:
                subprocess.run([blender,'--background',str(source),'--gpu-backend','opengl','--python-exit-code','1',
                    '--python',str(Path(__file__)),'--','--language',language,'--start',str(start),'--end',str(end)],
                    stdout=log,stderr=subprocess.STDOUT,check=True)
        saved=json.loads(manifest.read_text())
        assert len(saved['frames'])==end-start
        complete.extend(saved['frames'])
        print(f'COIL_BATCH={language} {end}/{136*FPS}',flush=True)
    (PART/f'{language}-frames.json').write_text(json.dumps(dict(fps=FPS,frames=complete,source_sha256=digest),indent=2)+'\n')
    encode(language)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('english','hinglish'),required=True)
    parser.add_argument('--stills',action='store_true')
    parser.add_argument('--encode',action='store_true')
    parser.add_argument('--blender')
    parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--end',type=int,default=136*FPS)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    if args.blender:batches(args.blender,args.language)
    elif args.encode:encode(args.language)
    else:render(args.language,args.start,args.end,args.stills)
