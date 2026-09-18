"""Refresh the nail, switch labels and clips without rebuilding field traces."""

from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from electromagnetism import coil_demo as demo, coil_experiments
from electromagnetism.materials import make_materials

scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
for collection in list(scene.collection.children):
    if collection.name.startswith("Coil | Core and paper clip experiments"):
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(collection)
coil_experiments.build(scene,make_materials(),scene.camera)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("COIL_EXPERIMENTS_REFRESHED",flush=True)
