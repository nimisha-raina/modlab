"""Verify the actual saved compass chapter, including fixed comparison geometry."""

import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from electromagnetism import current_demo as demo
from ammeter_checks import check_ammeter

scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
needle = scene.objects["Compass needle | north-seeking red tip"]
rings = [obj for obj in scene.objects if "current_level" in obj]
assert len(rings) == 16
assert scene.frame_end == demo.DURATION*demo.FPS
assert scene.render.fps == demo.FPS
assert not scene.sequence_editor, "The visual review must not reuse unrelated narration."
assert not any(obj.name.startswith("Mobile electron") for obj in scene.objects)
camera_comparisons = []
for seconds, current, count in [(0, 1, 8), (4, 1, 8), (8, 1, 8), (18, 2, 16), (23, 1, 8)]:
    scene.frame_set(round(seconds*demo.FPS)+1)
    bpy.context.view_layer.update()
    assert abs(needle["current_multiplier"]-current) < 1e-7
    point = demo.compass_position(seconds)
    assert abs(needle.rotation_euler.z-demo.compass_angle(current, point)) < 1e-6
    if not needle.hide_render:
        assert (needle.matrix_world.translation-Vector(point)).length < 1e-6
    assert sum(not obj.hide_render for obj in rings) == count
    switch = next(o for o in scene.objects if o.name.startswith("Switch hinge | animated"))
    assert (abs(switch.rotation_euler.y) < 1e-6) == (current > 0)
    readings = [o for o in scene.objects if "amperes" in o and not o.hide_render]
    assert len(readings) == 1 and abs(readings[0]["amperes"]-current*demo.REFERENCE_AMPS) < 1e-6
    check_ammeter(scene, current*demo.REFERENCE_AMPS, framed=seconds in (8, 18))
    if seconds in (8, 18):
        camera_comparisons.append(scene.camera.matrix_world.copy())
        projected = world_to_camera_view(scene, scene.camera, Vector(demo.COMPASS_CENTER))
        assert .2 < projected.x < .8 and .2 < projected.y < .8
        reading = readings[0]
        corners = [world_to_camera_view(scene, scene.camera, reading.matrix_world @ Vector(corner))
                   for corner in reading.bound_box]
        height = (max(p.y for p in corners)-min(p.y for p in corners))*scene.render.resolution_y
        assert height >= 10, ("Current reading too small", height)
        print(f"CURRENT_READING_HEIGHT_PIXELS={height:.1f} AT={seconds}s", flush=True)
        degrees = round(math.degrees(demo.NORTH_ANGLE-demo.compass_angle(current)))
        active = [o for o in scene.objects if "display_degrees" in o and not o.hide_render]
        assert len(active) == 1 and active[0]["display_degrees"] == degrees
        corners = [world_to_camera_view(scene, scene.camera, active[0].matrix_world @ Vector(c))
                   for c in active[0].bound_box]
        assert all(.02 < p.x < .98 and .02 < p.y < .98 for p in corners), "Deflection reading clipped"
        assert (max(p.y for p in corners)-min(p.y for p in corners))*scene.render.resolution_y >= 10
assert all(abs(a-b) < 1e-6 for row_a, row_b in zip(*camera_comparisons) for a, b in zip(row_a, row_b))

for seconds, heading in [(11, "More current. Stronger magnetic field."),
                         (28, "What we learned")]+[(28, body) for body in demo.SUMMARY_POINTS]:
    scene.frame_set(round(seconds*demo.FPS)+1)
    bpy.context.view_layer.update()
    labels = [obj for obj in scene.objects if obj.type == "FONT" and obj.data.body == heading]
    assert len(labels) == 1 and not labels[0].hide_render
    for corner in labels[0].bound_box:
        uv = world_to_camera_view(scene, scene.camera, labels[0].matrix_world @ Vector(corner))
        assert .03 < uv.x < .97 and .03 < uv.y < .97, (heading, tuple(uv))

previous_camera = None
previous_angle = None
for frame in range(1, scene.frame_end+1):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    position = scene.camera.matrix_world.translation.copy()
    if previous_camera is not None:
        assert (position-previous_camera).length < .6, "Camera jump"
        assert abs(needle.rotation_euler.z-previous_angle) < math.radians(5), "Needle jump"
    assert (needle.location-Vector(demo.COMPASS_CENTER)).length < 1e-6
    previous_camera, previous_angle = position, needle.rotation_euler.z
    seconds = (frame-1)/demo.FPS
    readings = [o for o in scene.objects if "amperes" in o and not o.hide_render]
    assert len(readings) == 1
    expected = round(demo.REFERENCE_AMPS*demo.current_at(seconds)*100)/100
    assert abs(readings[0]["amperes"]-expected) < 1e-6
    if not needle.hide_render:
        assert (needle.matrix_world.translation-Vector(demo.compass_position(seconds))).length < 1e-6
assert not any(o.name.startswith("Current setting card") for o in scene.objects)
assert not any(o.type == "FONT" and "CASE 1" in o.data.body.upper() for o in scene.objects)
scene.frame_set(round(demo.SUMMARY_START*demo.FPS)+1)
assert all(o.hide_render for o in scene.objects if o.type == "FONT" and
           o.data.body == "More current. Stronger magnetic field.")
assert any(o.type == "FONT" and o.data.body == "What we learned" and not o.hide_render for o in scene.objects)
assert len([o for o in scene.objects if "series_path" in o]) == 4
assert not any(o.name.split(".")[0] == "Copper conductor 1" for o in scene.objects)
scene.frame_set(1)
print("PASS: placed compass; measured needle angles; persistent circles at six locations; closed switch; "
      "series ammeter and readings; identical comparison framing; readable board heading; continuous motion.")
