"""Soft-iron core, switch-state labels and attracted paper clips."""

import math
import bpy
from mathutils import Vector
from . import geometry as g, chalkboard, coil_demo as demo
from .coil_keyframes import frames, CURRENT


def build(scene, mats, camera):
    group = g.collection("Coil | Core and paper clip experiments", scene)
    steel = mats["silver"].copy()
    steel.name = "EM / soft iron"
    steel.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (.19,.21,.22,1)
    nail = bpy.data.objects.new("Soft-iron nail placement", None)
    group.objects.link(nail)
    nail["soft_iron_core"] = True
    parts = [g.cylinder("Soft-iron nail shaft", (-1.9,0,0),(1.9,0,0),.115,steel,group),
             g.cylinder("Soft-iron nail head", (-2.05,0,0),(-1.88,0,0),.235,steel,group)]
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.115,radius2=0,depth=.3,location=(2.05,0,0))
    tip = g.put(bpy.context.object,"Soft-iron nail point",group,steel)
    tip.rotation_euler.y = math.pi/2
    parts.append(tip)
    for obj in parts:
        obj.parent = nail
        chalkboard.show_between(obj,demo.CORE_START,demo.DURATION,demo.FPS,demo.DURATION)
    switches = []
    for on in (False,True):
        obj = g.face_camera(g.text("Switch state | "+str(on),"SWITCH ON" if on else "SWITCH OFF",
                                  (3.1,-2.8,.70),.27,mats["ink_mint" if on else "ink_white"],group,align="CENTER"),camera)
        obj["switch_on"] = on
        switches.append((on,obj))
    clips = []
    clip_metal = mats["silver"].copy()
    clip_metal.name = "EM / polished iron paper clips"
    shader = clip_metal.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (.72,.77,.82,1)
    shader.inputs["Roughness"].default_value = .27
    for i in range(6):
        clip = bpy.data.objects.new(f"Iron paper clip placement {i+1}",None)
        group.objects.link(clip)
        clip["paper_clip"] = True
        # Two rounded loops and the open inner tip form a recognisable clip.
        points = []
        for radius, length, offset in ((.11,.19,0),(.065,.15,.015)):
            loop = [(radius*math.cos(j*math.tau/64),
                     length*(1 if math.sin(j*math.tau/64)>=0 else -1)+radius*math.sin(j*math.tau/64)+offset,0)
                    for j in range(65)]
            points.extend(loop)
        obj = g.line("Iron paper clip wire",points,.018,clip_metal,group)
        obj.parent = clip
        chalkboard.show_between(obj,99,demo.DURATION,demo.FPS,demo.DURATION)
        clips.append((i,clip))
    for frame in frames(*CURRENT,(68,72),(99,107),(112,112+demo.CLIP_FALL_DURATION)):
        seconds = (frame-1)/demo.FPS
        nail.location = (-4*(1-demo.core_fraction(seconds)),demo.CENTER[1],demo.CENTER[2])
        nail.keyframe_insert("location",frame=frame)
        for on,obj in switches:
            obj.hide_render = obj.hide_viewport = (abs(demo.current_at(seconds))>.001) != on
            obj.keyframe_insert("hide_render",frame=frame)
            obj.keyframe_insert("hide_viewport",frame=frame)
        for i,clip in clips:
            n = i-2.5
            x,y = demo.clip_site(i)
            start = Vector((x,y,.035))
            hanging = Vector((x,y,1.29))
            attracted = demo.ramp(seconds,103,107)
            # Release begins as the switch opens, then continues for a clearly
            # visible 2.5 seconds before the summary-board transition.
            drop_time = max(0.,seconds-111)
            drop = min(1.,(drop_time/demo.CLIP_FALL_DURATION)**2)
            # Clips rest below the nail and rise only after current establishes
            # the stronger core field; there is no sideways arrival animation.
            clip.location = start
            if seconds >=103:
                clip.location = start+(hanging-start)*attracted
                clip.location.z += .18*math.sin(math.pi*attracted)
            if seconds >=111:
                clip.location = hanging+(start-hanging)*drop
            clip.rotation_euler = (math.pi/2*attracted*(1-drop),0,.10*n*(1-attracted+drop))
            clip.keyframe_insert("location",frame=frame)
            clip.keyframe_insert("rotation_euler",frame=frame)
    return nail, clips
