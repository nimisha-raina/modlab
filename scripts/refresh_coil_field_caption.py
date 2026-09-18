"""Clarify the axial field label and render only affected draft states.

This bounded revision changes the two internal-field captions only. Other
reviewed frames retain their original render. Run after render_coil_review.py
has completed, then encode again with the media environment.
"""
import hashlib
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from electromagnetism import coil_demo as demo
from render_coil_review import PART,FRAMES,fingerprint

scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
captions = [o for o in scene.objects if o.name.startswith("Coil field direction caption")]
assert len(captions)==2 and all(o.type=="FONT" for o in captions)
needs_save = any(o.data.body!=demo.INSIDE_FIELD_LABEL for o in captions)
for caption in captions:
    assert caption.data.body in ("FIELD DIRECTION","FIELD INSIDE COIL",demo.INSIDE_FIELD_LABEL)
    caption.data.body = demo.INSIDE_FIELD_LABEL
scene.frame_set(1)
if needs_save:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
with Path(bpy.data.filepath).open("rb") as source:
    digest = hashlib.file_digest(source,"sha256").hexdigest()
report_path = PART/"extended-render.json"
report = json.loads(report_path.read_text())
assert len(report["sequence"])==demo.DURATION*report["fps"]
scene.render.resolution_x,scene.render.resolution_y = report["width"],report["height"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.eevee.taa_render_samples = 8
changed = set()
for index in range(len(report["sequence"])):
    scene.frame_set(round(index*demo.FPS/report["fps"])+1)
    bpy.context.view_layer.update()
    if all(o.hide_render for o in captions):
        continue
    key = fingerprint(scene,digest)
    path = FRAMES/(key+".png")
    if key not in changed:
        if not path.is_file():
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
        changed.add(key)
        if len(changed)%20==0:
            print(f"INTERNAL_FIELD_CAPTION_STATES={len(changed)}",flush=True)
    report["sequence"][index] = path.name
report["caption"] = demo.INSIDE_FIELD_LABEL
report["caption_updated_states"] = len(changed)
report["unique_states"] = len(set(report["sequence"]))
report_path.write_text(json.dumps(report,indent=2)+"\n")
print("INTERNAL_FIELD_CAPTION_REVIEW_READY",flush=True)
