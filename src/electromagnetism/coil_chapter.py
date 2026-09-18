"""Build Part 2: coils, polarity, iron core, clips and practical applications."""

import math
import bpy
from mathutils import Vector
from . import geometry as g, stage, circuit, chalkboard, compass, ammeter
from . import coil_demo as demo, current_demo, morph_geometry as morph
from .coil_upper_guides import build as build_upper_guides
from .coil_field_transition import build as build_field_transition, fading_material
from . import coil_board, coil_experiments, coil_camera, coil_annotations, coil_current_guides
from .coil_strength_guides import build as build_strength_guides
from .coil_keyframes import frames, CURRENT
from .build import clean_previous_lesson
from .config import OUTPUT, SAMPLE_Z
from .materials import make_materials

DESTINATION = OUTPUT / "parts" / "02_coil_reversal"


def update_markers(scene):
    scene.timeline_markers.clear()
    for seconds,title in ((0,"Ten-turn coil ready | Switch OFF"),
                          (5,"Switch ON | Conventional current arrows"),
                          (6,"Paired local field circles"),(12,"Local fields combine"),
                          (16,"3D field orbit"),(17,"Place smaller compasses"),
                          (26,"Switch OFF | Reverse directly"),(27,"Turn disconnected cell"),
                          (32,"Poles and blue arrows reversed"),(44,"Board | More turns"),
                          (51,"Switch OFF | Wind twenty turns"),(59,"Switch ON | Same 0.50 A"),
                          (66,"Switch OFF | Prepare iron core"),(68,"Insert nail from right"),
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

    coil_board.build(scene,mats)
    compasses = []
    for side, center in zip(("left", "right"), demo.COMPASS_CENTERS):
        needle = compass.build(scene, mats, center, demo.NORTH_ANGLE, on_stand=True)
        needle["coil_compass_side"] = side
        compass_group = needle.users_collection[0]
        placement = bpy.data.objects.new("Coil compass placement | " + side, None)
        compass_group.objects.link(placement)
        placement.location = center
        placement.scale = (demo.COMPASS_SCALE,demo.COMPASS_SCALE,1)
        for obj in list(compass_group.objects):
            if obj != placement and obj.parent is None:
                obj.parent = placement
                obj.location -= Vector(center)
            if obj != placement:
                chalkboard.show_between(obj, demo.COMPASS_START, demo.DURATION,
                                        demo.FPS, demo.DURATION)

        template = g.face_camera(g.text("Coil compass deflection", "0°", (center[0],center[1]-1.65,.13),
                                       .22,mats["ink_gold"],compass_group,align="CENTER"),camera)
        compass.animate_deflection_readings((None,template),demo.FPS,demo.DURATION,
            lambda t,c=center: None if t < demo.COMPASS_START else abs(demo.needle_angle_at(t,c)-demo.NORTH_ANGLE))
        reading_root = bpy.data.objects.new("Compass reading placement | "+side,None)
        compass_group.objects.link(reading_root)
        for obj in compass_group.objects:
            if "display_degrees" in obj:
                obj.parent = reading_root
        compasses.append((needle,placement,center,reading_root))
    field_group = g.collection("Coil | Combining magnetic fields", scene)
    traces = demo.solenoid_lines()
    dense_traces = demo.solenoid_lines(demo.DENSE_TURNS,demo.DENSE_RADIUS,8)
    core_traces = demo.solenoid_lines(demo.DENSE_TURNS,demo.DENSE_RADIUS,12)
    guides = []
    paths = []
    # Prepare local contributions and closed resultant drawings for a crossfade.
    for i in range(demo.TURNS):
        x = -demo.LENGTH/2+demo.LENGTH*(i+.5)/demo.TURNS
        straight, local, final, dense_final, core_final = [], [], [], [], []
        # Distinct meridional planes make the all-around field readable during
        # the right-side camera orbit. A plane and plane+pi would be duplicates.
        plane = (i % 5)*math.pi/5
        for j in range(192):
            a = j*2*math.pi/192
            straight.append((x, demo.CENTER[1]+.42*math.cos(a), SAMPLE_Z+.42*math.sin(a)))
            # At each turn's midpoint the wire tangent is nearly vertical.
            local.append((x+.28*math.cos(a), demo.CENTER[1]-demo.RADIUS+.28*math.sin(a), SAMPLE_Z))
            px, radial, _ = traces[i % len(traces)][j]
            final.append((px, demo.CENTER[1]+radial*math.cos(plane), SAMPLE_Z+radial*math.sin(plane)))
            px,radial,_ = dense_traces[(0,2,4,6,7)[i % 5]][j]
            dense_final.append((px,demo.CENTER[1]+radial*math.cos(plane),SAMPLE_Z+radial*math.sin(plane)))
            px,radial,_ = core_traces[(0,3,6,9,11)[i % 5]][j]
            core_final.append((px,demo.CENTER[1]+radial*math.cos(plane),
                               SAMPLE_Z+radial*math.sin(plane)))
        obj = morph.tube(f"Coil field guide {i+1}", {"Basis": straight, "Around wound wire": local,
                         "Combined solenoid field": final,"Dense coil field": dense_final,"Iron core field":core_final}, .013, mats["ink_mint"], field_group, cyclic=True)
        obj["field_guide"] = True
        guides.append(obj)
        paths.append((straight, local, final,dense_final,core_final))

    build_upper_guides(scene, mats["ink_mint"], guides)
    build_strength_guides(scene,mats,field_group,dense_traces,core_traces)

    current_guides = coil_current_guides.build(mats,field_group,group)

    # Separate arrow objects reverse direction while the field geometry stays.
    direction_objects = []
    for i in (0,4,5,9):
        points,dense_points,core_points = paths[i][2:]
        for sign in (1, -1):
            arrows = []
            root = bpy.data.objects.new(f"Moving field arrow | {i+1} | {sign}",None)
            field_group.objects.link(root)
            root.rotation_mode = "QUATERNION"
            arrows = g.arrow("Moving field direction",(-.22,0,0),(.22,0,0),.045,
                             mats["ink_gold" if sign == 1 else "ink_cyan"],field_group)
            for obj in arrows:
                obj.parent = root
            direction_objects.append((sign,arrows,root,points,dense_points,core_points))
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
        wound, combined = demo.coil_fraction(seconds), demo.field_fraction(seconds)
        current = demo.current_at(seconds)
        reading_board = (44 <= seconds <50 or 80 <= seconds <90 or seconds >=114)
        animate_winding(wire, seconds, frame)
        for needle, placement, center, reading_root in compasses:
            placed = demo.smoothstep((seconds-demo.COMPASS_START)/(demo.COMPASS_END-demo.COMPASS_START))
            placement.location = demo.compass_center_at(seconds,center)
            placement.location.z += (1-placed)*1.6
            reading_root.location.x = placement.location.x-center[0]
            reading_root.keyframe_insert("location",frame=frame)
            placement.keyframe_insert("location", frame=frame)
            angle = demo.needle_angle_at(seconds,center)
            # Arrive pointing to Earth's north, then settle toward the local
            # resultant field. Interpolate the shortest arc to avoid a spin.
            needle.rotation_euler.z = angle
            needle.keyframe_insert("rotation_euler", frame=frame)
            needle["current_multiplier"] = current
            needle.keyframe_insert('["current_multiplier"]', frame=frame)
        turn = demo.smoothstep((seconds-demo.CELL_TURN_START)/(demo.CELL_TURN_END-demo.CELL_TURN_START))
        cell.rotation_euler.z = math.pi*turn
        cell.location.z = .7+.8*math.sin(math.pi*turn)
        cell.keyframe_insert("rotation_euler", frame=frame)
        cell.keyframe_insert("location", frame=frame)
        switch.rotation_euler.y = math.radians(-43)*(1-abs(current))
        switch.keyframe_insert("rotation_euler", frame=frame)
        coil_current_guides.animate(current_guides,seconds,frame,reading_board)
        for sign, objects,root,points,dense_points,core_points in direction_objects:
            dense = demo.dense_fraction(seconds)
            coordinate = (8-sign*demo.flow_phase(seconds,sign)*192) % 192
            index = int(coordinate)
            u = coordinate-index
            def point(j):
                return Vector(points[j%192]).lerp(Vector(dense_points[j%192]),dense).lerp(Vector(core_points[j%192]),demo.core_fraction(seconds))
            root.location = point(index).lerp(point(index+1),u)
            tangent = (point(index+1)-point(index-1)).normalized()*-sign
            root.rotation_quaternion = Vector((1,0,0)).rotation_difference(tangent)
            root.keyframe_insert("location",frame=frame)
            root.keyframe_insert("rotation_quaternion",frame=frame)
            for obj in objects:
                obj.hide_render = obj.hide_viewport = combined < .999 or current*sign <= .001 or reading_board
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)
        for sign, obj in poles:
            obj.hide_render = obj.hide_viewport = seconds < demo.POLE_START or combined < .999 or current*sign <= .001 or reading_board
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
        for sign, obj in terminal_labels:
            obj.hide_render = obj.hide_viewport = current*sign <= .001
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
    coil_camera.animate(scene)
    build_field_transition(scene, guides)
    print("COIL_GEOMETRY_AND_FIELDS_READY",flush=True)
    coil_experiments.build(scene,mats,camera)
    update_markers(scene)
    scene["audio_status"] = "Silent visual review; final narration pending sequence approval."
    scene["physics"] = "10 then 20 turns; complete-circuit fields; ideal symmetric end-compass comparison with one common Earth field; illustrative core gain."
    scene["field_guides"] = "Paired local circles; axisymmetric finite-ring approximation in several planes; closed resultant loops; drawing density is illustrative."
    scene["wire_reconfiguration"] = "The experiment opens with a completed ten-turn coil; only the later ten-to-twenty-turn comparison changes the winding."
    scene["reference_amperes"] = .5
    scene.frame_set(1)
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 8
    DESTINATION.mkdir(parents=True, exist_ok=True)
    return scene
