"""Validate the saved six-turn coil, cell reversal, poles and ammeter readings."""

import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from electromagnetism import coil_demo as demo
from ammeter_checks import check_ammeter

scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
assert scene.frame_start == 1 and scene.frame_end == demo.FPS*demo.DURATION
assert scene.render.fps == 24 and not scene.sequence_editor
wire = next(o for o in scene.objects if "turns" in o)
assert wire["turns"] == 6
assert not any(o.name.startswith(("Sample cover", "Mobile electron", "Copper ion")) for o in scene.objects)
leads = [o for o in scene.objects if o.get("rear_connection")]
assert len(leads) == 2
assert all(o.data.bevel_depth < .06 for o in leads)
assert len([o for o in scene.objects if "series_path" in o]) == 4
guides = [o for o in scene.objects if "field_guide" in o]
assert len(guides) == 6
assert wire["insulation"] == "enamel; spaced turns"
needle = next(o for o in scene.objects if o.name.startswith("Compass needle | north-seeking"))
switch = next(o for o in scene.objects if o.name.startswith("Switch hinge"))
cell = next(o for o in scene.objects if o.name.startswith("Cell | Reverse connections"))
for seconds, amps, left_pole in [(0, .5, None), (16, .5, "N"), (18, .5, None), (23.5, 0, None), (26, -.5, "S")]:
    scene.frame_set(round(seconds*demo.FPS)+1)
    bpy.context.view_layer.update()
    reading = [o for o in scene.objects if "amperes" in o and not o.hide_render]
    assert len(reading) == 1 and abs(reading[0]["amperes"]-amps) < 1e-6
    check_ammeter(scene, amps, framed=seconds in (16, 26))
    poles = [o for o in scene.objects if "pole" in o and not o.hide_render]
    assert len(poles) == (0 if left_pole is None else 2)
    if left_pole:
        assert next(o for o in poles if o["side"] == "left")["pole"] == left_pole
        assert all(not o.hide_render for o in guides)
    if amps == 0:
        assert all(o.hide_render for o in guides)
        assert abs(switch.rotation_euler.y-math.radians(-43)) < 1e-6
    else:
        assert abs(switch.rotation_euler.y) < 1e-6
    assert abs(needle.rotation_euler.z-demo.compass_angle(demo.coil_fraction(seconds), amps/.5)) < 1e-6
    assert (needle.location-Vector(demo.COMPASS_CENTER)).length < 1e-6
    if seconds >= 25:
        assert abs(cell.rotation_euler.z-math.pi) < 1e-6
    if seconds in (16, 26):
        for pole in poles:
            uv = world_to_camera_view(scene, scene.camera, pole.matrix_world.translation)
            assert .05 < uv.x < .95 and .05 < uv.y < .95
    if seconds in (0, 18):
        body = "A coil has north and south poles" if seconds == 0 else "Reverse current. Swap the poles."
        heading = next(o for o in scene.objects if o.type == "FONT" and o.data.body == body)
        assert not heading.hide_render
        for corner in heading.bound_box:
            uv = world_to_camera_view(scene, scene.camera, heading.matrix_world @ Vector(corner))
            assert .03 < uv.x < .97 and .03 < uv.y < .97
scene.frame_set(1)
print("PASS: frame-one 28-second case; six turns; closed field loops; +/-0.50 A; disconnected cell swap; exchanged poles; compass follows total field; concealed series connections.")
