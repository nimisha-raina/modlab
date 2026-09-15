"""Fit the entire Blender scene to speech, keeping one synchronized timeline."""
import json
import bpy
from .config import OUTPUT, ROOT, LESSON
from .timing import map_time


def curves(action):
    """Support Blender's layered actions as well as older action formats."""
    if hasattr(action, "fcurves"):
        yield from action.fcurves
    else:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves


def attach(scene):
    path = OUTPUT / "audio/narration-timing.json"
    if not path.exists():
        return None
    timing = json.loads(path.read_text())
    actions = set()
    for obj in scene.objects:
        if obj.animation_data and obj.animation_data.action:
            actions.add(obj.animation_data.action)
        if getattr(obj.data,"animation_data",None) and obj.data.animation_data.action:
            actions.add(obj.data.animation_data.action)
        for material in getattr(obj.data, "materials", []):
            if material and material.node_tree and material.node_tree.animation_data:
                action = material.node_tree.animation_data.action
                if action:
                    actions.add(action)
    for action in actions:
        for curve in curves(action):
            for key in curve.keyframe_points:
                for point in (key.co,key.handle_left,key.handle_right):
                    point.x = map_time((point.x-1)/LESSON.fps,timing)*LESSON.fps+1
            curve.update()
    for marker in scene.timeline_markers:
        marker.frame = round(map_time((marker.frame-1)/LESSON.fps,timing)*LESSON.fps)+1
    scene.frame_end = timing["frames"]
    editor = scene.sequence_editor_create()
    strips = editor.strips if hasattr(editor,"strips") else editor.sequences
    for index, clip in enumerate(timing["segments"]):
        strip = strips.new_sound(f"Narrator / {index+1:02}",str(ROOT/clip["audio"]),
                                 channel=1,frame_start=round((clip["target_start"]+.2)*LESSON.fps)+1)
        strip.volume = 1.0
        # Carry the voice inside the .blend when the project is moved or shared.
        strip.sound.pack()
    scene.render.use_sequencer = True
    scene["narration_timing"] = json.dumps(timing)
    scene["narrator"] = "Thoma / AI4Bharat Indic Parler-TTS / Indian English"
    scene["source_duration"] = LESSON.duration
    for name in ("switch_on_frame","switch_off_frame"):
        scene[name] = round(map_time((scene[name]-1)/LESSON.fps,timing)*LESSON.fps)+1
    return timing
