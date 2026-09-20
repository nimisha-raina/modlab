"""Paired local field rings and conventional-current arrows for Case 2."""

import bpy
from mathutils import Vector
from . import coil_demo as demo, fields, geometry as g
from .field_layout import with_ammeter


def build(mats, field_group, coil_group):
    """Build two rings per circuit site and arrows on every visible branch."""
    branch_guides, circuit_arrows = [], []
    field_mats = dict(mats,ink_mint=mats["ink_cyan"])
    for name, center, electron_direction in with_ammeter():
        # The straight end connections slope gently toward the winding.
        if name in ("Far left", "Far right"):
            x = -4.25 if name == "Far left" else 4.25
            center = (x, demo.CENTER[1]+demo.RADIUS*(5-abs(x))/(5-demo.LENGTH/2), demo.CENTER[2])
            electron_direction = (1, demo.RADIUS/(5-demo.LENGTH/2)*(1 if x<0 else -1), 0)
        site = bpy.data.objects.new("Coil case field site | " + name, None)
        field_group.objects.link(site)
        site.location = center
        site.rotation_mode = "QUATERNION"
        rotation = Vector((1, 0, 0)).rotation_difference(
            Vector(electron_direction).normalized())
        objects = []
        for pair, radius in enumerate((.46, .68), 1):
            _, ring_objects = fields.guide(
                field_group, field_mats, f"Branch field pair {pair} | {name}", radius, .011)
            for obj in ring_objects:
                obj.parent = site
                obj["branch_field_pair"] = pair
            objects.extend(ring_objects)
        branch_guides.append((site, rotation, objects))

        direction = Vector(electron_direction).normalized()
        arrow_center = Vector(center) + Vector((0, 0, .16))
        for sign in (1, -1):
            conventional = -direction*sign
            arrow_objects = g.arrow(
                f"Conventional current on {name} | {sign}",
                arrow_center-conventional*.34, arrow_center+conventional*.34,
                .035, mats["ink_gold"], coil_group)
            for obj in arrow_objects:
                obj["conventional_current_arrow"] = True
                obj["circuit_site"] = name
            circuit_arrows.append((sign, arrow_objects))

    coil_arrows = []
    initial = demo.wire_points(1)
    dense = demo.dense_wire_points(1)
    # Equal arc-length samples lie on the copper helix rather than its axis.
    for slot, index in enumerate((135, 245, 355, 465, 575), 1):
        for sign in (1, -1):
            root = bpy.data.objects.new(
                f"Conventional current on winding {slot} | {sign}", None)
            coil_group.objects.link(root)
            root.rotation_mode = "QUATERNION"
            arrow_objects = g.arrow(
                "Conventional current along copper winding",
                (-.18, 0, 0), (.18, 0, 0), .030,
                mats["ink_gold"], coil_group)
            for obj in arrow_objects:
                obj.parent = root
                obj["conventional_current_arrow"] = True
                obj["winding_arrow"] = slot
            coil_arrows.append((sign, arrow_objects, root, index, initial, dense))
    return branch_guides, circuit_arrows, coil_arrows


def animate(data, seconds, frame, reading_board):
    branch_guides, circuit_arrows, coil_arrows = data
    current = demo.current_at(seconds)
    for site, rotation, objects in branch_guides:
        site.rotation_quaternion = rotation
        # Reflect one in-plane axis to reverse ring circulation.
        site.scale = (1, 1, -1 if current < 0 else 1)
        site.keyframe_insert("scale", frame=frame)
        for obj in objects:
            obj.hide_render = obj.hide_viewport = abs(current) < .001 or reading_board
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
    for sign, objects in circuit_arrows:
        for obj in objects:
            obj.hide_render = obj.hide_viewport = current*sign <= .001 or reading_board
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
    dense_fraction = demo.dense_fraction(seconds)
    for sign, objects, root, index, initial, dense in coil_arrows:
        def point(i):
            return Vector(initial[i]).lerp(Vector(dense[i]), dense_fraction)
        root.location = point(index)
        tangent = (point(index+1)-point(index-1)).normalized()*-sign
        root.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(tangent)
        root.keyframe_insert("location", frame=frame)
        root.keyframe_insert("rotation_quaternion", frame=frame)
        for obj in objects:
            obj.hide_render = obj.hide_viewport = current*sign <= .001 or reading_board
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)
