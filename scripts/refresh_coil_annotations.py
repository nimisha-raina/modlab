"""Apply current coil-caption layout and compass-reading clearance in place."""
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from electromagnetism import coil_demo as demo, coil_annotations
from electromagnetism.config import PALETTE

scene = bpy.data.scenes[demo.SCENE_NAME]
assert scene.frame_end==demo.DURATION*demo.FPS, "Rebuild for timeline changes"
bpy.context.window.scene = scene
for obj in list(scene.objects):
    if obj.get("field_annotation") or obj.name.startswith(("Coil field direction caption",
          "Coil outside field direction caption","Clear axial field direction","Clear outside field direction")):
        bpy.data.objects.remove(obj,do_unlink=True)
    elif "display_degrees" in obj:
        obj.location.y = demo.CENTER[1]-1.65
        obj.location.z = .13
        obj.data.size = .22
mats = {"ink_"+name:bpy.data.materials["EM / ink / "+name] for name in PALETTE
        if "EM / ink / "+name in bpy.data.materials}
group = next(c for c in scene.collection.children if c.name.startswith("Coil | Combining magnetic fields"))
coil_annotations.build(scene,mats,scene.camera,group)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("COIL_ANNOTATIONS_REFRESHED",flush=True)
