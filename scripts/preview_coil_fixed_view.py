"""Render a fixed-camera layout from a loaded coil scene without saving over it."""
from pathlib import Path
import sys
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism.coil_fixed_view import arrange
from electromagnetism import coil_demo as demo

scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
arrange(scene)
scene.frame_set(24*24+1)
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 16
scene.render.use_sequencer = False
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(Path(bpy.data.filepath).parent / "fixed_layout_test.png")
bpy.ops.render.render(write_still=True)
