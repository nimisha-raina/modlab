"""Build the Case 2 source and text inventory before shaping language variants."""
from pathlib import Path
import json
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from electromagnetism.coil_chapter import build
PART=ROOT/'output/parts/02_coil_reversal/bilingual'
PART.mkdir(exist_ok=True)
scene=build()
scene['revision']='Contact-synchronized fields, 60-degree nail orbit, English/Hindi H5P lesson'
scene['camera_layout']='Front overview with a temporary 60-degree right-hand nail view'
for area in bpy.context.window.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
source=PART/'coil_bilingual_source.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
inventory={'coil':[{'text':o.data.body,'name':o.name} for o in scene.objects if o.type=='FONT']}
(PART/'text-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('COIL_SOURCE_READY: shape labels, then run build_coil_language_scene.py',flush=True)
