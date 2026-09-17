"""Compact apparatus legends and a persistent switch indicator.

Narration captions are exported separately, not baked over the laboratory.
"""

import math
import bpy
from . import geometry as g
from .config import LESSON
from .motion import visibility

# Design in a 6.4 x 3.6 rectangle, then place it one unit from a 45 mm camera.
S = 1/8


def attach(obj, camera, position):
    obj.parent = camera
    obj.location = (position[0]*S, position[1]*S, position[2]*S)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (S, S, S)
    return obj


def label(camera, group, mats, body, x, y, size, color="white", align="LEFT", name=None):
    obj = g.text(name or body, body, (0, 0, 0), size, mats["ink_"+color], group, align=align)
    return attach(obj, camera, (x, y, -7.95))


def panel(camera, group, mats, name, x, y, width, height, color="navy"):
    obj = g.box(name, (0, 0, 0), (width, height, 0.018), mats["ink_"+color], group, 0.035)
    return attach(obj, camera, (x, y, -8.0))


def fitted_panel(camera, group, mats, name, labels, color="navy"):
    """Fit a backplate to evaluated text bounds with a small, even margin."""
    bpy.context.view_layer.update()
    # Text is slightly nearer the camera; match its projected bounds.
    depth_ratio = 8.0 / 7.95
    points = [(obj.location.x/S + corner[0], obj.location.y/S + corner[1])
              for obj in labels for corner in obj.bound_box]
    left, right = min(p[0] for p in points), max(p[0] for p in points)
    bottom, top = min(p[1] for p in points), max(p[1] for p in points)
    obj = panel(camera, group, mats, name,
                (left+right)*depth_ratio/2, (bottom+top)*depth_ratio/2,
                (right-left)*depth_ratio+.16, (top-bottom)*depth_ratio+.10, color)
    obj["text_width"] = (right-left)*depth_ratio*S
    obj["horizontal_padding"] = .16*S
    return obj


def build(scene, mats, camera, board_until=0):
    group = g.collection("05 | Apparatus legends", scene)
    status = label(camera, group, mats, "CIRCUIT STATUS", 2.15, 1.16, 0.065, "muted", "CENTER")
    visibility(status, LESSON.frame(board_until), LESSON.last_frame)
    for start, end, body, color in [
        (0, LESSON.switch_on, "SWITCH  OPEN", "gold"),
        (LESSON.switch_on, LESSON.switch_off, "SWITCH  CLOSED", "mint"),
        (LESSON.switch_off, LESSON.duration, "SWITCH  OPEN", "gold"),
    ]:
        obj = label(camera, group, mats, body, 2.15, 1.31, 0.105, color, "CENTER")
        plate = fitted_panel(camera, group, mats, "Switch state card", [obj, status], "panel")
        for item in (obj, plate):
            visibility(item, LESSON.frame(max(start, board_until)), min(LESSON.frame(end)-1, LESSON.last_frame))
    for left, right in [((1.59, 0.75), (1.91, 0.75)), ((2.42, 0.75), (2.73, 0.75))]:
        obj = g.line("Status switch lead", [(left[0], left[1], 0), (right[0], right[1], 0)], 0.008, mats["ink_muted"], group)
        attach(obj, camera, (0, 0, -7.95))
        visibility(obj, LESSON.frame(board_until), LESSON.last_frame)
    blade = g.line("Status switch blade", [(0, 0, 0), (0.51, 0, 0)], 0.012, mats["ink_white"], group)
    attach(blade, camera, (1.91, 0.75, -7.95))
    visibility(blade, LESSON.frame(board_until), LESSON.last_frame)
    for seconds, angle in [(0, 28), (LESSON.switch_move, 28), (LESSON.switch_on, 0),
                           (LESSON.switch_off-1/LESSON.fps, 0), (LESSON.switch_off+0.7, 28), (LESSON.duration, 28)]:
        blade.rotation_euler.z = math.radians(angle)
        blade.keyframe_insert("rotation_euler", frame=LESSON.frame(seconds))

    micro_start, micro_end = LESSON.frame(LESSON.microscope_in), LESSON.frame(LESSON.microscope_out+1)
    for body, x, y, size, color, align in [
        ("COPPER IONS / vibrate in place", -2.8, 0.73, 0.083, "copper_light", "LEFT"),
        ("BLUE DOTS / mobile electrons", -2.8, 0.56, 0.083, "cyan", "LEFT"),
        ("FROM BATTERY (-)", -2.85, 0.30, 0.098, "cyan", "LEFT"),
        ("TOWARDS BATTERY (+)", 2.85, 0.30, 0.098, "gold", "RIGHT"),
    ]:
        obj = label(camera, group, mats, body, x, y, size, color, align)
        visibility(obj, micro_start, micro_end)
        if "BATTERY" in body:
            plate = fitted_panel(camera, group, mats, "Terminal connection label plate", [obj])
            visibility(plate, micro_start, micro_end)
    direction = label(camera, group, mats, "ELECTRON FLOW   /   negative to positive", 0, -1.30, 0.105, "cyan", "CENTER")
    visibility(direction, LESSON.frame(LESSON.switch_on), micro_end)
    # A full-width arrow and two local arrows make entry and exit unambiguous.
    for x1, x2, y in [(-2.3, 2.3, -1.10), (-2.7, -2.15, 0.10), (2.15, 2.7, 0.10)]:
        obj = g.line("Electron flow arrow", [(x1,y,0),(x2,y,0),(x2-0.10,y+0.05,0),(x2,y,0),(x2-0.10,y-0.05,0)], 0.008, mats["ink_cyan"], group)
        attach(obj, camera, (0, 0, -7.95))
        visibility(obj, LESSON.frame(LESSON.switch_on), micro_end)
    obj = label(camera, group, mats, "RANDOM MOTION  /  no net electron flow", 0, -0.83, 0.105, "cyan", "CENTER")
    visibility(obj, micro_start, LESSON.frame(LESSON.switch_on)-1)
    obj = label(camera, group, mats, "GREEN / magnetic field direction", 0, 0.91, 0.078, "mint", "CENTER")
    visibility(obj, LESSON.frame(LESSON.field_reveal), LESSON.frame(LESSON.switch_off)-1)
    # The later convention is separated from the microscopic electron arrows.
    comparison = []
    for body, y, color in [("Electron flow   -  >>>  +", 1.43, "cyan"),
                            ("Conventional current   -  <<<  +", 1.24, "gold")]:
        obj = label(camera, group, mats, body, -2.85, y, 0.09, color)
        comparison.append(obj)
        visibility(obj, LESSON.frame(38), LESSON.frame(LESSON.switch_off)-1)
    card = fitted_panel(camera, group, mats, "Flow comparison plate", comparison)
    visibility(card, LESSON.frame(38), LESSON.frame(LESSON.switch_off)-1)
    return group
