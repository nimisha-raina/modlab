"""Refresh Case 2's timed board content without rebuilding its apparatus."""
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from electromagnetism import coil_demo as demo, coil_board
from electromagnetism.config import PALETTE

scene = bpy.data.scenes[demo.SCENE_NAME]
assert scene.frame_end == demo.DURATION*demo.FPS, "Rebuild for timeline changes"
bpy.context.window.scene = scene
mats = {"ink_"+name:bpy.data.materials["EM / ink / "+name] for name in PALETTE
        if "EM / ink / "+name in bpy.data.materials}
coil_board.build(scene,mats)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("COIL_BOARD_REFRESHED",flush=True)
