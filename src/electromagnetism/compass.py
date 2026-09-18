"""A reusable physical compass with a two-colour, keyframeable needle."""

import math
import bpy
from . import geometry as g


def build(scene, mats, center, north_angle=0, on_stand=False):
    group = g.collection("Compass | Fixed measurement position", scene)
    x, y, z = center
    if on_stand:
        g.cylinder("Compass stand foot", (x, y, .02), (x, y, .10), .58, mats["rubber"], group)
        g.cylinder("Compass nonmagnetic stand", (x, y, .10), (x, y, z-.08), .12, mats["gold"], group)
    else:
        g.cylinder("Compass nonmagnetic base", (x, y, .02), (x, y, z-.06), .84, mats["rubber"], group)
    g.cylinder("Compass brass rim", (x, y, z-.08), (x, y, z), .82, mats["gold"], group)
    g.cylinder("Compass dial", (x, y, z-.01), (x, y, z+.006), .76, mats["ink_navy"], group)
    for tick in range(72):
        angle = north_angle+tick*math.tau/72
        a = .67 if tick % 6 == 0 else .71
        g.line("Compass graduation", [(x+r*math.cos(angle), y+r*math.sin(angle), z+.013)
                                      for r in (a, .75)], .006, mats["ink_muted"], group)
    for body, angle in [("N", 0), ("E", -math.pi/2), ("S", math.pi), ("W", math.pi/2)]:
        angle += north_angle
        obj = g.text("Compass cardinal | " + body, body,
                     (x+.57*math.cos(angle), y+.57*math.sin(angle)-.055, z+.018),
                     .14, mats["ink_white"], group, align="CENTER")
    needle = bpy.data.objects.new("Compass needle | north-seeking red tip", None)
    group.objects.link(needle)
    needle.location = center
    red = mats["ink_copper_light"].copy()
    red.name = "Compass | red north tip"
    next(node for node in red.node_tree.nodes if node.type == "EMISSION").inputs["Color"].default_value = (.8, .035, .025, 1)
    for sign, material, name in [(1, red, "North"), (-1, mats["ink_white"], "South")]:
        mesh = bpy.data.meshes.new("Compass " + name + " half")
        mesh.from_pydata([(0, -.10, .04), (sign*.51, 0, .04), (0, .10, .04)], [], [(0, 1, 2)])
        obj = bpy.data.objects.new("Needle | " + name, mesh)
        group.objects.link(obj)
        obj.parent = needle
        mesh.materials.append(material)
    g.cylinder("Compass pivot", (x, y, z+.03), (x, y, z+.075), .055, mats["gold"], group)
    g.text("Compass apparatus label", "MAGNETIC COMPASS", (x, y-1.05, .025), .14,
           mats["ink_white"], group, align="CENTER")
    return needle


def deflection_indicator(scene, mats, center, north_angle, maximum_angle):
    """A fixed north reference and an arc measuring the needle's deflection."""
    needle = next(o for o in scene.objects if o.name.startswith("Compass needle |"))
    group = needle.users_collection[0]
    x, y, z = center
    span = north_angle-maximum_angle
    points = [(x+.96*math.cos(north_angle-span*i/64),
               y+.96*math.sin(north_angle-span*i/64), z+.025) for i in range(65)]
    arc = g.line("Compass deflection arc", points, .012, mats["ink_gold"], group)
    arc["maximum_radians"] = span
    for degrees in (0, 25, round(math.degrees(span))):
        angle = north_angle-math.radians(degrees)
        g.line("Compass angle reference", [(x+r*math.cos(angle), y+r*math.sin(angle), z+.03)
                                            for r in (.85, 1.04)],
               .009, mats["ink_gold"], group)
        g.text("Compass marked angle", f"{degrees}°",
               (x+1.17*math.cos(angle), y+1.17*math.sin(angle)-.03, z+.03),
               .12, mats["ink_gold"], group, align="CENTER")
    reading = g.text("Compass deflection reading", "Deflection: 25°", (x, y-1.40, .03),
                     .21, mats["ink_gold"], group, align="CENTER")
    return arc, reading


def key_deflection(indicator, angle, frame):
    arc, _ = indicator
    arc.data.bevel_factor_end = max(0, min(1, angle/arc["maximum_radians"]))
    arc["deflection_degrees"] = math.degrees(angle)
    arc.data.keyframe_insert("bevel_factor_end", frame=frame)
    arc.keyframe_insert('["deflection_degrees"]', frame=frame)


def animate_deflection_readings(indicator, fps, duration, angle_at):
    """Keep a readable integer-degree measurement beside the placed compass."""
    _, template = indicator
    template.animation_data_clear()
    group = template.users_collection[0]
    frames = {frame: None if angle_at((frame-1)/fps) is None else
              round(math.degrees(angle_at((frame-1)/fps)))
              for frame in range(1, duration*fps+1)}
    for index, value in enumerate(sorted(set(frames.values())-{None})):
        obj = template if index == 0 else template.copy()
        if index:
            obj.data = template.data.copy()
            obj.animation_data_clear()
            group.objects.link(obj)
        obj.name = f"Compass deflection reading | {value} degrees"
        obj.data.body = f"Deflection: {value}°"
        obj["display_degrees"] = value
        previous = None
        for frame, active in frames.items():
            hidden = active != value
            if hidden != previous:
                obj.hide_render = obj.hide_viewport = hidden
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)
            previous = hidden
