"""Reveal local field guides above each turn, then merge into the coil field."""

import math
import bpy
from mathutils import Vector
from . import coil_demo as demo, morph_geometry as morph
from .coil_field_transition import fading_material
from .coil_keyframes import frames


def build(scene, material, lower_guides):
    """Add local turn contributions; leave the final field drawing intact."""
    for obj in list(scene.objects):
        if obj.get("upper_winding_field"):
            bpy.data.objects.remove(obj, do_unlink=True)
    group = lower_guides[0].users_collection[0]
    ink, opacity_socket = fading_material(material, "EM / upper turn contributions")
    guides = []
    for index, lower in enumerate(lower_guides):
        u = (index+.25)/demo.TURNS
        straight_x = -4+8*u
        coil_x = -demo.LENGTH/2+demo.LENGTH*u
        final_key = lower.data.shape_keys.key_blocks["Combined solenoid field"]
        # Eight vertices form each tube cross-section. Their mean recovers
        # the existing centre line, so both guide sets meet the same field pose.
        final = [sum((final_key.data[j*8+k].co for k in range(8)), Vector())/8
                 for j in range(192)]
        for pair, radius in enumerate((.28,.40),1):
            straight, local = [], []
            for j in range(192):
                a = j*math.tau/192
                straight.append((straight_x, demo.CENTER[1]+.42*math.cos(a),
                                 demo.CENTER[2]+.42*math.sin(a)))
                # At the uppermost wire point the local field lies in XZ.
                local.append((coil_x+radius*math.cos(a), demo.CENTER[1],
                              demo.CENTER[2]+demo.RADIUS+radius*math.sin(a)))
            obj = morph.tube(f"Upper winding field guide {index+1} | pair {pair}",
                             {"Basis": straight, "Around wound wire": local,
                              "Combined solenoid field": final},
                             .010 if pair == 2 else .013, ink, group, cyclic=True)
            obj["upper_winding_field"] = True
            obj["turn_index"] = index
            obj["concentric_pair"] = pair
            guides.append(obj)
    for frame in frames((5,16)):
        seconds = (frame-1)/demo.FPS
        wound, combined = demo.coil_fraction(seconds), demo.field_fraction(seconds)
        reveal = demo.smoothstep((seconds-demo.CLOSE_START)/(demo.FIELD_START-demo.CLOSE_START))
        opacity = reveal*(1-combined)*abs(demo.current_at(seconds))
        opacity_socket.default_value = opacity
        opacity_socket.keyframe_insert("default_value", frame=frame)
        for obj in guides:
            morph.key_pose(obj, "Around wound wire", wound, frame)
            morph.key_pose(obj, "Combined solenoid field", 0., frame)
            obj.hide_render = obj.hide_viewport = opacity < .001
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
    scene["upper_field_guides"] = "Paired upper-wire circles appear with current and fade into the resultant field by 16 seconds."
    return guides
