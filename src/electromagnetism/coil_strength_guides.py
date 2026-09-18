"""Interleave stronger-field guides across each complete closed-loop family."""
import math
from . import coil_demo as demo, geometry as g, morph_geometry as morph
from .coil_field_transition import fading_material
from .coil_keyframes import frames, CURRENT


def world_points(trace, plane):
    return [(x,demo.CENTER[1]+r*math.cos(plane),demo.CENTER[2]+r*math.sin(plane))
            for x,r,_ in trace]


def build(scene, mats, group, dense_traces, core_traces):
    """Redistribute existing drawings as new ones appear, avoiding paired bands."""
    for phase,indices,amount in (("dense",(1,3,5),demo.dense_fraction),
                                ("core",(1,4,7,10),demo.core_fraction)):
        material,opacity = fading_material(mats["ink_mint"],"EM / "+phase+" strength guides")
        objects = []
        for slot,index in enumerate(indices):
            for plane in (0,math.pi):
                if phase == "dense":
                    obj = morph.tube("Additional coil field | dense",
                        {"Basis":world_points(dense_traces[index],plane),
                         "Iron core field":world_points(core_traces[(2,5,8)[slot]],plane+demo.CORE_GUIDE_ANGLE)},
                        .013,material,group,cyclic=True)
                else:
                    obj = g.line("Additional coil field | core",world_points(core_traces[index],plane+demo.CORE_GUIDE_ANGLE),
                                 .013,material,group,cyclic=True)
                obj["strength_stage"] = phase
                objects.append(obj)
        for frame in frames(*CURRENT,(51,56),(73,77)):
            seconds = (frame-1)/demo.FPS
            value = abs(demo.current_at(seconds))*amount(seconds)
            opacity.default_value = value
            opacity.keyframe_insert("default_value",frame=frame)
            for obj in objects:
                keys = getattr(obj.data,"shape_keys",None)
                if keys:
                    key = keys.key_blocks["Iron core field"]
                    key.value = demo.core_fraction(seconds)
                    key.keyframe_insert("value",frame=frame)
                obj.hide_render = obj.hide_viewport = value < .001
                obj.keyframe_insert("hide_render",frame=frame)
                obj.keyframe_insert("hide_viewport",frame=frame)
