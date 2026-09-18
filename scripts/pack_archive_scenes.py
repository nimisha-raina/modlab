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
    bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=True)
    packed[job["original_sha256"]] = target
    print("PACKED_ARCHIVE_SCENE="+job["path"],flush=True)
print("ARCHIVE_SCENES_PACKED",flush=True)
