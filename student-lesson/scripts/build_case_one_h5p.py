"""Publish localized Case 1 videos with two compact native H5P questions."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile
from build_h5p import ROOT,DIST,LIBRARIES,read,write,defaults,question_interaction

PART=ROOT.parent/'output/parts/01_compass_current/bilingual'
if not (PART/'audio_english/narration-timing.json').is_file():
    PART=ROOT.parent/'archive/generated/parts/01_compass_current/bilingual'


def main(questions_only=False,languages=('english','hinglish')):
    configuration={}
    for language in languages:
        folder=PART/f'audio_{language}'
        timing=read(folder/('narration-timing.json' if questions_only else 'video-timing.json'))
        if not questions_only:
            prepared=read(folder/'narration-timing.json')
            assert timing['segments']==prepared['segments'] and timing['speaker']==prepared['speaker'], 'Render the current narration before publishing.'
        questions=read(ROOT/f'content/case-one/{language}.json')
        sections={s['id']:s for s in timing['segments']}
        times=[round(sections[q['after_id']]['target_end']-.3,3) for q in questions]
        for question,time in zip(questions,times):
            section=sections[question['after_id']]
            assert time>section['speech_start']+section['speech_seconds']+.1,'Question interrupts narration'
        package=DIST/f'h5p/case-one-{language}'
        package.mkdir(parents=True,exist_ok=True)
        dependencies=[]
        for library in sorted(LIBRARIES.iterdir()):
            meta=read(library/'library.json')
            dependencies.append({k:meta[k] for k in ('machineName','majorVersion','minorVersion')})
            shutil.copytree(library,package/library.name,dirs_exist_ok=True)
        params=defaults(read(LIBRARIES/'H5P.InteractiveVideo-1.28/semantics.json'))
        params['interactiveVideo']={
            'video':{'files':[{'path':'videos/lesson.mp4','mime':'video/mp4','copyright':{'license':'U'}}],
                'startScreenOptions':{'title':'Electricity makes magnetism','hideStartTitle':True,'shortStartDescription':'',
                'poster':{'path':'images/poster.jpg','mime':'image/jpeg','width':1280,'height':720,'copyright':{'license':'U'}}}},
            'assets':{'interactions':[question_interaction(q,i,times[i],len(questions)) for i,q in enumerate(questions)],'bookmarks':[],'endscreens':[]},
            'summary':{'task':{'library':'H5P.Summary 1.10','params':{'summaries':[]}},'displayAt':0}}
        params['override'].update(autoplay=False,loop=False,hasNoAutoPause=False,showSolutionButton='off',retryButton='on',
            showRewind10=True,preventSkippingMode='forward',deactivateSound=False)
        params['l10n'].update(defaultAdaptivitySeekLabel='Continue video' if language=='english' else 'आगे बढ़ें',
            requiresCompletionWarning='Try again before continuing.' if language=='english' else 'आगे बढ़ने से पहले फिर कोशिश कीजिए।')
        if language=='hinglish':
            ui=read(ROOT/'content/case-one/ui-hi.json')
            params['l10n'].update(ui['video'])
            params['interactiveVideo']['video']['startScreenOptions']['title']='विद्युत धारा का चुंबकीय प्रभाव'
            for item in params['interactiveVideo']['assets']['interactions']:
                item['action']['params']['UI'].update(ui['question'])
        write(package/'content/content.json',params)
        write(package/'h5p.json',dict(title='Electricity makes magnetism — English' if language=='english' else 'विद्युत धारा का चुंबकीय प्रभाव — हिंदी',language='en' if language=='english' else 'hi',
            mainLibrary='H5P.InteractiveVideo',embedTypes=['iframe'],license='U',preloadedDependencies=dependencies))
        if questions_only:continue
        (package/'content/videos').mkdir(parents=True,exist_ok=True)
        (package/'content/images').mkdir(parents=True,exist_ok=True)
        shutil.copy2(PART/timing['video_file'],package/'content/videos/lesson.mp4')
        shutil.copy2(PART/f'poster-{language}.jpg',package/'content/images/poster.jpg')
        if language=='english':shutil.copy2(PART/'poster-english.jpg',DIST/'case-one-poster.jpg')
        target=ROOT.parent/f'output/share/case-one-{language}.h5p'
        target.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(package.rglob('*')):
                if path.is_file():archive.write(path,path.relative_to(package))
        configuration[language]=dict(path=f'./h5p/case-one-{language}',duration=timing['duration'],questions=len(questions),speaker=timing['speaker'],
            captions=[[s['speech_start'],s['target_end'],s['text']] for s in timing['segments']])
        write(folder/'h5p-timing.json',dict(questions=[dict(id=q['id'],time=t) for q,t in zip(questions,times)],duration=timing['duration']))
        print(f'CASE_ONE_H5P_READY={language}',flush=True)
    if not questions_only:
        (DIST/'case-one-config.js').write_text('window.CASE_ONE_LESSONS = '+json.dumps(configuration,ensure_ascii=False)+';\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questions-only',action='store_true')
    parser.add_argument('--language',choices=('english','hinglish'),help='Build one language for local authoring; publication always builds both')
    args=parser.parse_args()
    main(args.questions_only,(args.language,) if args.language else ('english','hinglish'))
