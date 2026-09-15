"""A practical school laboratory surrounding the original teaching circuit.

All furniture uses simple reusable bpy geometry and procedural materials.
The circuit remains the focus; the room gives it familiar real-world context.
"""
import math
from . import geometry as g


def bench(group, mats, x, y, width=14, depth=9):
    g.box("Stone laboratory worktop", (x, y, -0.28), (width, depth, 0.5), mats["worktop"], group, .08)
    g.box("Hardwood bench apron", (x, y, -0.75), (width-.25, depth-.25, .5), mats["wood"], group, .04)
    for dx in (-width/2+.6, width/2-.6):
        for dy in (-depth/2+.6, depth/2-.6):
            g.box("Bench timber leg", (x+dx, y+dy, -2.7), (.5, .5, 4), mats["wood"], group, .04)
    g.box("Bench lower rail", (x, y+depth/2-.6, -3.8), (width-1, .28, .3), mats["wood"], group, .025)


def build(scene, mats):
    group = g.collection("06 | Indian school science laboratory", scene)
    bench(group, mats, 0, 0)
    g.box("Tiled lab floor", (0, 0, -5.05), (60, 55, .35), mats["floor"], group, 0)
    for x in range(-28, 30, 3):
        g.box("Floor grout", (x, 0, -4.871), (.018, 55, .005), mats["grout"], group, 0)
    for y in range(-25, 29, 3):
        g.box("Floor grout", (0, y, -4.871), (60, .018, .005), mats["grout"], group, 0)
    g.box("School plaster wall", (0, 12, 2), (60, .35, 14), mats["plaster"], group, .02)
    g.box("Green lower wall paint", (0, 11.8, -2), (60, .06, 6), mats["wall_green"], group, 0)
    g.box("Wall skirting", (0, 11.73, -4.5), (60, .12, .55), mats["wood"], group, .02)
    # Familiar tall windows with painted timber frames and metal grilles.
    for x in (-13, 13):
        g.box("Window daylight", (x, 11.73, 3.5), (7.4, .08, 8), mats["window_light"], group, 0)
        for dx in (-3.9, 0, 3.9):
            g.box("Window frame upright", (x+dx, 11.56, 3.5), (.16, .28, 8.4), mats["window_frame"], group, .025)
        for z in (-.7, 3.5, 7.7):
            g.box("Window frame horizontal", (x, 11.56, z), (8, .28, .16), mats["window_frame"], group, .025)
        for dx in (-2.6, -1.3, 1.3, 2.6):
            g.cylinder("Window safety grille", (x+dx,11.4,-.5), (x+dx,11.4,7.5), .035, mats["silver"], group)
        g.box("Window sill", (x, 11.15, -.8), (8.4, .9, .2), mats["plaster"], group, .03)
    # Painted chalkboard, chalk ledge and understated class label.
    g.box("Chalkboard timber frame", (0, 11.4, 3.25), (14.3, .35, 7), mats["wood"], group, .07)
    g.box("School science chalkboard", (0, 11.15, 3.25), (13.8, .08, 6.5), mats["chalkboard"], group, .02)
    for body, z, size in [("SCIENCE LABORATORY", 5.5, .62), ("CLASS VIII", 4.35, .42), ("Electricity & Magnetism", 2.8, .52)]:
        g.text("Chalkboard / "+body, body, (0,11.08,z), size, mats["chalk"], group,
               rotation=(math.pi/2,0,0), align="CENTER")
    g.box("Chalk ledge", (0, 10.85, .05), (14, .5, .15), mats["wood"], group, .03)
    g.box("Board eraser", (4.5, 10.85, .2), (.7, .3, .18), mats["rubber"], group, .025)
    bench(group, mats, -17, 5, 9, 5)
    bench(group, mats, 17, 5, 9, 5)
    for x in (-11, 11):
        g.cylinder("Lab stool seat", (x,2,-2), (x,2,-1.8), 1.1, mats["wood"], group)
        for dx, dy in ((-.6,-.6),(.6,-.6),(0,.7)):
            g.cylinder("Stool steel leg", (x+dx,2+dy,-4.85), (x+dx*.8,2+dy*.8,-2), .08, mats["silver"], group)
    return group
