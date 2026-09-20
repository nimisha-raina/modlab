"""Fixed, symmetric compass instruments with visible angular measurements."""
import math
from . import geometry as g, compass, coil_demo as demo


def build(scene, mats, camera):
    instruments = []
    for side, center in zip(("left", "right"), demo.COMPASS_CENTERS):
        needle = compass.build(scene, mats, center, demo.NORTH_ANGLE, on_stand=True)
        needle["coil_compass_side"] = side
        group = needle.users_collection[0]
        x, y, z = center
        arcs = []
        for sign in (1, -1):
            points = [(x+.66*math.cos(demo.NORTH_ANGLE+sign*math.pi*i/160),
                       y+.66*math.sin(demo.NORTH_ANGLE+sign*math.pi*i/160), z+.035)
                      for i in range(81)]
            arc = g.line("Compass measured deflection arc", points, .019, mats["ink_gold"], group)
            arc["compass_arc"] = True
            arcs.append((sign, arc))
        g.line("Compass zero reference", [(x,y+.30,z+.025),(x,y+.69,z+.025)],
               .012, mats["ink_muted"], group)
        template = g.face_camera(g.text("Coil compass deflection", "0°",
            (x,y-.6,.9), .28,mats["ink_gold"],group,align="CENTER"),camera)
        compass.animate_deflection_readings((None,template),demo.FPS,demo.DURATION,
            lambda t,c=center: abs(demo.needle_angle_at(t,c)-demo.NORTH_ANGLE))
        instruments.append((needle, center, arcs))
    return instruments


def animate(instruments, seconds, frame):
    for needle, center, arcs in instruments:
        angle = demo.needle_angle_at(seconds, center)
        needle.rotation_euler.z = angle
        needle.keyframe_insert("rotation_euler",frame=frame)
        for sign, arc in arcs:
            arc.data.bevel_factor_end = max(0, sign*(angle-demo.NORTH_ANGLE)/(math.pi/2))
            arc.data.keyframe_insert("bevel_factor_end",frame=frame)
            arc.hide_render = arc.hide_viewport = arc.data.bevel_factor_end < .001
            arc.keyframe_insert("hide_render",frame=frame)
            arc.keyframe_insert("hide_viewport",frame=frame)
