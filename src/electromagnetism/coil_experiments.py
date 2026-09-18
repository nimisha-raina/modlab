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
    caption = g.face_camera(g.text("Paper clip experiment caption","IRON PAPER CLIPS",(0,.3,.20),
                                  .25,mats["ink_white"],group,align="CENTER"),camera)
    chalkboard.show_between(caption,104,114,demo.FPS,demo.DURATION)
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
        chalkboard.show_between(obj,101,demo.DURATION,demo.FPS,demo.DURATION)
        clips.append((i,clip))
    for frame in frames(*CURRENT,(73,77),(101,107),(112,112+demo.CLIP_FALL_DURATION)):
        seconds = (frame-1)/demo.FPS
        nail.location = (-4*(1-demo.core_fraction(seconds)),demo.CENTER[1],demo.CENTER[2])
        nail.keyframe_insert("location",frame=frame)
        for on,obj in switches:
            obj.hide_render = obj.hide_viewport = (abs(demo.current_at(seconds))>.001) != on
            obj.keyframe_insert("hide_render",frame=frame)
            obj.keyframe_insert("hide_viewport",frame=frame)
        for i,clip in clips:
            side = -1 if i < 3 else 1
            n = i % 3
            start = Vector((side*(2.6+.20*n),.85+.30*n,.035))
            hanging = Vector((side*(1.94+.07*n),2.08+.09*(n-1),1.29))
            brought = demo.ramp(seconds,101,104)
            attracted = demo.ramp(seconds,104,107)
            drop_time = max(0.,seconds-112)
            drop = min(1.,(drop_time/demo.CLIP_FALL_DURATION)**2)
            clip.location = start+Vector((0,-1.8*(1-brought),.65*(1-brought)))
            if seconds >=104:
                clip.location = start+(hanging-start)*attracted
                clip.location.z += .18*math.sin(math.pi*attracted)
            if seconds >=112:
                clip.location = hanging+(start-hanging)*drop
            clip.rotation_euler = (math.pi/2*attracted*(1-drop),0,.18*(n-1)*(1-attracted+drop))
            clip.keyframe_insert("location",frame=frame)
            clip.keyframe_insert("rotation_euler",frame=frame)
    return nail, clips
