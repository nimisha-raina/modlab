"""Cameras and soft studio lighting for an uncluttered classroom view."""

import bpy
from mathutils import Vector
from . import geometry as g
from .config import LESSON, MICRO_ORIGIN, QUALITY
from .camera_path import camera_pose
from . import laboratory


def point_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, group):
    data = bpy.data.cameras.new(name)
    data.lens = 45
    # The microscopic camera stays well outside this distance. A larger near
    # plane preserves depth precision for instrument faces in the lab overview.
    data.clip_start = 0.05
    data.clip_end = 250
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    obj.location = location
    point_at(obj, target)
    return obj


def area(name, location, target, power, size, color, group):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    obj.location = location
    point_at(obj, target)


def setup(scene, mats, quality):
    group = g.collection("00 | Stage and cameras", scene)
    preset = QUALITY[quality]
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = preset["samples"]
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = preset["resolution"]
    scene.render.resolution_percentage = 100
    scene.render.fps = LESSON.fps
    scene.frame_start = 1
    scene.frame_end = LESSON.last_frame
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    world = bpy.data.worlds.new("EM | School laboratory daylight")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.65, 0.8, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    scene.world = world

    laboratory.build(scene, mats)

    macro = camera("Camera | Continuous lesson", (3, -20, 16), (0, 0, 0.5), group)
    scene.camera = macro
    for frame in range(1, LESSON.last_frame+1):
        location, target = camera_pose((frame-1)/LESSON.fps)
        macro.location = location
        point_at(macro, target)
        macro.keyframe_insert("location", frame=frame)
        macro.keyframe_insert("rotation_euler", frame=frame)

    for seconds, label in [
        (0, "01  Explore the circuit"),
        (LESSON.microscope_in, "02  Inside the copper"),
        (LESSON.switch_on, "03  Switch closes"),
        (LESSON.field_reveal, "04  Reveal three concentric field guides"),
        (LESSON.microscope_out, "05  Slow pullback begins"),
        (LESSON.zoom_out_end, "06  Original view restored"),
        (LESSON.switch_off, "07  Switch opens"),
    ]:
        scene.timeline_markers.new(label, frame=LESSON.frame(seconds))

    area("Window daylight", (-9, 6, 9), (0,0,0), 2600, 7, (.87,.93,1), group)
    area("Soft front fill", (2,-7,9), (0,0,0), 1500, 8, (1,.9,.76), group)
    area("Ceiling bounce", (5,4,11), (0,2,0), 1800, 6, (1,.96,.87), group)
    scene.frame_set(1)
    return macro
