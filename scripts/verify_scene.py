"""Validate the saved revision in Blender, including all camera frames."""

from pathlib import Path
import sys
import bpy
import json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism.config import LESSON, SCENE_NAME, MICRO_ORIGIN, ELECTRON_HALF_LENGTH, ELECTRON_RADIUS
from electromagnetism.timing import map_time
from electromagnetism.field_layout import OVERVIEW_GUIDES

scene = bpy.data.scenes[SCENE_NAME]
bpy.context.window.scene = scene
timing = json.loads(scene["narration_timing"]) if "narration_timing" in scene else None
def frame_at(seconds):
    # Visibility was baked on the source's 24-fps grid before retiming.
    source_time = (LESSON.frame(seconds)-1)/LESSON.fps
    return round(map_time(source_time,timing)*LESSON.fps)+1
assert scene.frame_end == (timing["frames"] if timing else LESSON.last_frame)
assert scene.render.fps == LESSON.fps
assert scene.render.resolution_x / scene.render.resolution_y == 16/9
if timing:
    sounds = [strip for strip in scene.sequence_editor.strips if strip.type == "SOUND"]
    assert len(sounds) == len(timing["segments"]), "A narration section is missing."
    assert all(strip.sound.packed_file for strip in sounds), "Narration must travel with the .blend file."
assert len([obj for obj in scene.objects if obj.type == "CAMERA"]) == 1
assert not any(marker.camera for marker in scene.timeline_markers)
assert not any(obj.name.startswith("Selected sample") for obj in scene.objects)
electrons = [obj for obj in scene.objects if obj.name.startswith("Mobile electron")]
ions = [obj for obj in scene.objects if obj.name.startswith("Copper ion ")]
rings = sorted([obj for obj in scene.objects if obj.name.startswith("Magnetic concentric circle")
                and "guide_radius" in obj], key=lambda obj: obj.name)
overview_rings = [obj for obj in scene.objects if obj.name.startswith("Circuit field circle")
                  and "guide_radius" in obj]
assert len(electrons) == LESSON.electrons and len(ions) == 36
markers = [obj for obj in scene.objects if obj.name.startswith("Electron direction marker")]
assert not markers, "Electron markers belong only in the magnified copper model."
# Include the parent's scale in the world-space particle-size check.
# Hidden Blender objects can retain stale parent matrices. Measure the rendered
# marker size during the visible microscopic interval, at both current states.
for seconds in (LESSON.microscope_in+.5, LESSON.switch_on+1, LESSON.microscope_out-.1):
    scene.frame_set(frame_at(seconds))
    bpy.context.view_layer.update()
    for obj in electrons + markers:
        radius = max((obj.matrix_world.to_3x3() @ vertex.co).length for vertex in obj.data.vertices)
        assert abs(radius - ELECTRON_RADIUS) < 1e-6, (obj.name, seconds, radius)
assert len(rings) == 3
assert len(overview_rings) == len(OVERVIEW_GUIDES) == 6
assert [obj["guide_radius"] for obj in rings] == sorted(obj["guide_radius"] for obj in rings)
assert all(obj.location.length < 1e-8 for obj in rings)
assert all((obj.parent.location-Vector(MICRO_ORIGIN)).length < 1e-8 for obj in rings)
for ring in rings:
    assert all(abs(point.co.x) < 1e-8 for point in ring.data.splines[0].points)

scene.frame_set(frame_at(41))
bpy.context.view_layer.update()
for ring in overview_rings:
    assert not ring.hide_render and not ring.hide_viewport
    current = Vector(ring.parent["conventional_current"])
    transform = ring.matrix_world.to_3x3()
    assert all(abs(current.dot(transform @ point.co.xyz)) < 1e-6
               for point in ring.data.splines[0].points), "Field plane must be perpendicular to wire."
    arrows = [child for child in ring.parent.children if "chevron" in child.name]
    for arrow in arrows:
        wing_a, tip, wing_b = [transform @ p.co.xyz for p in arrow.data.splines[0].points]
        tangent = tip-(wing_a+wing_b)/2
        assert current.cross(tip).dot(tangent) > 0, "Field arrow violates the right-hand rule."

for seconds, visible in [(0, False), (LESSON.microscope_in-.1, False),
                         (LESSON.microscope_in+.1, True), (LESSON.microscope_out-.1, True),
                         (LESSON.microscope_out+.1, False), (41, False)]:
    scene.frame_set(frame_at(seconds))
    assert all(obj.hide_render == (not visible) and obj.hide_viewport == (not visible)
               for obj in electrons+ions), (seconds, "ions and electrons must be revealed together")

scene.frame_set(frame_at(LESSON.microscope_out+1.1))
assert all(obj.hide_render for obj in scene.objects
           if obj.name.startswith(("Copper cutaway shell", "Cutaway rim")))
cover = next(obj for obj in scene.objects if obj.name.startswith("Sample cover"))
blend = next(node for node in cover.data.materials[0].node_tree.nodes if node.type == "MIX_SHADER")
assert abs(blend.inputs[0].default_value) < 1e-6, "Wire surface must close early during pullback"

assert "Lesson title backplate" not in scene.objects
assert "Caption plate" not in scene.objects
assert not any(obj.type == "FONT" and ("FIELD NOTES" in obj.data.body or "LAB VIEW" in obj.data.body)
               for obj in scene.objects)
for obj in scene.objects:
    if "text_width" in obj:
        # Hidden objects can have stale evaluated dimensions in Blender.
        xs = [vertex.co.x for vertex in obj.data.vertices]
        width = (max(xs)-min(xs))*obj.scale.x
        assert abs(width - obj["text_width"] - obj["horizontal_padding"]) < 1e-5, obj.name

switch = bpy.data.objects["Switch hinge | animated"]
for seconds, expected in [(0, False), (LESSON.switch_on-.05, False), (LESSON.switch_on, True),
                          (LESSON.switch_off-1, True), (LESSON.switch_off, False), (47, False)]:
    scene.frame_set(frame_at(seconds))
    if expected:
        assert abs(switch.rotation_euler.y) < 0.0001
    if not expected:
        assert all(ring.hide_render and ring.hide_viewport for ring in rings+overview_rings)
for index, ring in enumerate(rings):
    start = frame_at(LESSON.field_reveal+index*0.55)
    scene.frame_set(start-1)
    assert ring.hide_render
    scene.frame_set(frame_at(LESSON.field_reveal+index*0.55+1))
    assert not ring.hide_render

# The moving camera must stay continuous, with the subject in frame throughout
# the critical magnified view and early pullback (before reframing the board).
previous = None
for frame in range(1, scene.frame_end+1):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    pose = scene.camera.matrix_world.copy()
    if previous is not None:
        step = (pose.translation-previous.translation).length
        distance = (pose.translation-Vector(MICRO_ORIGIN)).length
        assert step/max(distance,0.1) < 0.08, (frame, "camera discontinuity")
    previous = pose
    seconds = (frame-1)/LESSON.fps
    if map_time(LESSON.microscope_in,timing) <= seconds <= map_time(LESSON.zoom_out_end,timing):
        uv = world_to_camera_view(scene, scene.camera, Vector(MICRO_ORIGIN))
        assert 0.25 < uv.y < 0.75 and 0.2 < uv.x < 0.8, (frame, "sample lost during zoom")
    if seconds < map_time(LESSON.switch_on,timing):
        assert all(ring.hide_render for ring in rings+overview_rings)

scene.frame_set(frame_at(7))
before, ion_before = electrons[0].location.copy(), ions[0].location.copy()
scene.frame_set(frame_at(7.25))
assert (electrons[0].location-before).length > 0.01
assert (ions[0].location-ion_before).length > 0.005
for seconds in (7, 16, 24, 32, 41, 46):
    scene.frame_set(frame_at(seconds))
    bpy.context.view_layer.update()
    for electron in electrons:
        assert abs(electron.location.x) <= ELECTRON_HALF_LENGTH+0.001
    for ion in ions:
        assert (ion.location-Vector(ion["rest_position"])).length < 0.062
    for obj in scene.objects:
        if obj.type == "FONT" and obj.parent == scene.camera and not obj.hide_render:
            for corner in obj.bound_box:
                uv = world_to_camera_view(scene, scene.camera, obj.matrix_world @ Vector(corner))
                assert 0.015 <= uv.x <= 0.985 and 0.015 <= uv.y <= 0.985, (seconds, obj.name, tuple(uv))
assert not any(obj.animation_data and obj.animation_data.drivers for obj in scene.objects)
scene.frame_set(1)
print(f"PASS: {len(scene.objects)} objects; 3 close-up and 6 circuit guides; right-hand rule; "
      "continuous camera; field timing; shared particle visibility; compact label bounds.")
