"""Map every animated datablock onto measured, natural-speed tutor speech."""
import json
import bpy
from . import coil_demo as demo
from .config import ROOT
from .narration import curves
from .timing import map_time


def attach(scene, folder=None):
    folder = folder or ROOT / "output/parts/02_coil_reversal/audio_fixed"
    timing = json.loads((folder/"narration-timing.json").read_text(encoding="utf-8"))
    actions = set()
    for obj in scene.objects:
        data = obj.data
        blocks = [obj,data,getattr(data,"shape_keys",None)]
        blocks += [m.node_tree for m in getattr(data,"materials",[]) if m and m.use_nodes]
        for block in blocks:
            animation = getattr(block,"animation_data",None)
            if animation and animation.action:
                actions.add(animation.action)
    for action in actions:
        for curve in curves(action):
            for key in curve.keyframe_points:
                for point in (key.co,key.handle_left,key.handle_right):
                    point.x = map_time((point.x-1)/demo.FPS,timing)*demo.FPS+1
            curve.update()
    for marker in scene.timeline_markers:
        marker.frame = round(map_time((marker.frame-1)/demo.FPS,timing)*demo.FPS)+1
    scene.frame_end = timing["frames"]
    editor = scene.sequence_editor_create()
    strips = editor.strips
    voice = strips.new_sound("Indian-English tutor", str(folder/"narration.wav"),channel=1,frame_start=1)
    voice.sound.pack()
    scene.render.use_sequencer = False
    scene["narrator"] = timing["speaker"]
    scene["narration_timing"] = json.dumps(timing)
    scene["source_duration"] = demo.DURATION
    scene["audio_status"] = "Packed Indian male tutor narration, measured and synchronized."
    return timing
