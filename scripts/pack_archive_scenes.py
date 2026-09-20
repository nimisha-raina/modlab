"""Pack public scene copies without changing approved local masters."""
from pathlib import Path
import json
import shutil
import bpy

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/"archive"
preparation = json.loads((ARCHIVE/"preparation.json").read_text(encoding="utf-8"))
packed = {}
for job in preparation["blender_jobs"]:
    original = ROOT/"output"/job["path"]
    target = ARCHIVE/"generated"/job["path"]
    if job["original_sha256"] in packed:
        shutil.copy2(packed[job["original_sha256"]],target)
        print("REUSED_PACKED_SCENE="+job["path"],flush=True)
        continue
    bpy.ops.wm.open_mainfile(filepath=str(original))
    bpy.ops.file.pack_all()
    bpy.ops.file.make_paths_relative()
    for scene in bpy.data.scenes:
        scene.render.filepath = "/"*1023
        scene.render.filepath = "//renders/lesson_"
    # Fixed-size path buffers can retain bytes beyond a shorter replacement.
    # Clear them before storing portable paths in the public copy.
    for block in list(bpy.data.sounds)+list(bpy.data.images):
        if not block.filepath:
            continue
        relative = block.filepath
        if not relative.startswith("//"):
            relative = "//packed/"+Path(relative).name
        block.filepath = "/"*1023
        block.filepath = relative
    for screen in bpy.data.screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type=="FILE_BROWSER" and space.params:
                    space.params.directory = b"/"*1023
                    space.params.directory = b"//"
    for area in bpy.context.window.screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"
            area.spaces.active.shading.type = "MATERIAL"
    bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=True)
    packed[job["original_sha256"]] = target
    print("PACKED_ARCHIVE_SCENE="+job["path"],flush=True)
print("ARCHIVE_SCENES_PACKED",flush=True)
