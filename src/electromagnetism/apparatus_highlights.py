"""Timed tutor pointers identify apparatus without resembling magnetic rings."""

import bpy
from . import geometry as g
from .chalkboard import show_between

POINTS = {
    "battery": (-.45, -2.2, 1.4),
    "switch": (2.9, -2.2, 1.1),
    "copper wire": (0, 2.2, 1.6),
    "resistor": (5, -.1, .95),
    "series ammeter": (-5, 0, 2.4),
}


def build(scene, cues):
    group = g.collection("Tutor | Apparatus pointers", scene)
    material = bpy.data.materials.new("Tutor pointer | warm yellow")
    material.diffuse_color = (1, .72, .08, 1)
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    ink = tree.nodes.new("ShaderNodeEmission")
    ink.inputs[0].default_value = (1, .72, .08, 1)
    ink.inputs[1].default_value = 1.5
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(ink.outputs[0], output.inputs[0])
    for cue in cues:
        name = cue["component"]
        x, y, z = POINTS[name]
        objects = g.arrow("Tutor pointer | " + name, (x, y, z + 1.5),
                          (x, y, z + .15), .075, material, group)
        title = g.face_camera(g.text("Tutor component | " + name, name.title(),
                              (x, y, z + 1.7), .32, material, group, align="CENTER"), scene.camera)
        for obj in [*objects, title]:
            obj["tutor_component"] = name
            obj["cue_start"] = cue["start"]
            obj["cue_end"] = cue["end"]
            show_between(obj, cue["start"], cue["end"], scene.render.fps,
                         scene.frame_end / scene.render.fps)
    return group
