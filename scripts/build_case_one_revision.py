"""Derive a new Case 1 storyboard without modifying the frozen approved scene."""
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from electromagnetism import geometry as g, stage, case_one_revision as revision
from electromagnetism.config import SCENE_NAME
from electromagnetism.current_demo import SCENE_NAME as CHAPTER
from electromagnetism.chalkboard import show_between
from electromagnetism import case_one_presentation as presentation

PART=ROOT/'output/parts/01_compass_current/bilingual'
PART.mkdir(parents=True,exist_ok=True)
source=ROOT/'output/parts/frozen_case_01/opening_and_compass_tutor.blend'
approved='f177ebd25f4bd62ff1ee84da2ef3894e1af788de11180d003096695fc0a8b4fb'
accepted={approved}
manifest=ROOT/'archive/manifest.json'
if manifest.exists():
    accepted.update(e['sha256'] for e in json.loads(manifest.read_text())['files']
        if e['path']=='parts/frozen_case_01/opening_and_compass_tutor.blend' and e['original_sha256']==approved)
assert hashlib.sha256(source.read_bytes()).hexdigest() in accepted,'Use the preserved approved source scene.'
bpy.ops.wm.open_mainfile(filepath=str(source))
intro=bpy.data.scenes[SCENE_NAME]
chapter=bpy.data.scenes[CHAPTER]
mats=presentation.palette()
for scene in (intro,chapter):
    bpy.context.window.scene=scene
    presentation.restyle(scene,mats)
    group=g.collection('Conventional current | yellow direction arrows',scene)
    ink=mats['ink_gold']
    for i,(a,b) in enumerate(revision.conventional_segments()):
        objects=g.arrow(f'Conventional current {i+1}',a,b,.044,ink,group)
        presentation.travel_arrow(objects,a,b,38 if scene==intro else 0,48 if scene==intro else 24,48 if scene==intro else 38)
    if scene==intro:
        # Microscopic current arrow follows the conductor (-X), not the field circles.
        a=(.14,2.12,1.82);b=(-.14,2.12,1.82)
        presentation.travel_arrow(g.arrow('Conventional current | microscopic',a,b,.006,ink,group),a,b,23,38,48)
        label=g.face_camera(g.text('Current arrow legend','YELLOW / conventional current',
                 (0,2.12,1.90),.018,ink,group,align='CENTER'),scene.camera)
        show_between(label,23,38,24,48)
        scene.camera.animation_data_clear()
        for frame in range(1,48*24+1):
            scene.camera.location,target=revision.camera_pose((frame-1)/24)
            stage.point_at(scene.camera,target)
            scene.camera.keyframe_insert('location',frame=frame)
            scene.camera.keyframe_insert('rotation_euler',frame=frame)
        # The apparatus tour gets fresh measured-name cues in each language later.
        for obj in list(scene.objects):
            if obj.get('tutor_component'):
                bpy.data.objects.remove(obj,do_unlink=True)
    else:presentation.comparison(scene,mats)
    scene['revision']='Case 1 bilingual: moving current arrows, clear localized headings, before/now readings'
    scene.frame_set(1)
assembly=bpy.data.scenes['00 - Opening and compass']
assembly['revision']='Case 1 bilingual source storyboard'
bpy.context.window.scene=assembly
bpy.ops.wm.save_as_mainfile(filepath=str(PART/'case_one_source.blend'))
inventory={}
for scene in (intro,chapter):
    inventory[scene.name]=[dict(name=o.name,text=o.data.body) for o in scene.objects if o.type=='FONT']
(PART/'text-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('CASE_ONE_STORYBOARD_READY',flush=True)
