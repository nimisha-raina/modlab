"""Save a revised source and two packed narration variants; preserve earlier media."""
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from electromagnetism.coil_chapter import build
from electromagnetism.coil_narration import attach
PART=ROOT/'output/parts/02_coil_reversal/bilingual'
PART.mkdir(exist_ok=True)
scene=build()
scene['revision']='Contact-synchronized fields, 60-degree nail orbit, English/Hinglish H5P lesson'
scene['camera_layout']='Front overview with a temporary 60-degree right-hand nail view'
for area in bpy.context.window.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
source=PART/'coil_bilingual_source.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
for language in ('visual','english','hinglish'):
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene=bpy.context.scene
    timing=attach(scene,PART/f'audio_{language}')
    scene['narration_language']=language
    scene.frame_set(1)
    name='coil_visual_master.blend' if language=='visual' else f'coil_{language}.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(PART/name))
    print(f'BILINGUAL_SCENE={language} {timing["duration"]:.2f}s',flush=True)
