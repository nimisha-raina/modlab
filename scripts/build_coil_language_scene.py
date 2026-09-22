"""Localize the Case 2 storyboard, then attach each measured narration."""
import json
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'src'))
import build_case_one_language_scene as lettering
from electromagnetism.coil_narration import attach
from electromagnetism import chalkboard, coil_demo
from electromagnetism import coil_arrow_motion
from electromagnetism.narration import curves
PART=ROOT/'output/parts/02_coil_reversal/bilingual'
lettering.PART=PART
labels=json.loads((PART/'text/labels.json').read_text(encoding='utf-8'))
for language in ('english','hinglish'):
    bpy.ops.wm.open_mainfile(filepath=str(PART/'coil_bilingual_source.blend'))
    scene=bpy.context.scene
    scene['narration_language']=language
    scene['revision']='Clear comparisons, travelling current, Prabhat English / Swara Hindi'
    coil_arrow_motion.bake(scene)
    for obj in scene.objects:
        if obj.get('application_highlight'):
            # Put the bright ring in front of its thicker dark contrast halo.
            for point in obj.data.splines[0].points:point.co.y=10.90
        if obj.get('magnetic_field_arrow') or (obj.type=='MESH' and obj.get('field_annotation')):
            obj.scale.x*=.7
            obj.scale.y*=.7
        if obj.type=='FONT' and obj.data.body.startswith('Before: air core'):
            obj.animation_data_clear()
            chalkboard.show_between(obj,74,80,24,coil_demo.DURATION)
    if language=='hinglish':
        bpy.context.view_layer.update()
        for obj in list(scene.objects):
            if obj.type!='FONT':continue
            item=labels[obj.data.body][language]
            if item['text']==obj.data.body:continue
            # Give Hindi phrases room without changing their apparatus anchors.
            if obj.name.startswith('Case ') or 'Compass before' in obj.name:
                obj['localized_width']=12.
            lettering.localized_plane(obj,item)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(PART/f'coil_{language}_source.blend'))
    timing=attach(scene,PART/f'audio_{language}')
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(PART/f'coil_{language}.blend'))
    print(f'COIL_LANGUAGE_READY={language} {timing["duration"]}',flush=True)
