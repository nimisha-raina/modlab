"""Local wire circles and three evenly distributed, closed solenoid drawings.

The line count is a teaching convention, not a magnetic-flux measurement.
Directions follow the right-hand rule for conventional current.
"""
import math
import bpy
from mathutils import Vector
from . import coil_demo as demo, geometry as g, fields
from .coil_field_transition import fading_material
from .coil_keyframes import frames, CURRENT


def world_points(trace, plane):
    return [(x,demo.CENTER[1]+r*math.cos(plane),demo.CENTER[2]+r*math.sin(plane))
            for x,r,_ in trace]


def build(scene, mats, group):
    local_material, local_opacity = fading_material(mats["ink_cyan"], "EM / local wire contributions")
    local_mats = dict(mats, ink_mint=local_material)
    local = []
    for turn in range(demo.TURNS):
        for phase in (.25,.50):
            u = (turn+phase)/demo.TURNS
            angle = math.tau*demo.TURNS*u
            root = bpy.data.objects.new("Local winding field site",None)
            group.objects.link(root)
            root.location = (-demo.LENGTH/2+demo.LENGTH*u,
                             demo.CENTER[1]+demo.RADIUS*math.cos(angle),
                             demo.CENTER[2]+demo.RADIUS*math.sin(angle))
            tangent = Vector((demo.LENGTH,-demo.RADIUS*math.tau*demo.TURNS*math.sin(angle),
                              demo.RADIUS*math.tau*demo.TURNS*math.cos(angle))).normalized()
            root.rotation_mode = "QUATERNION"
            root.rotation_quaternion = Vector((1,0,0)).rotation_difference(tangent)
            root["electron_tangent"] = tuple(tangent)
            for pair,radius in enumerate((.24,.36),1):
                _, objects = fields.guide(group,local_mats,"Local winding concentric field",radius,.011)
                for obj in objects:
                    obj.parent = root
                    obj["local_winding_pair"] = pair
                local.extend(objects)

    families = []
    # Each plane contains several nested finite-ring traces. Rebuild each
    # strength family as a whole, so new lines do not bunch beside old lines.
    for stage,count in enumerate((2,4,6)):
        material, opacity = fading_material(mats["ink_cyan"], f"EM / field strength {stage}")
        traces = demo.solenoid_lines(seed_count=count)
        objects, arrows = [], []
        for plane_index in range(5):
            plane = math.tau*plane_index/5
            for index,trace in enumerate(traces):
                points = world_points(trace,plane)
                obj = g.line(f"Closed solenoid field | stage {stage} | plane {plane_index} | {index}",
                             points,.012,material,group,cyclic=True)
                obj["resultant_stage"] = stage
                obj["field_plane"] = plane
                objects.append(obj)
                if index != count-1 or plane_index not in (1,3):
                    continue
                # Tangent arrows on the broad outer return, clear of copper.
                for coordinate in (max(range(len(trace)), key=lambda k: trace[k][1]),):
                    center = Vector(points[coordinate])
                    tangent = (Vector(points[(coordinate+1)%192])-Vector(points[coordinate-1])).normalized()
                    for sign in (1,-1):
                        # Ring tracing uses +X current; this circuit starts -X.
                        direction = tangent*-sign
                        parts = g.arrow("Magnetic field tangent",center-.17*direction,center+.17*direction,
                                        .036,material,group)
                        for part in parts:
                            part["magnetic_field_arrow"] = True
                        arrows.append((sign,parts))
        families.append((stage,opacity,objects,arrows))

    for frame in frames(*CURRENT,(5,16),(51,56),(68,72)):
        seconds = (frame-1)/demo.FPS
        current = demo.current_at(seconds)
        combined = demo.field_fraction(seconds)
        value = demo.ramp(seconds,5,8)*(1-combined)*abs(current)
        local_opacity.default_value = value
        local_opacity.keyframe_insert("default_value",frame=frame)
        for obj in local:
            obj.hide_render = obj.hide_viewport = value < .001
            obj.keyframe_insert("hide_render",frame=frame)
            obj.keyframe_insert("hide_viewport",frame=frame)
        dense, core = demo.dense_fraction(seconds), demo.core_fraction(seconds)
        weights = (1-dense,dense*(1-core),dense*core)
        for stage,opacity,objects,arrows in families:
            value = weights[stage]*combined*abs(current)
            opacity.default_value = value
            opacity.keyframe_insert("default_value",frame=frame)
            for obj in objects:
                obj.hide_render = obj.hide_viewport = value < .001
                obj.keyframe_insert("hide_render",frame=frame)
                obj.keyframe_insert("hide_viewport",frame=frame)
            for sign,parts in arrows:
                for obj in parts:
                    obj.hide_render = obj.hide_viewport = value < .001 or current*sign <= 0
                    obj.keyframe_insert("hide_render",frame=frame)
                    obj.keyframe_insert("hide_viewport",frame=frame)
    scene["resultant_line_counts"] = "10 / 20 / 30 illustrative closed traces in five meridional planes"
    scene["field_transition"] = "Local contributions fade into the resultant; field lines do not physically join."
