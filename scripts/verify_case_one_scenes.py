"""Compare narrated Blender edits with their localized source poses and visibility."""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from electromagnetism.timing import map_time
from electromagnetism.case_one_revision import orbit_pose
from electromagnetism.config import MICRO_ORIGIN

PART=ROOT/'output/parts/01_compass_current/bilingual'
SCENES=('01 - Electricity makes magnetism','02 - Compass and current')
PROBES=(0,5.5,18.5,20.5,22,24,28,30,34,39,45,49,55,60,64,66,70,78,84)


def capture(timing=None):
    snapshots=[]
    for seconds in PROBES:
        offset=0 if seconds<48 else 48
        scene=bpy.data.scenes[SCENES[bool(offset)]]
        bpy.context.window.scene=scene
        local=seconds-offset if timing is None else map_time(seconds,timing)-map_time(offset,timing)
        frame=local*24+1
        scene.frame_set(math.floor(frame),subframe=frame%1)
        bpy.context.view_layer.update()
        snapshot={}
        for obj in scene.objects:
            if obj.hide_render:continue
            snapshot[obj.name]=tuple(v for row in obj.matrix_world for v in row)
        snapshots.append(snapshot)
        if offset==0:
            arrows=[o for o in scene.objects if 'current_vector' in o and not o.hide_render]
            assert bool(arrows)==(seconds>=23),('Switch and current arrows disagree',seconds,[o.name for o in arrows])
        elif 53<=seconds<72:
            mirrors={o['instrument_mirror']:o['measurement'] for o in scene.objects
                     if o.get('instrument_mirror') and not o.hide_render}
            originals={key:o[key] for o in scene.objects for key in ('amperes','display_degrees')
                       if key in o and not o.hide_render}
            assert mirrors==originals,('Comparison differs from physical instruments',seconds,mirrors,originals)
    return snapshots


def main(language):
    timing=json.loads((PART/f'audio_{language}/narration-timing.json').read_text(encoding='utf-8'))
    bpy.ops.wm.open_mainfile(filepath=str(PART/f'case_one_{language}_source.blend'))
    source=capture()
    scene=bpy.data.scenes[SCENES[0]]
    moving=[o for o in scene.objects if o.get('travelling_current_arrow') and 'microscopic' not in o.name]
    scene.frame_set(42*24+1)
    before={o.name:o.location.copy() for o in moving}
    scene.frame_set(42*24+13)
    for obj in moving:
        delta=obj.location-before[obj.name]
        dot=sum(a*b for a,b in zip(delta,obj['current_vector']))
        assert dot>.03,('Current arrow does not advance along the conductor',obj.name)
    if language=='hinglish':
        translations=json.loads((ROOT/'docs/case-one-labels-hi.json').read_text(encoding='utf-8'))
        for name in SCENES:
            for obj in bpy.data.scenes[name].objects:
                if obj.type=='FONT':
                    assert translations.get(obj.data.body,obj.data.body)==obj.data.body,('Untranslated visible text',obj.name)
    bpy.ops.wm.open_mainfile(filepath=str(PART/f'case_one_{language}.blend'))
    actual=capture(timing)
    maximum=0
    for seconds,before,after in zip(PROBES,source,actual):
        assert before.keys()==after.keys(),('Visibility differs',seconds,sorted(before.keys()^after.keys()))
        error=max(abs(a-b) for name in before for a,b in zip(before[name],after[name]))
        assert error<.02,('Retimed pose differs',seconds,error)
        maximum=max(maximum,error)
    assembly=bpy.data.scenes['00 - Opening and compass']
    assert assembly.frame_end==timing['frames']
    sound=[s for s in assembly.sequence_editor.strips if s.type=='SOUND']
    assert len(sound)==1 and sound[0].sound.packed_file
    assert assembly['narrator']==('hi-IN-SwaraNeural' if language=='hinglish' else 'hi-IN-MadhurNeural')
    scene=bpy.data.scenes[SCENES[0]]
    assert scene['switch_on_frame']==round(map_time(23,timing)*24)+1
    position=orbit_pose()[0]
    angle=math.degrees(math.atan2(position[0]-MICRO_ORIGIN[0],MICRO_ORIGIN[1]-position[1]))
    assert abs(angle-60)<1e-6
    for image in bpy.data.images:
        if image.source=='FILE' and image.users:assert image.packed_file,image.name
    report=dict(language=language,probes=len(PROBES),maximum_pose_error=maximum,camera_azimuth_degrees=angle,
        packed_narration=True,packed_localized_labels=True,visibility_matches_source=True,
        live_readings_match_instruments=True,current_arrows_advance_along_wire=True)
    (PART/f'{language}-scene-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('english','hinglish'),required=True)
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).language)
