"""Shared checks for the saved analogue instrument, not its construction code."""

from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from electromagnetism import current_demo as demo


def check_ammeter(scene, amperes, framed=False):
    pointer = next(o for o in scene.objects if o.get("analogue_pointer"))
    root = pointer.parent
    assert root["scale_min_amperes"] == -1 and root["scale_max_amperes"] == 1
    assert (root.matrix_world.translation-Vector(demo.AMMETER_CENTER)).length < 1e-6
    assert abs(pointer["needle_amperes"]-amperes) < 1e-6
    assert abs(pointer.rotation_euler.z-demo.meter_angle(amperes)) < 1e-6
    housing = next(o for o in scene.objects if o.name.startswith("Ammeter round black housing"))
    assert housing.parent == root
    assert len([o for o in scene.objects if o.name.startswith("Ammeter scale graduation")]) == 41
    assert root["connection_layout"] == "concealed rear terminals"
    assert not any("insulated_lead" in o for o in scene.objects)
    assert len([o for o in scene.objects if o.get("rear_connection")]) == 2
    assert all(o.hide_render for o in scene.objects if o.get("rear_connection"))
    assert len([o for o in scene.objects if "series_path" in o]) == 4
    face = next(o for o in scene.objects if o.name.startswith("Ammeter white analogue dial"))
    bezel = next(o for o in scene.objects if o.name.startswith("Ammeter raised black bezel"))
    face_depth = min(v.co.z for v in face.data.vertices)
    bezel_depth = max((bezel.matrix_local @ Vector(c)).z for c in bezel.bound_box)
    assert face_depth-bezel_depth >= .03, "Dial face too close to black bezel"
    assert all(len(p.vertices) == 3 for p in face.data.polygons)
    assert pointer.location.z > face_depth+.02
    assert scene.camera.data.clip_start >= .05
    if framed:
        for corner in housing.bound_box:
            uv = world_to_camera_view(scene, scene.camera, housing.matrix_world @ Vector(corner))
            assert .02 < uv.x < .98 and .02 < uv.y < .98, ("Meter clipped", tuple(uv))
