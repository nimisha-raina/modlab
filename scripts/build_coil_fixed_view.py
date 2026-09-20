"""Build the fixed-camera Case 2 source and packed narrated scene separately."""
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from electromagnetism.coil_chapter import build, DESTINATION
from electromagnetism.coil_narration import attach

scene = build()
for area in bpy.context.window.screen.areas:
    if area.type=="VIEW_3D":
        area.spaces.active.region_3d.view_perspective = "CAMERA"
        area.spaces.active.shading.type = "MATERIAL"
bpy.ops.wm.save_as_mainfile(filepath=str(DESTINATION/"coil_fixed_view_source.blend"))
timing = attach(scene)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(DESTINATION/"coil_fixed_view_narrated.blend"))
print(f"FIXED_VIEW_READY={timing['duration']} seconds",flush=True)
