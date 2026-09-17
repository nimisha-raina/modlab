"""Build Part 2: a six-turn air-core coil and supply-polarity reversal."""

import math
import bpy
from mathutils import Vector
from . import geometry as g, stage, circuit, chalkboard, compass, ammeter
from . import coil_demo as demo, current_demo, morph_geometry as morph
from .build import clean_previous_lesson
from .config import OUTPUT, SAMPLE_Z
from .materials import make_materials

DESTINATION = OUTPUT / "parts" / "02_coil_reversal"


def build():
    clean_previous_lesson(demo.SCENE_NAME)
    scene = bpy.data.scenes.new(demo.SCENE_NAME)
    bpy.context.window.scene = scene
    mats = make_materials()
    camera = stage.setup(scene, mats, "preview")
    switch = circuit.build(scene, mats, camera)
    scene.frame_end = demo.DURATION*demo.FPS
    scene.timeline_markers.clear()
    camera.animation_data_clear()
    switch.animation_data_clear()
    switch.rotation_euler.y = 0
    for obj in scene.objects:
        if obj.type == "FONT":
            obj.animation_data_clear()
            obj.hide_render = obj.hide_viewport = False
    for obj in list(scene.objects):
        if obj.type == "FONT" and obj.data.body == "Copper wire":
            bpy.data.objects.remove(obj, do_unlink=True)
    reading = ammeter.build(scene, mats)
    ammeter.animate(reading, demo.FPS, demo.DURATION, demo.current_at)
    # Replace every part of the former straight top span, including its cover.
    group = g.collection("Coil | Six turns in the microscope wire area", scene)
    for obj in list(scene.objects):
        if obj.name.startswith("Sample cover") or obj.name.split(".")[0] == "Copper conductor 2" or obj.get("series_path") == 3:
            bpy.data.objects.remove(obj, do_unlink=True)
    lead = g.line("Ammeter series conductor 4", [current_demo.METER_PATH[-1], (-5, 2.2, SAMPLE_Z)], .115, mats["copper"], group)
    lead["series_path"] = 3
    g.line("Copper conductor 2", [(5, 2.2, SAMPLE_Z), (5, .5, .7)], .115, mats["copper"], group)
    enamel = mats["copper"].copy()
    enamel.name = "EM / enamel-insulated copper winding"
    enamel.node_tree.nodes.get("Principled BSDF").inputs["Coat Weight"].default_value = .7
    wire = morph.tube("Copper wire | Straight to six-turn coil", {"Basis": demo.wire_points(0),
                      "Six turns": demo.wire_points(1)}, .085, enamel, group)
    wire["turns"] = demo.TURNS
    wire["insulation"] = "enamel; spaced turns"

    chalkboard.build(scene, mats, [
        {"start": 0, "end": 17, "case": "CASE 2  /  MAKING A SIX-TURN COIL",
         "heading": "A coil has north and south poles",
         "observation": "The fields of its turns combine. Current: 0.50 A."},
        {"start": 17, "end": demo.DURATION, "case": "CASE 2  /  REVERSING THE CURRENT",
         "heading": "Reverse current. Swap the poles.",
         "observation": "Same coil. Same current magnitude. Needle turns."},
    ])
    needle = compass.build(scene, mats, demo.COMPASS_CENTER, demo.NORTH_ANGLE)
    field_group = g.collection("Coil | Combining magnetic fields", scene)
    traces = demo.solenoid_lines()
    guides = []
    paths = []
    # Six local wire guides become six resultant loops, three on each side.
    for i in range(6):
        x = -demo.LENGTH/2+demo.LENGTH*(i+.5)/6
        straight, local, final = [], [], []
        plane = 0 if i < 3 else math.pi
        for j in range(192):
            a = j*2*math.pi/192
            straight.append((x, demo.CENTER[1]+.42*math.cos(a), SAMPLE_Z+.42*math.sin(a)))
            # At each turn's midpoint the wire tangent is nearly vertical.
            local.append((x+.28*math.cos(a), demo.CENTER[1]-demo.RADIUS+.28*math.sin(a), SAMPLE_Z))
            px, radial, _ = traces[i % 3][j]
            final.append((px, demo.CENTER[1]+radial*math.cos(plane), SAMPLE_Z+radial*math.sin(plane)))
        obj = morph.tube(f"Coil field guide {i+1}", {"Basis": straight, "Around wound wire": local,
                         "Combined solenoid field": final}, .013, mats["ink_mint"], field_group, cyclic=True)
        obj["field_guide"] = True
        guides.append(obj)
        paths.append((straight, local, final))

    # Separate arrow objects reverse direction while the field geometry stays.
    direction_objects = []
    for i, (_, _, points) in enumerate(paths):
        for sign in (1, -1):
            arrows = []
            for index in (8, 105):
                p = Vector(points[index])
                # Traces follow +X internally; this winding's forward current
                # produces -X internally, so baseline points against the trace.
                tangent = (Vector(points[(index+1) % 192])-Vector(points[(index-1) % 192])).normalized()*-sign
                arrows.extend(g.arrow(f"Coil field arrow | {i+1} | {sign}", p-tangent*.19, p+tangent*.05,
                                      .021, mats["ink_mint"], field_group))
            direction_objects.append((sign, arrows))
    poles = []
    for sign in (1, -1):
        for side, x in [("left", -2.05), ("right", 2.05)]:
            north = (side == "left") == (sign == 1)
            obj = g.face_camera(g.text(f"Coil pole | {side} | {sign}", "N" if north else "S",
                   (x, 2.2, 2.52), .55, mats["ink_mint" if north else "ink_gold"], group, align="CENTER"), camera)
            obj["pole"] = "N" if north else "S"
            obj["side"] = side
            poles.append((sign, obj))

    # Reverse the actual cell while the knife switch is open. A dry cell's
    # chemical terminals retain their polarity; turning it swaps connections.
    cell = bpy.data.objects.new("Cell | Reverse connections while switch open", None)
    group.objects.link(cell)
    cell.location = (-.5, -2.2, .7)
    for obj in list(scene.objects):
        if obj.name.startswith(("Battery body", "Battery copper cap", "Battery negative contact",
                                "Battery positive contact", "Printed cell label")):
            obj.parent = cell
            obj.location -= cell.location
    # Supply terminal labels change along with its controlled output polarity.
    terminal_labels = []
    for obj in list(scene.objects):
        if obj.type == "FONT" and obj.data.body in ("(+)", "(-)"):
            original = obj.data.body
            swapped = obj.copy()
            swapped.data = obj.data.copy()
            swapped.animation_data_clear()
            swapped.data.body = "(-)" if original == "(+)" else "(+)"
            group.objects.link(swapped)
            terminal_labels.extend([(1, obj), (-1, swapped)])

    for frame in range(1, scene.frame_end+1):
        seconds = (frame-1)/demo.FPS
        wound, combined = demo.coil_fraction(seconds), demo.field_fraction(seconds)
        current = demo.current_at(seconds)
        camera.location, target = demo.camera_pose(seconds)
        stage.point_at(camera, target)
        camera.keyframe_insert("location", frame=frame)
        camera.keyframe_insert("rotation_euler", frame=frame)
        morph.key_pose(wire, "Six turns", wound, frame)
        needle.rotation_euler.z = demo.compass_angle(wound, current)
        needle.keyframe_insert("rotation_euler", frame=frame)
        needle["current_multiplier"] = current
        needle.keyframe_insert('["current_multiplier"]', frame=frame)
        turn = demo.smoothstep((seconds-22.5)/2)
        cell.rotation_euler.z = math.pi*turn
        cell.location.z = .7+.8*math.sin(math.pi*turn)
        cell.keyframe_insert("rotation_euler", frame=frame)
        cell.keyframe_insert("location", frame=frame)
        switch.rotation_euler.y = math.radians(-43)*(1-abs(current))
        switch.keyframe_insert("rotation_euler", frame=frame)
        for obj in guides:
            morph.key_pose(obj, "Around wound wire", wound*(1-combined), frame)
            morph.key_pose(obj, "Combined solenoid field", combined, frame)
            obj.hide_render = obj.hide_viewport = abs(current) < .001
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
        for sign, objects in direction_objects:
            for obj in objects:
                obj.hide_render = obj.hide_viewport = combined < .999 or current*sign <= .001
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)
        for sign, obj in poles:
            reading_board = 17 <= seconds < 20
            obj.hide_render = obj.hide_viewport = combined < .999 or current*sign <= .001 or reading_board
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
        for sign, obj in terminal_labels:
            obj.hide_render = obj.hide_viewport = current*sign <= .001
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
    for seconds, title in [(0, "Read board | Making a coil"), (5, "Wind six turns"),
                           (11, "Combine fields"), (15, "North and south | 0.50 A"),
                           (17, "Read board | Reversing current"), (22, "Reverse supply polarity"),
                           (25, "Poles exchanged | -0.50 A")]:
        scene.timeline_markers.new(title, frame=round(seconds*demo.FPS)+1)
    scene["audio_status"] = "Silent visual review; final narration pending sequence approval."
    scene["physics"] = "Six-turn air-core helix; compass uses complete circuit plus fixed Earth field."
    scene["field_guides"] = "Axisymmetric finite-ring approximation; closed resultant loops; drawing density is illustrative."
    scene["wire_reconfiguration"] = "Diagram of winding a longer wire segment, not a simulation of material stretch."
    scene["reference_amperes"] = .5
    scene.frame_set(1)
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 8
    DESTINATION.mkdir(parents=True, exist_ok=True)
    return scene
