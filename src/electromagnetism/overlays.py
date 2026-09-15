"""Camera-attached titles, captions and a persistent switch indicator."""

import math
import bpy
from . import geometry as g
from .config import LESSON
from .lesson_text import CAPTIONS
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


def build(scene, mats, camera):
    group = g.collection("05 | Titles, captions and legends", scene)
    panel(camera, group, mats, "Lesson title backplate", -1, 1.30, 4.02, .66)
    label(camera, group, mats, "FIELD NOTES    /    CLASS 8 SCIENCE", -2.92, 1.48, 0.075, "mint")
    label(camera, group, mats, "Electricity makes magnetism", -2.92, 1.19, 0.215)
    for start, end, body in [
        (0, 3, "01  /  THE CIRCUIT"),
        (3, LESSON.microscope_out, "02  /  INSIDE COPPER"),
        (LESSON.microscope_out, LESSON.duration, "03  /  BACK TO THE CIRCUIT"),
    ]:
        obj = label(camera, group, mats, body, -2.92, 1.01, 0.077, "muted")
        visibility(obj, LESSON.frame(start), min(LESSON.frame(end)-1, LESSON.last_frame))
    panel(camera, group, mats, "Switch state card", 2.15, 1.31, 1.5, 0.43, "panel")
    for start, end, body, color in [
        (0, LESSON.switch_on, "SWITCH  OPEN", "gold"),
        (LESSON.switch_on, LESSON.switch_off, "SWITCH  CLOSED", "mint"),
        (LESSON.switch_off, LESSON.duration, "SWITCH  OPEN", "gold"),
    ]:
        obj = label(camera, group, mats, body, 2.15, 1.31, 0.105, color, "CENTER")
        visibility(obj, LESSON.frame(start), min(LESSON.frame(end)-1, LESSON.last_frame))
    label(camera, group, mats, "CIRCUIT STATUS", 2.15, 1.16, 0.065, "muted", "CENTER")
    for left, right in [((1.59, 0.75), (1.91, 0.75)), ((2.42, 0.75), (2.73, 0.75))]:
        obj = g.line("Status switch lead", [(left[0], left[1], 0), (right[0], right[1], 0)], 0.008, mats["ink_muted"], group)
        attach(obj, camera, (0, 0, -7.95))
    blade = g.line("Status switch blade", [(0, 0, 0), (0.51, 0, 0)], 0.012, mats["ink_white"], group)
    attach(blade, camera, (1.91, 0.75, -7.95))
    for seconds, angle in [(0, 28), (LESSON.switch_move, 28), (LESSON.switch_on, 0),
                           (LESSON.switch_off-1/LESSON.fps, 0), (LESSON.switch_off+0.7, 28), (LESSON.duration, 28)]:
        blade.rotation_euler.z = math.radians(angle)
        blade.keyframe_insert("rotation_euler", frame=LESSON.frame(seconds))

    panel(camera, group, mats, "Caption plate", 0, -1.26, 5.95, 0.55)
    for start, end, title, subtitle in CAPTIONS:
        for body, y, size, color in [(title, -1.2, 0.123, "white"), (subtitle, -1.4, 0.101, "muted")]:
            obj = label(camera, group, mats, body, -2.76, y, size, color)
            visibility(obj, LESSON.frame(start), min(LESSON.frame(end)-1, LESSON.last_frame))
    label(camera, group, mats, "LAB VIEW  /  Teaching model: particle sizes, spacing and motion exaggerated", -2.92, -1.65, 0.065, "muted")
    label(camera, group, mats, "04", 2.9, -1.65, 0.075, "mint", "RIGHT")

    micro_start, micro_end = LESSON.frame(LESSON.microscope_in), LESSON.frame(LESSON.microscope_out+1)
    for x in (-2.12, 2.08):
        obj = panel(camera, group, mats, "Terminal connection label plate", x, 0.32, 1.68, 0.23)
        visibility(obj, micro_start, micro_end)
    for body, x, y, size, color, align in [
        ("COPPER IONS / vibrate in place", -2.8, 0.73, 0.083, "copper_light", "LEFT"),
        ("BLUE DOTS / mobile electrons", -2.8, 0.56, 0.083, "cyan", "LEFT"),
        ("FROM BATTERY (-)", -2.85, 0.30, 0.098, "cyan", "LEFT"),
        ("TOWARDS BATTERY (+)", 2.85, 0.30, 0.098, "gold", "RIGHT"),
    ]:
        obj = label(camera, group, mats, body, x, y, size, color, align)
        visibility(obj, micro_start, micro_end)
    direction = label(camera, group, mats, "ELECTRON FLOW   /   negative to positive", 0, -0.83, 0.105, "cyan", "CENTER")
    visibility(direction, LESSON.frame(LESSON.switch_on), micro_end)
    # A full-width arrow and two local arrows make entry and exit unambiguous.
    for x1, x2, y in [(-2.3, 2.3, -0.65), (-2.7, -2.15, 0.10), (2.15, 2.7, 0.10)]:
        obj = g.line("Electron flow arrow", [(x1,y,0),(x2,y,0),(x2-0.10,y+0.05,0),(x2,y,0),(x2-0.10,y-0.05,0)], 0.008, mats["ink_cyan"], group)
        attach(obj, camera, (0, 0, -7.95))
        visibility(obj, LESSON.frame(LESSON.switch_on), micro_end)
    obj = label(camera, group, mats, "RANDOM MOTION  /  no net electron flow", 0, -0.83, 0.105, "cyan", "CENTER")
    visibility(obj, micro_start, LESSON.frame(LESSON.switch_on)-1)
    obj = label(camera, group, mats, "GREEN / magnetic field direction", 0, 0.91, 0.078, "mint", "CENTER")
    visibility(obj, LESSON.frame(LESSON.field_reveal), LESSON.frame(LESSON.switch_off)-1)
    # The later convention is separated from the microscopic electron arrows.
    card = panel(camera, group, mats, "Flow comparison plate", 0, -0.75, 3.1, 0.43)
    visibility(card, LESSON.frame(38), LESSON.frame(LESSON.switch_off)-1)
    for body, y, color in [("Electron flow   -  >>>  +", -0.69, "cyan"),
                            ("Conventional current   -  <<<  +", -0.88, "gold")]:
        obj = label(camera, group, mats, body, 0, y, 0.09, color, "CENTER")
        visibility(obj, LESSON.frame(38), LESSON.frame(LESSON.switch_off)-1)
    return group
