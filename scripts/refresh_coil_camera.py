"""Apply a camera-only timing/layout update to the saved Case 2 scene."""
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from electromagnetism import coil_demo as demo, coil_camera
scene = bpy.data.scenes[demo.SCENE_NAME]
assert scene.frame_end==demo.DURATION*demo.FPS,"Rebuild after changing lesson duration"
coil_camera.animate(scene)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("COIL_CAMERA_REFRESHED",flush=True)
