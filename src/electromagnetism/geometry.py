"""Small, reusable bpy modelling helpers. No external dependencies."""

import math
import bpy
from mathutils import Vector


def collection(name, scene):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result


def put(obj, name, group, material=None):
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    group.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj


def smooth(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def box(name, location, size, material, group, bevel=0.12):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = put(bpy.context.object, name, group, material)
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft corners", "BEVEL")
        modifier.width = bevel
        modifier.segments = 4
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def sphere(name, location, radius, material, group):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=12, radius=radius, location=location
    )
    return smooth(put(bpy.context.object, name, group, material))


def cylinder(name, start, end, radius, material, group, vertices=48):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2
    )
    obj = put(bpy.context.object, name, group, material)
    obj.rotation_euler = (b-a).to_track_quat("Z", "Y").to_euler()
    return smooth(obj)


def line(name, points, radius, material, group, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point, coord in zip(spline.points, points):
        point.co = (*coord, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    group.objects.link(obj)
    curve.materials.append(material)
    return obj


def arrow(name, start, end, radius, material, group):
    a, b = Vector(start), Vector(end)
    direction = (b-a).normalized()
    neck = b - direction * radius * 5
    shaft = cylinder(name + " / shaft", a, neck, radius, material, group)
    bpy.ops.mesh.primitive_cone_add(
        vertices=24, radius1=radius*2.8, radius2=0,
        depth=radius*5, location=(neck+b)/2,
    )
    head = put(bpy.context.object, name + " / arrowhead", group, material)
    head.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return [shaft, smooth(head)]


def ring_x(name, center, radius, thickness, material, group):
    x, y, z = center
    return line(name, [
        (x, y+radius*math.cos(a), z+radius*math.sin(a))
        for a in (i*2*math.pi/96 for i in range(96))
    ], thickness, material, group, cyclic=True)


def text(name, body, location, size, material, group, rotation=None, align="LEFT"):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.space_line = 1.2
    curve.extrude = 0.0
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    if rotation is not None:
        obj.rotation_euler = rotation
    group.objects.link(obj)
    curve.materials.append(material)
    return obj


def face_camera(obj, camera):
    obj.rotation_euler = camera.rotation_euler
    constraint = obj.constraints.new("COPY_ROTATION")
    constraint.name = "Keep this label facing the camera"
    constraint.target = camera
    return obj
