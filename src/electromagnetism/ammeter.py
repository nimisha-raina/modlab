"""Round analogue series ammeter mounted in the left copper-wire branch."""

import math
import bpy
from . import geometry as g, current_demo as demo
from .config import MICRO_SCALE, SAMPLE_Z, WIRE_Z


def build(scene, mats):
    group = g.collection("Ammeter | Series circuit connection", scene)
    old = next(o for o in scene.objects if o.name.split(".")[0] == "Copper conductor 1")
    bpy.data.objects.remove(old, do_unlink=True)
    paths = [
        [(-2, -2.2, WIRE_Z), (-5, -2.2, WIRE_Z), demo.METER_PATH[0]],
        demo.METER_PATH[:2], demo.METER_PATH[2:],
        [demo.METER_PATH[-1], (-5, 2.2, SAMPLE_Z), (-5.15*MICRO_SCALE, 2.2, SAMPLE_Z)],
    ]
    for index, points in enumerate(paths):
        material = mats["rubber"] if index in (1, 2) else mats["copper"]
        conductor = g.line(f"Ammeter series conductor {index+1}", points,
                           .047 if index in (1, 2) else .115, material, group)
        conductor["series_path"] = index
        if index in (1, 2):
            conductor["rear_connection"] = True
            conductor.hide_render = conductor.hide_viewport = True

    root = bpy.data.objects.new("Ammeter | Inline round analogue instrument", None)
    group.objects.link(root)
    root.location = demo.AMMETER_CENTER
    root.rotation_euler.x = demo.AMMETER_TILT
    root["scale_min_amperes"] = -1.
    root["scale_max_amperes"] = 1.
    root["connection_layout"] = "concealed rear terminals"

    def local(obj):
        obj.parent = root
        return obj

    local(g.cylinder("Ammeter round black housing", (0, 0, -.30), (0, 0, -.025), .84,
                     mats["rubber"], group, vertices=96))
    local(g.cylinder("Ammeter metal dial rim", (0, 0, -.026), (0, 0, .012), .735,
                     mats["silver"], group, vertices=96))
    local(g.cylinder("Ammeter raised black bezel", (0, 0, .012), (0, 0, .042), .72,
                     mats["rubber"], group, vertices=96))
    # A clipped white face and broad lower housing match a school panel meter.
    dial = bpy.data.meshes.new("Ammeter white dial face")
    arc = [math.radians(-39+258*i/96) for i in range(97)]
    # Explicit triangles and generous depth separation prevent the black
    # bezel from competing with the dial in the moving, distant camera view.
    vertices = [(0, 0, .080)]+[(.675*math.cos(a), .675*math.sin(a), .080) for a in arc]
    triangles = [(0, i, i+1) for i in range(1, len(vertices)-1)]
    triangles.append((0, len(vertices)-1, 1))
    dial.from_pydata(vertices, [], triangles)
    face = bpy.data.objects.new("Ammeter white analogue dial", dial)
    group.objects.link(face)
    dial.materials.append(mats["ink_white"])
    local(face)
    for angle in (math.pi/2, 7*math.pi/6, 11*math.pi/6):
        x, y = .755*math.cos(angle), .755*math.sin(angle)
        local(g.cylinder("Ammeter mounting screw", (x, y, -.015), (x, y, .03), .034,
                         mats["silver"], group, vertices=16))
    # A centre-zero scale correctly displays the later reverse-current case.
    pivot_y = -.20
    for index in range(41):
        amperes = -1+index/20
        angle = demo.meter_angle(amperes)
        length = .057 if index % 10 == 0 else .033 if index % 5 == 0 else .02
        points = [(r*math.cos(angle), pivot_y+r*math.sin(angle), .095)
                  for r in (.71-length, .71)]
        local(g.line("Ammeter scale graduation", points, .0035, mats["ink_navy"], group))
        if index % 10 == 0:
            body = "0" if amperes == 0 else f"{amperes:+.1f}"
            local(g.text("Ammeter printed scale | " + body, body,
                         (.56*math.cos(angle), pivot_y+.56*math.sin(angle)-.033, .100),
                         .09, mats["ink_navy"], group, align="CENTER"))
    local(g.text("Ammeter printed unit", "A", (0, -.045, .100), .21,
                 mats["ink_navy"], group, align="CENTER"))
    pointer = bpy.data.objects.new("Ammeter analogue pointer | measured current", None)
    group.objects.link(pointer)
    pointer.parent = root
    pointer.location = (0, pivot_y, .110)
    pointer["analogue_pointer"] = True
    mesh = bpy.data.meshes.new("Ammeter red pointer")
    mesh.from_pydata([(-.07, -.015, 0), (.66, 0, 0), (-.07, .015, 0)], [], [(0, 1, 2)])
    needle = bpy.data.objects.new("Ammeter red needle", mesh)
    group.objects.link(needle)
    needle.parent = pointer
    pointer_ink = mats["ink_navy"].copy()
    pointer_ink.name = "EM / ammeter red pointer"
    pointer_ink.diffuse_color = (.7, .025, .02, 1)
    next(n for n in pointer_ink.node_tree.nodes if n.type == "EMISSION").inputs["Color"].default_value = pointer_ink.diffuse_color
    mesh.materials.append(pointer_ink)
    local(g.cylinder("Ammeter pointer pivot", (0, pivot_y, .112), (0, pivot_y, .135),
                     .044, mats["silver"], group, vertices=24))
    for name, terminal in zip(("negative", "positive"), demo.METER_TERMINALS):
        x, y, z = terminal
        terminal_obj = local(g.cylinder("Ammeter terminal | " + name,
                                       (x, y, z-.05), (x, y, z+.04),
                                       .075, mats["silver"], group))
        terminal_obj.hide_render = terminal_obj.hide_viewport = True
    local(g.cylinder("Ammeter mechanical zero adjustment", (0, -.57, .045), (0, -.57, .07),
                     .072, mats["rubber"], group, vertices=32))
    local(g.line("Ammeter adjustment screw slot", [(-.04, -.57, .072), (.04, -.57, .072)],
                 .007, mats["silver"], group))
    x, y, _ = demo.AMMETER_CENTER
    g.box("Ammeter mounting foot", (x, y, .04), (1.0, .8, .1), mats["rubber"], group, .04)
    g.cylinder("Ammeter inline mounting support", (x, y, .09),
               (x, y, demo.AMMETER_CENTER[2]-.58), .13,
               mats["silver"], group)
    # A small on-face teaching readout accompanies the actual analogue needle.
    reading = local(g.text("Ammeter measured current", "0.50 A", (0, -.40, .100), .18,
                           mats["ink_navy"], group, align="CENTER"))
    reading["reference_amperes"] = demo.REFERENCE_AMPS
    return reading


def animate(reading, fps, duration, current_at):
    """Show centiampere readings using frame-accurate text visibility."""
    # Blender font bodies cannot be keyframed. Use one visible text object per
    # value, with frame-accurate visibility; the physical display stays fixed.
    group = reading.users_collection[0]
    pointer = next(obj for obj in group.objects if obj.get("analogue_pointer"))
    for frame in range(1, round(duration*fps)+1):
        amperes = demo.REFERENCE_AMPS*current_at((frame-1)/fps)
        pointer.rotation_euler.z = demo.meter_angle(amperes)
        pointer["needle_amperes"] = amperes
        pointer.keyframe_insert("rotation_euler", frame=frame)
        pointer.keyframe_insert('["needle_amperes"]', frame=frame)
    values = {}
    for frame in range(1, round(duration*fps)+1):
        value = round(demo.REFERENCE_AMPS*current_at((frame-1)/fps)*100)
        values.setdefault(value, []).append(frame)
    readings = []
    for value, frames in values.items():
        obj = reading if not readings else reading.copy()
        if readings:
            obj.data = reading.data.copy()
            group.objects.link(obj)
            obj.animation_data_clear()
        obj.name = f"Ammeter reading | {value/100:.2f} A"
        obj.data.body = f"{value/100:.2f} A"
        obj["amperes"] = value/100
        readings.append(obj)
        active = set(frames)
        previous = None
        for frame in range(1, round(duration*fps)+1):
            hidden = frame not in active
            if hidden != previous:
                obj.hide_render = obj.hide_viewport = hidden
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)
            previous = hidden
    return readings
