"""Concentric close-up guides and local guides distributed around the circuit."""

import math
import bpy
from mathutils import Vector
from . import geometry as g
from .config import LESSON, MICRO_ORIGIN
from .motion import visibility
from .camera_path import field_guide_scale
from .field_layout import OVERVIEW_GUIDES, OVERVIEW_RADIUS, SAMPLE_RADII


def guide(group, mats, name, radius, thickness):
    """Circle and two arrowheads for conventional current along local -X."""
    ring = g.ring_x(name, (0, 0, 0), radius, thickness, mats["ink_mint"], group)
    ring["guide_radius"] = radius
    objects = [ring]
    for angle in (0.9, 3.8):
        tip = (0, radius*math.cos(angle), radius*math.sin(angle))
        back = angle+0.24
        wings = [(0, r*math.cos(back), r*math.sin(back))
                 for r in (radius-thickness*5, radius+thickness*5)]
        head = g.line(name + " direction chevron", [wings[0], tip, wings[1]],
                      thickness*1.2, mats["ink_mint"], group)
        objects.append(head)
    return ring, objects


def reveal(ring, objects, parent, start, end):
    for obj in objects:
        obj.parent = parent
        visibility(obj, LESSON.frame(start), LESSON.frame(end)-1)
    for seconds, value in [(0, 0), (start, 0), (start+0.7, 1), (LESSON.duration, 1)]:
        ring.data.bevel_factor_end = value
        ring.data.keyframe_insert("bevel_factor_end", frame=LESSON.frame(seconds))


def build(scene, mats, overview_guides=OVERVIEW_GUIDES):
    group = g.collection("04 | Magnetic field guides", scene)
    root = bpy.data.objects.new("Field guides | illustrative radius", None)
    group.objects.link(root)
    root.location = MICRO_ORIGIN
    for frame in range(1, LESSON.last_frame+1):
        root.scale = (field_guide_scale((frame-1)/LESSON.fps),)*3
        root.keyframe_insert("scale", frame=frame)

    # Same centre, same perpendicular YZ plane, three different radii.
    # For conventional current -X, the tangent is (0, sin(a), -cos(a)).
    for index, radius in enumerate(SAMPLE_RADII):
        ring, objects = guide(group, mats, f"Magnetic concentric circle {index+1}", radius, .024)
        start = LESSON.field_reveal + index*0.55
        reveal(ring, objects, root, start, LESSON.switch_off)

    # Introduce each wire's local guide as the camera returns to the circuit.
    # Keep the same illustrative radius at all six overview sites.
    for index, (name, center, direction) in enumerate(overview_guides):
        if tuple(center) == MICRO_ORIGIN:
            # The original three circles already show this site's field.
            continue
        site = bpy.data.objects.new("Field site | " + name, None)
        group.objects.link(site)
        site.location = center
        site.rotation_mode = "QUATERNION"
        site.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(Vector(direction).normalized())
        site["conventional_current"] = tuple(-v for v in Vector(direction).normalized())
        ring, objects = guide(group, mats, "Circuit field circle | " + name, OVERVIEW_RADIUS, .015)
        reveal(ring, objects, site, LESSON.zoom_out_end-3+index*.12, LESSON.switch_off)
    return group
