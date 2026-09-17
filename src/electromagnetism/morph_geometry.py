"""Editable tube shape keys for continuous wire and field-guide transitions."""

import math
import bpy
from mathutils import Vector
from . import geometry as g


def tube_coordinates(points, radius, cyclic=False, sides=8):
    coordinates = []
    for i, point in enumerate(points):
        before = points[(i-1) % len(points)] if cyclic else points[max(0, i-1)]
        after = points[(i+1) % len(points)] if cyclic else points[min(len(points)-1, i+1)]
        tangent = (Vector(after)-Vector(before)).normalized()
        reference = Vector((0, 1, 0)) if abs(tangent.z) > .9 else Vector((0, 0, 1))
        normal = tangent.cross(reference).normalized()
        binormal = tangent.cross(normal).normalized()
        for side in range(sides):
            angle = side*2*math.pi/sides
            coordinates.append(Vector(point)+radius*(normal*math.cos(angle)+binormal*math.sin(angle)))
    return coordinates


def tube(name, paths, radius, material, group, cyclic=False):
    """paths map Basis and named poses to equally sampled centre lines."""
    sides = 8
    initial = next(iter(paths.values()))
    coordinates = tube_coordinates(initial, radius, cyclic, sides)
    faces = []
    for i in range(len(initial) if cyclic else len(initial)-1):
        for side in range(sides):
            a, b = i*sides+side, i*sides+(side+1) % sides
            next_i = (i+1) % len(initial)
            faces.append((a, b, next_i*sides+(side+1) % sides, next_i*sides+side))
    if not cyclic:
        faces.extend([tuple(reversed(range(sides))), tuple(range(len(coordinates)-sides, len(coordinates)))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(coordinates, [], faces)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    g.smooth(obj)
    obj.shape_key_add(name="Basis")
    for pose, points in list(paths.items())[1:]:
        key = obj.shape_key_add(name=pose)
        for vertex, coordinate in zip(key.data, tube_coordinates(points, radius, cyclic, sides)):
            vertex.co = coordinate
    return obj


def key_pose(obj, name, value, frame):
    key = obj.data.shape_keys.key_blocks[name]
    key.value = value
    key.keyframe_insert("value", frame=frame)
