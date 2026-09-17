"""Apply the spoken tour timing and pointers to the reviewed connected scene."""
import json
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from electromagnetism.config import SCENE_NAME
from electromagnetism.narration import curves
from electromagnetism.tutor_timing import lesson_time
from electromagnetism.apparatus_highlights import build

PART = ROOT / "output/parts/01_compass_current"
bpy.ops.wm.open_mainfile(filepath=str(PART / "opening_and_compass.blend"))
scene = bpy.data.scenes[SCENE_NAME]
actions = set()
for obj in scene.objects:
    owners = [obj, obj.data, getattr(obj.data, "shape_keys", None)]
    owners += [m.node_tree for m in getattr(obj.data, "materials", []) if m]
    for owner in owners:
        animation = getattr(owner, "animation_data", None)
        if animation and animation.action:
            actions.add(animation.action)
for action in actions:
    for curve in curves(action):
        for key in curve.keyframe_points:
            for point in (key.co, key.handle_left, key.handle_right):
                point.x = lesson_time((point.x - 1) / 24) * 24 + 1
        curve.update()
for marker in scene.timeline_markers:
    marker.frame = round(lesson_time((marker.frame - 1) / 24) * 24) + 1
for key in ("switch_on_frame", "switch_off_frame"):
    scene[key] = round(lesson_time((scene[key] - 1) / 24) * 24) + 1
scene.frame_end = 48 * 24
scene["tutor_timing"] = "10s apparatus tour; 8s zoom; 5s atomic explanation; 8s drift; shorter overview."
scene["microscopic_flow_seconds"] = 8
lesson = json.loads((ROOT / "docs/first-case-narration.json").read_text(encoding="utf-8"))
build(scene, json.loads((ROOT / lesson["audio_directory"] / "apparatus-cues.json").read_text(encoding="utf-8")))
assembly = bpy.data.scenes["00 - Opening and compass"]
strips = assembly.sequence_editor.strips
opening = next(s for s in strips if s.scene == scene)
chapter = next(s for s in strips if s != opening)
opening.frame_final_end = 48 * 24 + 1
chapter.frame_start = 48 * 24 + 1
old_chapter_end = chapter.scene.frame_end
chapter.scene.frame_end = round((lesson["duration"] - 48) * 24)
# Keep the board visible throughout the added stationary summary hold.
for obj in chapter.scene.objects:
    animation = obj.animation_data
    if animation and animation.action:
        for curve in curves(animation.action):
            if curve.data_path in ("hide_render", "hide_viewport"):
                for key in curve.keyframe_points:
                    if round(key.co.x) == old_chapter_end + 1:
                        shift = chapter.scene.frame_end - old_chapter_end
                        for point in (key.co, key.handle_left, key.handle_right):
                            point.x += shift
                curve.update()
chapter.frame_final_end = lesson["duration"] * 24 + 1
assembly.frame_end = lesson["duration"] * 24
for marker in assembly.timeline_markers:
    marker.frame += 6 * 24
assembly["opening_seconds"] = 48
assembly["tutor_revision"] = 2
assembly["audio_status"] = "Final tutor narration is mixed into the movie separately."
bpy.context.window.scene = assembly
assembly.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(PART / "opening_and_compass_tutor.blend"))
print("TUTOR_SEQUENCE_READY", flush=True)
