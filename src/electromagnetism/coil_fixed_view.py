"""Compose the physical board and whole circuit for a stationary lesson view."""
import bpy
from mathutils import Matrix
from . import coil_camera


def arrange(scene):
    coil_camera.animate(scene)
    root = bpy.data.objects.new("Fixed view | Laboratory board placement", None)
    scene.collection.objects.link(root)
    root.matrix_world = Matrix.Translation((0, -4, 2.5)) @ Matrix.Diagonal((1, 1, .72, 1))
    board_names = ("Chalkboard timber frame", "School science chalkboard", "Chalk ledge", "Board eraser")
    board_groups = ("Chalkboard |", "Coil | Magnetic regions on", "Coil | Applications on")
    for obj in list(scene.objects):
        on_board = obj.name.startswith(board_names) or any(c.name.startswith(board_groups) for c in obj.users_collection)
        if on_board and obj.parent is None:
            obj.parent = root
    scene["camera_layout"] = "Fixed, slightly elevated front view; physical board and complete apparatus together."
