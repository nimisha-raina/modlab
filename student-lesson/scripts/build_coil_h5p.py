"""Build two genuine H5P videos behind one opening narration choice."""
import json
import argparse
from pathlib import Path
import shutil
import zipfile
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_h5p import ROOT,DIST,LIBRARIES,read,write,defaults,question_interaction
PART=ROOT.parent/'output/parts/02_coil_reversal/bilingual'
if not (PART/'audio_english/narration-timing.json').is_file():
    PART=ROOT.parent/'archive/generated/parts/02_coil_reversal/bilingual'


def main(questions_only=False):
    (DIST/'coils').mkdir(exist_ok=True)
    player=ROOT/'node_modules/h5p-standalone'
    shutil.copytree(player/'dist',DIST/'vendor/h5p-player',dirs_exist_ok=True)
    shutil.copy2(player/'LICENSE',DIST/'vendor/h5p-player/LICENSE')
    configuration={}
    for language in ('english','hinglish'):
        folder=PART/f'audio_{language}'
        timing=read(folder/('narration-timing.json' if questions_only else 'video-timing.json'))
        questions=read(ROOT/f'content/coil/{language}.json')
        segments={s['id']:s for s in timing['segments']}
        times=[round(segments[q['after_id']]['target_end']-.3,3) for q in questions]
        for q,t in zip(questions,times):
            section=segments[q['after_id']]
            assert t>section['speech_start']+section['speech_seconds']+.1,'Question interrupts speech'
        package=DIST/f'h5p/coil-{language}'
        package.mkdir(parents=True,exist_ok=True)
        dependencies=[]
        for library in sorted(LIBRARIES.iterdir()):
            meta=read(library/'library.json')
            dependencies.append({k:meta[k] for k in ('machineName','majorVersion','minorVersion')})
            shutil.copytree(library,package/library.name,dirs_exist_ok=True)
        params=defaults(read(LIBRARIES/'H5P.InteractiveVideo-1.28/semantics.json'))
        params['interactiveVideo']={
            'video':{'files':[{'path':'videos/coil.mp4','mime':'video/mp4','copyright':{'license':'U'}}],
                'startScreenOptions':{'title':'Build an electromagnet' if language=='english' else 'आइए, विद्युत चुंबक बनाएँ','hideStartTitle':True,'shortStartDescription':'',
                'poster':{'path':'images/poster.jpg','mime':'image/jpeg','width':1280,'height':720,'copyright':{'license':'U'}}}},
            'assets':{'interactions':[question_interaction(q,i,times[i],len(questions)) for i,q in enumerate(questions)],
                'bookmarks':[],'endscreens':[]},
            'summary':{'task':{'library':'H5P.Summary 1.10','params':{'summaries':[]}},'displayAt':0}}
        params['override'].update(autoplay=False,loop=False,hasNoAutoPause=False,showSolutionButton='off',
            retryButton='on',showRewind10=True,preventSkippingMode='forward',deactivateSound=False)
        params['l10n'].update(defaultAdaptivitySeekLabel='Continue video' if language=='english' else 'आगे बढ़ें',
            requiresCompletionWarning='Try again before continuing.' if language=='english' else 'आगे बढ़ने से पहले फिर कोशिश कीजिए।')
        if language=='hinglish':
            ui=read(ROOT/'content/case-one/ui-hi.json')
            params['l10n'].update(ui['video'])
            for item in params['interactiveVideo']['assets']['interactions']:
                item['action']['params']['UI'].update(ui['question'])
        write(package/'content/content.json',params)
        write(package/'h5p.json',dict(title='Build an electromagnet — English' if language=='english' else 'आइए, विद्युत चुंबक बनाएँ — हिंदी',language='en' if language=='english' else 'hi',
            mainLibrary='H5P.InteractiveVideo',embedTypes=['iframe'],license='U',preloadedDependencies=dependencies))
        if questions_only:
            print(f'QUESTION_CONTENT_READY={language}')
            continue
        video=PART/timing['video_file']
        (package/'content/videos').mkdir(parents=True,exist_ok=True)
        (package/'content/images').mkdir(parents=True,exist_ok=True)
        shutil.copy2(video,package/'content/videos/coil.mp4')
        shutil.copy2(PART/f'poster-{language}.jpg',package/'content/images/poster.jpg')
        if language=='english':
            shutil.copy2(PART/'poster.jpg',DIST/'coils/poster.jpg')
        destination=ROOT.parent/f'output/share/coil-{language}.h5p'
        destination.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(package.rglob('*')):
                if path.is_file():archive.write(path,path.relative_to(package))
        configuration[language]=dict(path=f'../h5p/coil-{language}',duration=timing['duration'],questions=len(questions),
            speaker=timing['speaker'],captions=[[s['speech_start'],s['target_end'],s['text']] for s in timing['segments']])
        write(folder/'h5p-timing.json',dict(questions=[dict(id=q['id'],time=t) for q,t in zip(questions,times)],
            duration=timing['duration'],speaker=timing['speaker']))
        print(f'COIL_H5P={language}: {len(questions)} native questions')
    if not questions_only:
        (DIST/'coils/config.js').write_text('window.COIL_LESSONS = '+json.dumps(configuration,ensure_ascii=False)+';\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questions-only',action='store_true',help='Prepare native questions for scoring tests before media export')
    main(parser.parse_args().questions_only)
