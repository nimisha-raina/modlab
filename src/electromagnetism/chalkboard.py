"""Reusable timed headings drawn on the physical laboratory chalkboard."""

import math
import bpy
from . import geometry as g


def show_between(obj, start, end, fps, duration):
    for frame, hidden in sorted({1: start > 0, max(1, round(start*fps)+1): False,
                                  min(round(end*fps)+1, round(duration*fps)+1): True}.items()):
        obj.hide_render = obj.hide_viewport = hidden
        obj.keyframe_insert("hide_render", frame=frame)
        obj.keyframe_insert("hide_viewport", frame=frame)


def build(scene, mats, cases):
    """Timed headings with one observation or a short list of summary points."""
    for obj in list(scene.objects):
        if obj.name.startswith("Chalkboard /"):
            bpy.data.objects.remove(obj, do_unlink=True)
    group = g.collection("Chalkboard | Demonstration headings", scene)
    for index, case in enumerate(cases, 1):
        if "points" in case:
            rows = [(case["case"], 5.8, .35), (case["heading"], 5.0, .62)]
            rows += [(body, 4.05-.8*i, .42) for i, body in enumerate(case["points"])]
        else:
            rows = [(case["case"], 5.45, .35), (case["heading"], 4.15, .67),
                    (case["observation"], 2.8, .38)]
        for body, z, size in rows:
            obj = g.text(f"Case {index} | {body}", body, (0, 11.08, z), size,
                         mats["ink_white"], group, rotation=(math.pi/2, 0, 0), align="CENTER")
            bpy.context.view_layer.update()
            if obj.dimensions.x > 12:
                obj.data.size *= 12/obj.dimensions.x
            show_between(obj, case["start"], case["end"], scene.render.fps,
                         scene.frame_end/scene.render.fps)
    return group
