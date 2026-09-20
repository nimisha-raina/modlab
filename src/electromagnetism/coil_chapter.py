"""Build Part 2: coils, polarity, iron core, clips and practical applications."""

import math
import bpy
from mathutils import Vector
from . import geometry as g, stage, circuit, ammeter
from . import coil_demo as demo, current_demo, morph_geometry as morph
from . import coil_board, coil_experiments, coil_camera, coil_annotations, coil_current_guides
from . import coil_resultant_field, coil_fixed_view, coil_compasses
from .coil_keyframes import frames
from .build import clean_previous_lesson
from .config import OUTPUT, SAMPLE_Z
from .materials import make_materials

DESTINATION = OUTPUT / "parts" / "02_coil_reversal"


def update_markers(scene):
    scene.timeline_markers.clear()
    for seconds,title in ((0,"Ten-turn coil ready | Switch OFF"),
                          (5,"Switch ON | Conventional current arrows"),
                          (6,"Paired local field circles"),(12,"Local fields combine"),
                          (16,"Closed field | Fixed 3D view"),(17,"Read both compass deflections"),
                          (26,"Switch OFF | Reverse directly"),(27,"Turn disconnected cell"),
                          (32,"Poles and blue arrows reversed"),(44,"Board | More turns"),
                          (51,"Switch OFF | Wind twenty turns"),(59,"Switch ON | Same 0.50 A"),
                          (66,"Switch OFF | Prepare iron core"),(68,"Insert soft iron nail"),
                          (74,"Switch ON | Stronger electromagnet"),(83,"Magnetic-region explanation"),
                          (99,"Clips ready below nail | Switch OFF"),
                          (103,"Switch ON | Attract clips"),(112,"Switch OFF | Release clips"),
                          (114,"Summary board"),(125,"Applications | All three magnetic components")):
        scene.timeline_markers.new(title,frame=round(seconds*demo.FPS)+1)


def build_winding(material, group):
    """Begin with ten turns; retain only the later ten-to-twenty transition."""
    poses = {"Basis": demo.wire_points(1)}
    dense_steps = round((demo.DENSE_END-demo.DENSE_START)*demo.FPS)
    for i in range(1,dense_steps+1):
        fraction = demo.dense_fraction(demo.DENSE_START+i/demo.FPS)
        poses["Twenty turns" if i == dense_steps else f"More turns {i:03d}"] = demo.dense_wire_points(fraction)
    wire = morph.curve_tube("Copper wire | Ten then twenty turns", poses, demo.WIRE_RADIUS, material, group)
    wire.data.shape_keys.use_relative = False
    for key in wire.data.shape_keys.key_blocks:
        key.interpolation = "KEY_LINEAR"
    wire["turns"] = demo.TURNS
    wire["insulation"] = "enamel; spaced turns"
    wire["maximum_turns"] = demo.DENSE_TURNS
    wire["axial_length"] = demo.LENGTH
    return wire


def animate_winding(wire, seconds, frame):
    keys = wire.data.shape_keys
    steps = len(keys.key_blocks)-1
    progress = max(0.,min(steps,(seconds-demo.DENSE_START)*demo.FPS))
    index = min(steps-1, int(progress))
    a, b = keys.key_blocks[index].frame, keys.key_blocks[index+1].frame
    keys.eval_time = a+(b-a)*(progress-index)
    keys.keyframe_insert("eval_time", frame=frame)
    wire["turns"] = demo.TURNS+(demo.DENSE_TURNS-demo.TURNS)*demo.dense_fraction(seconds)
    wire["coil_radius"] = demo.RADIUS+(demo.DENSE_RADIUS-demo.RADIUS)*demo.dense_fraction(seconds)
    wire.keyframe_insert('["turns"]',frame=frame)
    wire.keyframe_insert('["coil_radius"]',frame=frame)


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
    group = g.collection("Coil | Ten turns in the microscope wire area", scene)
    for obj in list(scene.objects):
        if obj.name.startswith("Sample cover") or obj.name.split(".")[0] == "Copper conductor 2" or obj.get("series_path") == 3:
            bpy.data.objects.remove(obj, do_unlink=True)
    lead = g.line("Ammeter series conductor 4", [current_demo.METER_PATH[-1], (-5, 2.2, SAMPLE_Z)], .115, mats["copper"], group)
    lead["series_path"] = 3
    g.line("Copper conductor 2", [(5, 2.2, SAMPLE_Z), (5, .5, .7)], .115, mats["copper"], group)
    enamel = mats["copper"].copy()
    enamel.name = "EM / enamel-insulated copper winding"
    enamel.node_tree.nodes.get("Principled BSDF").inputs["Coat Weight"].default_value = .7
    wire = build_winding(enamel, group)

    print("APPARATUS_READY",flush=True)
    coil_board.build(scene,mats)
    compasses = coil_compasses.build(scene, mats, camera)
    print("COMPASSES_READY",flush=True)
    field_group = g.collection("Coil | Combining magnetic fields", scene)
    coil_resultant_field.build(scene, mats, field_group)

    print("FIELD_DRAWINGS_READY",flush=True)
    current_guides = coil_current_guides.build(mats,field_group,group)

    coil_annotations.build(scene,mats,camera,field_group)
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

    for frame in frames((0,59),(65,86),(89,114),
                        (0,0),(125,125)):
        seconds = (frame-1)/demo.FPS
        combined = demo.field_fraction(seconds)
        current = demo.current_at(seconds)
        reading_board = False
        animate_winding(wire, seconds, frame)
        coil_compasses.animate(compasses, seconds, frame)
        turn = demo.smoothstep((seconds-demo.CELL_TURN_START)/(demo.CELL_TURN_END-demo.CELL_TURN_START))
        cell.rotation_euler.z = math.pi*turn
        cell.location.z = .7+.8*math.sin(math.pi*turn)
        cell.keyframe_insert("rotation_euler", frame=frame)
        cell.keyframe_insert("location", frame=frame)
        switch.rotation_euler.y = math.radians(-43)*(1-abs(current))
        switch.keyframe_insert("rotation_euler", frame=frame)
        coil_current_guides.animate(current_guides,seconds,frame,reading_board)
        for sign, obj in poles:
            obj.hide_render = obj.hide_viewport = seconds < demo.POLE_START or combined < .999 or current*sign <= .001 or reading_board
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
        for sign, obj in terminal_labels:
            obj.hide_render = obj.hide_viewport = current*sign <= .001
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
    coil_camera.animate(scene)
    print("COIL_GEOMETRY_AND_FIELDS_READY",flush=True)
    coil_experiments.build(scene,mats,camera)
    coil_fixed_view.arrange(scene)
    update_markers(scene)
    scene["audio_status"] = "Source storyboard; narrated build attaches the measured Indian-English tutor script."
    scene["physics"] = "10 then 20 turns; complete-circuit fields; ideal symmetric end-compass comparison with one common Earth field; illustrative core gain."
    scene["field_guides"] = "Paired local circles; axisymmetric finite-ring approximation in several planes; closed resultant loops; drawing density is illustrative."
    scene["wire_reconfiguration"] = "The experiment opens with a completed ten-turn coil; only the later ten-to-twenty-turn comparison changes the winding."
    scene["reference_amperes"] = .5
    scene.frame_set(1)
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 8
    DESTINATION.mkdir(parents=True, exist_ok=True)
    return scene
