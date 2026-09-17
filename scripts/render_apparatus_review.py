"""Render circuit and meter-detail stills for reviewing the apparatus design."""

from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism import current_demo as demo, stage
from electromagnetism.current_chapter import DESTINATION

scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
scene.frame_set(8*demo.FPS+1)
scene.render.engine = "BLENDER_EEVEE"
scene.render.use_sequencer = False
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 32
scene.render.image_settings.file_format = "PNG"
camera = scene.camera
camera.animation_data_clear()
for name, pose in [("circuit_rear_connected_ammeter", ((2, -14, 14), (0, .2, 1))),
                   ("ammeter_and_compass_detail", demo.CLOSE_VIEW)]:
    camera.location, target = pose
    stage.point_at(camera, target)
    bpy.context.view_layer.update()
    scene.render.filepath = str(DESTINATION / (name+".png"))
    bpy.ops.render.render(write_still=True)
    print(f"APPARATUS_REVIEW={scene.render.filepath}", flush=True)
