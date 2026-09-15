"""Three concentric field guides, revealed only after electron drift starts."""

import math
import bpy
from . import geometry as g
from .config import LESSON, MICRO_ORIGIN
from .motion import visibility
from .camera_path import field_guide_scale


def build(scene, mats):
    group = g.collection("04 | Magnetic field guides", scene)
    root = bpy.data.objects.new("Field guides | illustrative radius", None)
    group.objects.link(root)
    root.location = MICRO_ORIGIN
    for frame in range(1, LESSON.last_frame+1):
        root.scale = (field_guide_scale((frame-1)/LESSON.fps),)*3
        root.keyframe_insert("scale", frame=frame)

    # Same centre, same perpendicular YZ plane, three different radii.
    # For conventional current -X, the tangent is (0, sin(a), -cos(a)).
    for index, radius in enumerate((1.20, 1.53, 1.86)):
        ring = g.ring_x(f"Magnetic concentric circle {index+1}", (0, 0, 0), radius,
                        0.024, mats["ink_mint"], group)
        ring["guide_radius"] = radius
        objects = [ring]
        for angle in (0.9, 3.8):
            # A broad chevron reads more clearly than a tiny 3D cone. Its tip
            # is at a smaller angle than both wings: the -X right-hand rule.
            tip = (0, radius*math.cos(angle), radius*math.sin(angle))
            back = angle+0.24
            wings = [(0, r*math.cos(back), r*math.sin(back))
                     for r in (radius-0.12, radius+0.12)]
            head = g.line(f"Circle {index+1} direction chevron", [wings[0], tip, wings[1]],
                          0.029, mats["ink_mint"], group)
            objects.append(head)
        start = LESSON.field_reveal + index*0.55
        for obj in objects:
            obj.parent = root
            visibility(obj, LESSON.frame(start), LESSON.frame(LESSON.switch_off)-1)
        for seconds, value in [(0, 0), (start, 0), (start+0.7, 1), (LESSON.duration, 1)]:
            ring.data.bevel_factor_end = value
            ring.data.keyframe_insert("bevel_factor_end", frame=LESSON.frame(seconds))
    return group
