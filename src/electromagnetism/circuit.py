"""The tabletop circuit: battery, copper, knife switch and current limiter."""

import math
import bpy
from . import geometry as g
from .config import LESSON, WIRE_Z, SAMPLE_Z, ELECTRON_PATH, MICRO_SCALE, ELECTRON_RADIUS
from .motion import drift_time, key_location, sample_path, visible_windows
from .materials import cutaway_cover

Z = WIRE_Z


def label(body, location, size, mats, group, camera, color="white"):
    return g.face_camera(g.text(body, body, location, size, mats["ink_"+color], group, align="CENTER"), camera)


def build(scene, mats, camera):
    group = g.collection("01 | Battery, copper and switch", scene)
    # Separate pieces leave real physical gaps for both the switch and limiter.
    paths = [
        [(-2, -2.2, Z), (-5, -2.2, Z), (-5, 2.2, SAMPLE_Z), (-5.15*MICRO_SCALE, 2.2, SAMPLE_Z)],
        [(5.15*MICRO_SCALE, 2.2, SAMPLE_Z), (5, 2.2, SAMPLE_Z), (5, 0.5, Z)],
        [(5, -0.7, Z), (5, -2.2, Z), (3.8, -2.2, Z)],
        [(2.0, -2.2, Z), (1, -2.2, Z)],
    ]
    for i, points in enumerate(paths):
        g.line(f"Copper conductor {i+1}", points, 0.115, mats["copper"], group)
    cover_material = cutaway_cover(mats["copper"], LESSON)
    g.cylinder("Sample cover | fades open", (-5.15*MICRO_SCALE, 2.2, SAMPLE_Z),
               (5.15*MICRO_SCALE, 2.2, SAMPLE_Z), 0.115, cover_material, group)
    for x, y in [(-5, -2.2), (-5, 2.2), (5, 2.2), (5, -2.2)]:
        g.sphere("Rounded copper bend", (x, y, SAMPLE_Z if y > 0 else Z), 0.115, mats["copper"], group)
    for x in (-4.6, 4.6):
        g.cylinder("Insulated wire support", (x, 2.2, 0), (x, 2.2, SAMPLE_Z-0.14), 0.13, mats["edge"], group)
        g.box("Wire support foot", (x, 2.2, 0.08), (0.65, 0.6, 0.16), mats["edge"], group, 0.08)
    # An explicit resistive component avoids presenting a direct battery short.
    g.cylinder("Current-limiting resistor", (5, -0.7, Z), (5, 0.5, Z), 0.23, mats["ceramic"], group)
    for y, color in [(-0.46, "copper"), (-0.2, "navy"), (0.18, "gold")]:
        g.cylinder("Resistor band", (5, y-0.045, Z), (5, y+0.045, Z), 0.235, mats[color], group)

    g.cylinder("Battery body", (-1.8, -2.2, Z), (0.65, -2.2, Z), 0.61, mats["panel"], group)
    g.cylinder("Battery copper cap", (0.25, -2.2, Z), (0.72, -2.2, Z), 0.62, mats["copper_light"], group)
    g.cylinder("Battery negative contact", (-2, -2.2, Z), (-1.8, -2.2, Z), 0.46, mats["silver"], group)
    g.cylinder("Battery positive contact", (0.72, -2.2, Z), (1, -2.2, Z), 0.25, mats["silver"], group)
    g.box("Battery holder", (-.45,-2.2,.12), (3.15,1.5,.24), mats["rubber"], group, .1)
    for x in (-1.85,.8):
        g.box("Battery holder end wall", (x,-2.2,.38), (.14,1.45,.58), mats["rubber"], group,.035)
    g.text("Printed cell label", "DRY CELL  1.5 V", (-.6,-2.812,.68), .15, mats["chalk"], group,
           rotation=(math.pi/2,0,0), align="CENTER")
    label("BATTERY", (-0.5, -2.3, 1.48), 0.25, mats, group, camera)
    label("(-)", (-2.3, -2.9, 1.1), 0.38, mats, group, camera, "cyan")
    label("(+)", (1.1, -2.9, 1.1), 0.38, mats, group, camera, "gold")
    label("Copper wire", (-0.8, 2.8, 1.95), 0.33, mats, group, camera, "copper_light")
    label("Current limiter", (5.3, -0.8, 0.1), 0.2, mats, group, camera, "muted")

    g.box("Switch base", (2.9, -2.2, 0.26), (2.55, 1, 0.3), mats["wood"], group)
    for x in (1.85,3.95):
        for y in (-2.53,-1.87):
            g.cylinder("Switch mounting screw", (x,y,.41), (x,y,.45), .065, mats["silver"], group)
            g.box("Screwdriver slot", (x,y,.454), (.085,.015,.008), mats["rubber"], group,0)
    for x in (2, 3.8):
        g.cylinder("Switch contact", (x, -2.2, 0.4), (x, -2.2, Z), 0.16, mats["silver"], group)
    pivot = bpy.data.objects.new("Switch hinge | animated", None)
    group.objects.link(pivot)
    pivot.location = (2, -2.2, Z)
    blade = g.box("Switch conducting blade", (0, 0, 0), (1.9, 0.22, 0.13), mats["copper_light"], group, 0.06)
    blade.parent = pivot
    blade.location = (0.9, 0, 0)
    handle = g.sphere("Switch insulated grip", (0, 0, 0), 0.19, mats["navy"], group)
    handle.parent = pivot
    handle.location = (1.55, 0, 0.12)
    for seconds, angle in [(0, -43), (LESSON.switch_move, -43), (LESSON.switch_on, 0),
                           (LESSON.switch_off-1/LESSON.fps, 0), (LESSON.switch_off+0.7, -43), (LESSON.duration, -43)]:
        pivot.rotation_euler.y = math.radians(angle)
        pivot.keyframe_insert("rotation_euler", frame=LESSON.frame(seconds))
    label("SWITCH", (2.9, -3.1, 0.3), 0.25, mats, group, camera)

    # No selection rings: students mistook them for magnetic field lines.
    # World labels are useful in overview; hide them during magnification.
    for obj in group.objects:
        if obj.type == "FONT":
            visible_windows(obj, [(1, LESSON.frame(2)),
                                  (LESSON.frame(LESSON.zoom_out_end-1), LESSON.last_frame)])

    # Surface dots are explanatory markers for electron drift, not a literal
    # model of electrons moving only along the outside of the wire.
    moving = g.collection("02 | Electron direction markers", scene)
    for index in range(28):
        obj = g.sphere(f"Electron direction marker {index+1:02}", (0, 0, 0), ELECTRON_RADIUS, mats["ink_cyan"], moving)
        visible_windows(obj, [(LESSON.frame(LESSON.zoom_out_end-1), LESSON.frame(LESSON.switch_off)-1)])
        for frame in range(LESSON.frame(LESSON.switch_on), LESSON.frame(LESSON.switch_off)+1):
            seconds = (frame-1)/LESSON.fps
            position = sample_path(ELECTRON_PATH, index/28 + drift_time(seconds)/19)
            key_location(obj, frame, (position[0], position[1], position[2]+0.13))
    return pivot
