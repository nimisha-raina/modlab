"""Reveal the resultant coil field without stretching individual field lines."""

import math
import bpy
from . import coil_demo as demo
from . import geometry as g
from .coil_keyframes import frames, CURRENT


def fading_material(material, name):
    ink = material.copy()
    ink.name = name
    nodes, links = ink.node_tree.nodes, ink.node_tree.links
    ink.node_tree.animation_data_clear()
    for node in list(nodes):
        if node.type in ("MIX_SHADER", "BSDF_TRANSPARENT"):
            nodes.remove(node)
    emission = next(n for n in nodes if n.type == "EMISSION")
    output = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    blend = nodes.new("ShaderNodeMixShader")
    blend.name = "Guide opacity"
    links.new(transparent.outputs[0], blend.inputs[1])
    links.new(emission.outputs[0], blend.inputs[2])
    links.new(blend.outputs[0], output.inputs["Surface"])
    return ink, blend.inputs[0]


def build_opening_guides(scene, material):
    """Show circular fields around the straight span before the switch opens."""
    for obj in list(scene.objects):
        if obj.get("opening_wire_field"):
            bpy.data.objects.remove(obj, do_unlink=True)
    group = g.collection("Coil | Straight wire opening field", scene)
    ink, opacity = fading_material(material, "EM / straight wire opening field")
    guides = []
    for i, x in enumerate((-1.2, 0., 1.2), 1):
        points = [(x, demo.CENTER[1]+.42*math.cos(j*math.tau/192),
                   demo.CENTER[2]+.42*math.sin(j*math.tau/192)) for j in range(193)]
        obj = g.line(f"Straight wire field circle {i}", points, .013, ink, group)
        obj["opening_wire_field"] = True
        guides.append(obj)
    for frame in frames(*CURRENT):
        seconds = (frame-1)/demo.FPS
        value = abs(demo.current_at(seconds)) if seconds < demo.OPEN_END else 0.
        opacity.default_value = value
        opacity.keyframe_insert("default_value", frame=frame)
        for obj in guides:
            obj.hide_render = obj.hide_viewport = value < .001
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)


def build(scene, guides):
    """Crossfade local contributions into the combined, closed field drawing."""
    for obj in list(scene.objects):
        if obj.get("local_lower_field"):
            bpy.data.objects.remove(obj, do_unlink=True)
    source = guides[0].data.materials[0]
    result_ink, result_opacity = fading_material(source, "EM / resultant coil field reveal")
    local_ink, local_opacity = fading_material(source, "EM / lower turn contributions")
    local_guides = []
    for guide in guides:
        local = guide.copy()
        local.data = guide.data.copy()
        local.animation_data_clear()
        del local["field_guide"]
        local["local_lower_field"] = True
        local.name = "Local lower contribution | " + guide.name
        guide.users_collection[0].objects.link(local)
        local.data.materials[0] = local_ink
        local_keys = local.data.shape_keys
        local_keys.animation_data_clear()
        local_keys.key_blocks["Around wound wire"].value = 1.
        local_keys.key_blocks["Combined solenoid field"].value = 0.
        local_keys.key_blocks["Dense coil field"].value = 0.
        local_keys.key_blocks["Iron core field"].value = 0.
        local_guides.append(local)
        guide.animation_data_clear()
        guide.data.materials[0] = result_ink
        keys = guide.data.shape_keys
        keys.animation_data_clear()
        keys.key_blocks["Around wound wire"].value = 0.
        keys.key_blocks["Combined solenoid field"].value = 1.
    for frame in frames(*CURRENT,(15,20),(51,56),(73,77)):
        seconds = (frame-1)/demo.FPS
        combined = demo.field_fraction(seconds)
        reveal = demo.smoothstep((seconds-demo.CLOSE_START)/(demo.FIELD_START-demo.CLOSE_START))
        current = abs(demo.current_at(seconds))
        dense = demo.dense_fraction(seconds)
        for guide in guides:
            keys = guide.data.shape_keys.key_blocks
            core = demo.core_fraction(seconds)
            for name, value in (("Combined solenoid field",1-dense),
                                ("Dense coil field",dense*(1-core)),("Iron core field",dense*core)):
                keys[name].value = value
                keys[name].keyframe_insert("value",frame=frame)
        for objects, socket, opacity in (
                (local_guides, local_opacity, reveal*(1-combined)*current),
                (guides, result_opacity, combined*current)):
            socket.default_value = opacity
            socket.keyframe_insert("default_value", frame=frame)
            for obj in objects:
                obj.hide_render = obj.hide_viewport = opacity < .001
                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)
    scene["field_transition"] = "Local turn contributions fade into a closed resultant pattern; guide lines do not stretch or physically join."
