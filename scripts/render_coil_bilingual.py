"""Render one shared picture track, then mux English and Hinglish narration."""
import argparse
import json
from pathlib import Path
import sys
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'output/parts/02_coil_reversal/bilingual'


def frame_indices(timing,master,fps):
    """Map equivalent explanation progress to the nearest master picture."""
    sections={s['id']:s for s in master['segments']}
    index=0
    result=[]
    for frame in range(round(timing['duration']*fps)):
        seconds=frame/fps
        while index+1<len(timing['segments']) and seconds>=timing['segments'][index]['target_end']:
            index+=1
        section=timing['segments'][index]
        reference=sections[section['id']]
        fraction=(seconds-section['target_start'])/(section['target_end']-section['target_start'])
        target=reference['target_start']+fraction*(reference['target_end']-reference['target_start'])
        result.append(min(round(target*fps),round(master['duration']*fps)-1))
    return result


def encode():
    import imageio_ffmpeg
    from PIL import Image
    report=json.loads((PART/'render.json').read_text(encoding='utf-8'))
    master=json.loads((PART/'audio_visual/narration-timing.json').read_text(encoding='utf-8'))
    with Image.open(PART/'bilingual_frames'/report['sequence'][0]) as picture:
        picture.convert('RGB').save(PART/'poster.jpg',quality=90)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    for language in ('english','hinglish'):
        folder=PART/f'audio_{language}'
        timing=json.loads((folder/'narration-timing.json').read_text(encoding='utf-8'))
        indices=frame_indices(timing,master,report['fps'])
        target=PART/f'coil_{language}_720p.mp4'
        temporary=target.with_name('encoding_'+target.name)
        process=subprocess.Popen([ffmpeg,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
            '-s','1280x720','-r',str(report['fps']),'-i','-','-i',str(folder/'narration.wav'),
            '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
            '-movflags','+faststart',str(temporary)],stdin=subprocess.PIPE)
        previous,data=None,None
        for index in indices:
            name=report['sequence'][index]
            if name!=previous:
                with Image.open(PART/'bilingual_frames'/name) as picture:data=picture.convert('RGB').tobytes()
                previous=name
            process.stdin.write(data)
        process.stdin.close()
        if process.wait():raise RuntimeError('Video encoding failed')
        temporary.replace(target)
        timing.update(fps=report['fps'],frames=len(indices),video_file=target.name)
        (folder/'video-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'picture-mapping.json').write_text(json.dumps(dict(master_scene_sha256=report['source_sha256'],
            master_fps=report['fps'],indices=indices,maximum_master_quantization_seconds=.5/report['fps']),indent=2)+'\n',encoding='utf-8')
        print(f'BILINGUAL_VIDEO={target.name}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stills',nargs='*',type=float,default=[])
    parser.add_argument('--encode',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ([] if 'bpy' in sys.modules else sys.argv[1:]))
    if args.encode:encode()
    else:
        sys.path.insert(0,str(ROOT/'scripts'))
        import render_coil_fixed_view as renderer
        renderer.PART=PART
        renderer.CACHE=PART/'bilingual_frames'
        renderer.REPORT=PART/'render.json'
        renderer.render(args.stills,6)
