"""Build the separate, frame-one coil and electromagnet lesson."""

from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism.coil_chapter import build, DESTINATION

scene = build()
for area in bpy.context.window.screen.areas:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_perspective = "CAMERA"
        area.spaces.active.shading.type = "MATERIAL"
target = DESTINATION / "coil_reversal.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print(f"COIL_CASE_READY={target}", flush=True)
