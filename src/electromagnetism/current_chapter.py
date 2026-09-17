"""Build the independent compass/current chapter from shared laboratory assets."""

import json
import math
import bpy
from mathutils import Vector
from . import geometry as g, stage, circuit, chalkboard, compass, fields, ammeter
from . import current_demo as demo
from .build import clean_previous_lesson
from .config import OUTPUT, LESSON
from .field_layout import first_case_guides, comparison_radii
from .materials import make_materials

DESTINATION = OUTPUT / "parts" / "01_compass_current"


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
    # This section uses the closed, opaque wire and physical apparatus labels.
    cover = next(o for o in scene.objects if o.name.startswith("Sample cover"))
    tree = cover.data.materials[0].node_tree
    tree.animation_data_clear()
    next(node for node in tree.nodes if node.type == "MIX_SHADER").inputs[0].default_value = 0
    for obj in scene.objects:
        if obj.type == "FONT":
            obj.animation_data_clear()
            obj.hide_render = obj.hide_viewport = False

    reading = ammeter.build(scene, mats)
    ammeter.animate(reading, demo.FPS, demo.DURATION, demo.current_at)

    chalkboard.build(scene, mats, [
        {"start": 0, "end": 10, "case": "CURRENT AND COMPASS",
         "heading": "A compass detects the magnetic field",
         "observation": "The current is already flowing."},
        {"start": 10, "end": demo.SUMMARY_START, "case": "DOUBLING THE CURRENT",
         "heading": "More current. Stronger magnetic field.",
         "observation": "Same wire. Same compass position."},
        {"start": demo.SUMMARY_START, "end": demo.DURATION, "case": "EXPERIMENT SUMMARY",
         "heading": "What we learned", "points": demo.SUMMARY_POINTS},
    ])
    needle = compass.build(scene, mats, demo.COMPASS_CENTER, demo.NORTH_ANGLE)
    indicator = compass.deflection_indicator(scene, mats, demo.COMPASS_CENTER,
                                             demo.NORTH_ANGLE, demo.compass_angle(2))
    compass_group = needle.users_collection[0]
    placement = bpy.data.objects.new("Compass | placement motion", None)
    compass_group.objects.link(placement)
    for obj in list(compass_group.objects):
        if obj != placement and obj.parent is None:
            obj.parent = placement
    for obj in compass_group.objects:
        if obj != placement:
            chalkboard.show_between(obj, demo.PLACEMENT_START, demo.DURATION, demo.FPS, demo.DURATION)
    group = g.collection("Current comparison | local field guides", scene)
    guide_sets = [[], []]
    for name, center, direction in first_case_guides():
        site = bpy.data.objects.new("Current field site | " + name, None)
        group.objects.link(site)
        site.location = center
        site.rotation_mode = "QUATERNION"
        site.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(Vector(direction).normalized())
        for level, radii in enumerate(comparison_radii(name)):
            for index, radius in enumerate(radii):
                ring, objects = fields.guide(group, mats, f"Current field {level+1}.{index+1} | {name}", radius, .012)
                ring["current_level"] = level+1
                ring["field_location"] = name
                for obj in objects:
                    obj.parent = site
                    guide_sets[level].append(obj)

    # Animate the existing series limiter's control to accompany the setting.
    control_group = g.collection("Current comparison | series control", scene)
    knob = g.cylinder("Series current control knob", (5, -.1, .94), (5, -.1, 1.12), .16, mats["rubber"], control_group)
    notch = g.line("Current knob index", [(0, 0, 0), (.12, 0, 0)], .012, mats["ink_white"], control_group)
    notch.parent = knob
    notch.location = (0, 0, .10)

    for frame in range(1, scene.frame_end+1):
        seconds = (frame-1)/demo.FPS
        current = demo.current_at(seconds)
        camera.location, target = demo.camera_pose(seconds)
        stage.point_at(camera, target)
        camera.keyframe_insert("location", frame=frame)
        camera.keyframe_insert("rotation_euler", frame=frame)
        placement.location = demo.placement_offset(seconds)
        placement.keyframe_insert("location", frame=frame)
        needle.rotation_euler.z = demo.compass_angle(current, demo.compass_position(seconds))
        needle.keyframe_insert("rotation_euler", frame=frame)
        needle["current_multiplier"] = current
        needle.keyframe_insert('["current_multiplier"]', frame=frame)
        angle = demo.NORTH_ANGLE-needle.rotation_euler.z
        compass.key_deflection(indicator, angle, frame)
        knob.rotation_euler.z = -(current-1)*math.pi/2
        knob.keyframe_insert("rotation_euler", frame=frame)
        for level, objects in enumerate(guide_sets):
            for obj in objects:
                obj.hide_render = obj.hide_viewport = current <= level+.001
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)

    compass.animate_deflection_readings(indicator, demo.FPS, demo.DURATION,
        lambda t: None if t < demo.PLACEMENT_END else
        demo.NORTH_ANGLE-demo.compass_angle(demo.current_at(t)))

    for seconds, title in [(0, "Continue from opening | switch closed"), (.5, "Place compass"),
                           (5, "Compass settled | current 0.50 A"),
                           (8, "Compare | I"), (10, "Read the board | Double current"),
                           (14, "Double current"), (18, "Compare | 2I"), (21, "Restore current I"),
                           (24, "Return to the board"), (demo.SUMMARY_START, "What we learned")]:
        scene.timeline_markers.new(title, frame=round(seconds*demo.FPS)+1)
    scene["chapter"] = "Part 1 | Compass and current"
    scene["audio_status"] = "Silent visual review; record male Indian-English narration after sequence review."
    scene["physics"] = "Finite circuit field plus a fixed horizontal Earth field; horizontal needle; relative current."
    scene["field_guides"] = "Six locations: original three circles plus five guides at I; doubled drawn count at 2I."
    scene["compass_position"] = demo.COMPASS_CENTER
    scene["join_source_seconds"] = LESSON.wide_view
    scene["reference_amperes"] = demo.REFERENCE_AMPS
    scene["north_angle"] = demo.NORTH_ANGLE
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.overlay.show_overlays = False
                area.spaces.active.shading.type = "MATERIAL"
    DESTINATION.mkdir(parents=True, exist_ok=True)
    (DESTINATION / "build-info.json").write_text(json.dumps({
        "scene": demo.SCENE_NAME, "fps": demo.FPS, "duration": demo.DURATION,
        "audio": "Silent visual review", "reference_amperes": demo.REFERENCE_AMPS,
        "double_amperes": 2*demo.REFERENCE_AMPS, "placement_end_seconds": demo.PLACEMENT_END,
        "join_source_seconds": LESSON.wide_view, "compass_degrees": {
            str(i): round(math.degrees(demo.NORTH_ANGLE-demo.compass_angle(i)), 3)
            for i in (0, 1, 2)},
    }, indent=2)+"\n", encoding="utf-8")
    return scene
