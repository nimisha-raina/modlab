"""Check actual pointer visibility, camera timing and eight-second flow in Blender."""
import json
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from electromagnetism.config import SCENE_NAME
from electromagnetism.tutor_timing import lesson_time
from electromagnetism.camera_path import opening_pose

scene = bpy.data.scenes[SCENE_NAME]
bpy.context.window.scene = scene
assembly = bpy.data.scenes["00 - Opening and compass"]
lesson = json.loads((ROOT / "docs/first-case-narration.json").read_text(encoding="utf-8"))
assert assembly.frame_end == lesson["duration"] * 24
assert scene.frame_end == 48 * 24
assert scene["switch_on_frame"] == 23 * 24 + 1
assert lesson_time(22) - lesson_time(14) == 8
pointers = [o for o in scene.objects if o.get("tutor_component")]
assert {o["tutor_component"] for o in pointers} == {"battery", "switch", "copper wire", "resistor", "series ammeter"}
for name in {o["tutor_component"] for o in pointers}:
    obj = next(o for o in pointers if o["tutor_component"] == name)
    scene.frame_set(round((obj["cue_start"] + obj["cue_end"]) / 2 * 24)+1)
    bpy.context.view_layer.update()
    visible = {o["tutor_component"] for o in pointers if not o.hide_render}
    assert visible == {name}, (name, visible)
for source in (0, 3, 11, 14, 22, 32, 42):
    time = lesson_time(source)
    scene.frame_set(round(time * 24)+1)
    if time >= 10:
        assert all(o.hide_render for o in pointers)
    expected, _ = opening_pose(source)
    assert max(abs(a-b) for a,b in zip(scene.camera.location, expected)) < .002, (source, time)
chapter = next(s.scene for s in assembly.sequence_editor.strips if s.scene != scene)
bpy.context.window.scene = chapter
chapter.frame_set((74 - 48) * 24 + 1)
summary_pose = chapter.camera.matrix_world.copy()
chapter.frame_set(chapter.frame_end)
bpy.context.view_layer.update()
summary = [o for o in chapter.objects if o.type == "FONT" and o.data.body == "What we learned"]
assert len(summary) == 1 and not summary[0].hide_render
assert max(abs(a-b) for row_a, row_b in zip(summary_pose, chapter.camera.matrix_world)
           for a, b in zip(row_a, row_b)) < .002
report = {"duration":lesson["duration"], "opening_seconds":48, "zoom_seconds":8, "electron_flow_seconds":8,
          "final_summary_visible":True, "final_board_camera_stationary":True,
          "pointer_components":5, "switch_closure_seconds":23, "camera_stops":"passed"}
target = ROOT / "output/parts/01_compass_current/tutor-scene-verification.json"
target.write_text(json.dumps(report,indent=2)+"\n")
print("PASS: apparatus pointers, camera timing and unchanged electron-flow duration.")
