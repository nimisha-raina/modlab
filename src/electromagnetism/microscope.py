"""Compact copper ions and sparse, visible electrons inside the actual wire."""

import math
import bpy
from . import geometry as g
from .config import LESSON, MICRO_ORIGIN, MICRO_SCALE, ELECTRON_RADIUS
from .motion import electron_position, ion_position, key_location, visibility


def build(scene, mats, camera):
    group = g.collection("03 | Inside copper - teaching model", scene)
    root = bpy.data.objects.new("Microscope | anchored inside wire", None)
    group.objects.link(root)
    root.location = MICRO_ORIGIN
    root.scale = (MICRO_SCALE,)*3

    def local(obj):
        obj.parent = root
        return obj

    def reveal_particle(obj):
        # Reveal both populations together only after reaching the cutaway.
        # Hide them together when the cover starts closing during pullback.
        visibility(obj, LESSON.frame(LESSON.microscope_in),
                   LESSON.frame(LESSON.microscope_out)-1)

    # Open lower shell, revealed as the normal wire surface fades away.
    angles = [math.radians(-165+i*180/40) for i in range(41)]
    vertices = [(x, 1.12*math.cos(a), 1.12*math.sin(a))
                for x in (-5.15, 5.15) for a in angles]
    mesh = bpy.data.meshes.new("Copper half-shell")
    mesh.from_pydata(vertices, [], [(i, i+1, i+42, i+41) for i in range(40)])
    shell = bpy.data.objects.new("Copper cutaway shell", mesh)
    group.objects.link(shell)
    local(shell)
    mesh.materials.append(mats["copper"])
    solidify = shell.modifiers.new("Thin cutaway wall", "SOLIDIFY")
    solidify.thickness = 0.025
    g.smooth(shell)
    visibility(shell, LESSON.frame(LESSON.microscope_in-1.2),
               LESSON.frame(LESSON.microscope_out+1)-1)
    for x in (-5.15, 5.15):
        rim = local(g.line("Cutaway rim", [(x, 1.13*math.cos(a), 1.13*math.sin(a)) for a in angles],
                     0.032, mats["copper_light"], group))
        visibility(rim, LESSON.frame(LESSON.microscope_in-1.2),
                   LESSON.frame(LESSON.microscope_out+1)-1)

    # Compact spacing is constant in this laboratory-frame illustration.
    # Closing the switch does not contract the positive lattice.
    for col in range(9):
        for row in range(2):
            for layer in range(2):
                index = col*4+row*2+layer
                base = (-3.8+col*0.95, -0.23+row*0.6, -0.30+layer*0.60)
                obj = local(g.sphere(f"Copper ion {index+1:02}", base, 0.205, mats["copper_light"], group))
                obj["rest_position"] = base
                reveal_particle(obj)
                for frame in range(1, LESSON.last_frame+1, 3):
                    key_location(obj, frame, ion_position(base, index, (frame-1)/LESSON.fps))

    for index in range(LESSON.electrons):
        obj = local(g.sphere(f"Mobile electron {index+1:02}", (0, 0, 0), ELECTRON_RADIUS / MICRO_SCALE, mats["ink_cyan"], group))
        reveal_particle(obj)
        for frame in range(1, LESSON.last_frame+1):
            point = electron_position(index+LESSON.seed, (frame-1)/LESSON.fps)
            key_location(obj, frame, point)
    return root
