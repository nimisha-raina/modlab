"""Experiment headings, magnetic-region model and illustrated applications."""

import math
import bpy
from . import chalkboard, geometry as g, coil_demo as demo
from .config import ROOT

SUMMARY = ["A current-carrying coil has north and south poles.",
           "Reversing current swaps the poles.",
           "More turns at the same current strengthen the field.",
           "An iron core makes the electromagnet stronger.",
           "Switching off releases the paper clips."]


def build(scene, mats):
    # Allow board-only revisions without rebuilding the winding or apparatus.
    for collection in list(scene.collection.children):
        if collection.name.startswith(("Chalkboard | Demonstration headings",
                "Coil | Magnetic regions on the laboratory board", "Coil | Applications on the laboratory board")):
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.collections.remove(collection)
    cases = [
        {"start": 0, "end": 5, "case": "MAGNETIC FIELD OF A COIL",
         "heading": "10 turns | Switch OFF",
         "observation": "Watch the current, field and compass needles."},
        {"start": 5, "end": 12, "case": "CLOSE THE SWITCH",
         "heading": "Current flows through the copper wire",
         "observation": "Yellow: conventional current, from + to -."},
        {"start": 12, "end": 26, "case": "MAGNETIC FIELD OF A COIL",
         "heading": "A Magnetic Field Like a Bar Magnet's",
         "observation": "Outside: N to S. Inside: S to N."},
        {"start": 26, "end": 44, "case": "REVERSE THE CURRENT",
         "heading": "The magnetic poles swap",
         "observation": "Watch the arrows and both compass needles reverse."},
        {"start": 44, "end": 66, "case": "INCREASING THE NUMBER OF TURNS",
         "heading": "More Turns, Stronger Magnetic Field",
         "observation": "Same length and diameter. Same current: 0.50 A."},
        {"start": 66, "end": 80, "case": "ADDING A SOFT IRON CORE",
         "heading": "Insert the Nail with the Switch OFF",
         "observation": "Switch ON to compare the stronger field directly."},
        {"start": 80, "end": 81, "case": "LOOK INSIDE THE IRON",
         "heading": "First, open the switch", "observation": "Then close it and watch the magnetic regions."},
        {"start": 81, "end": 90, "rows": [
            ("INSIDE THE SOFT IRON", 5.8, .35),
            ("Magnetic regions line up", 5.1, .53),
            ("Blue: coil field. Gold: magnetic regions.", 1.05, .27),
            ("Magnified model: groups of atoms act like tiny magnets.", .55, .30)]},
        {"start": 90, "end": 99, "case": "A STRONGER ELECTROMAGNET",
         "heading": "Compare the three magnetic fields",
         "observation": "10 turns < 20 turns < 20 turns + soft iron"},
        {"start": 99, "end": 103, "case": "CONTROL THE ELECTROMAGNET",
         "heading": "Paper clips below the iron nail",
         "observation": "Switch OFF: the clips rest on the table."},
        {"start": 103, "end": 111, "case": "SWITCH ON",
         "heading": "The electromagnet attracts iron",
         "observation": "The clips cling to the nail's exposed ends."},
        {"start": 111, "end": 114, "case": "SWITCH OFF",
         "heading": "The paper clips fall",
         "observation": "Soft iron loses most of its induced magnetism."},
        {"start": 114, "end": 125, "case": "WHAT WE LEARNED",
         "heading": "Coils and electromagnets", "points": SUMMARY},
        {"start": 125, "end": demo.DURATION, "rows": [
            ("USES OF ELECTROMAGNETISM", 5.5, .43),
            ("Educational cutaways show the coil or magnet inside.", .35, .29)]},
    ]
    chalkboard.build(scene, mats, cases)
    group = g.collection("Coil | Magnetic regions on the laboratory board", scene)
    # A fixed nail silhouette contains the region diagram; only the magnetic
    # directions turn. For the reversed winding, electrons go left and the
    # internal magnetic field points right, along the aligned north tips.
    outline = g.line("Nail outline | Magnetic-region model",
        [(x,11.025,z) for x,z in ((-6,1.85),(-5.55,1.85),(-5.55,2.05),
          (4.9,2.05),(6,3.1),(4.9,4.15),(-5.55,4.15),(-5.55,4.35),(-6,4.35))],
        .025,mats["ink_white"],group,cyclic=True)
    outline["nail_region_outline"] = True
    chalkboard.show_between(outline,81,90,demo.FPS,demo.DURATION)
    for name,z,a,b,ink in (("Internal field and region alignment",1.65,(-1.8,0,0),(1.8,0,0),"ink_cyan"),):
        for obj in g.arrow(name,(a[0],11.0,z),(b[0],11.0,z),.035,mats[ink],group):
            chalkboard.show_between(obj,86,90,demo.FPS,demo.DURATION)
    for i in range(10):
        x, z = (-4.5+2.25*(i % 5), 3.65-1.10*(i//5))
        boundary = g.line("Iron magnetic region boundary", [(x+a, 11.025, z+b)
                           for a, b in ((-.88,-.43),(.88,-.43),(.88,.43),(-.88,.43))],
                          .014, mats["ink_muted"], group, cyclic=True)
        chalkboard.show_between(boundary, 81, 90, demo.FPS, demo.DURATION)
        region = bpy.data.objects.new(f"Iron magnetic region {i+1}", None)
        group.objects.link(region)
        region.location = (x, 11.01, z)
        region["magnetic_region"] = True
        angle = math.radians((115, -65, 155, 40, -125, 75, -150, -40, 130, -85)[i])
        for a in (-.52, 0., .52):
            pivot = bpy.data.objects.new("Magnetic direction within fixed region",None)
            group.objects.link(pivot)
            pivot.parent = region
            pivot.location = (a,0,0)
            pivot["magnetic_direction"] = True
            for obj in g.arrow("Atomic magnetic direction", (-.20, 0, 0), (.20, 0, 0),
                               .025, mats["ink_gold"], group):
                obj.parent = pivot
                chalkboard.show_between(obj, 81, 90, demo.FPS, demo.DURATION)
            for frame in range(81*demo.FPS+1,90*demo.FPS+2):
                seconds = (frame-1)/demo.FPS
                rotation = angle*(1-demo.ramp(seconds,86,89))
                pivot.rotation_euler.y = rotation
                pivot.keyframe_insert("rotation_euler", frame=round(seconds*demo.FPS)+1)
    build_current_diagram(group,mats)
    build_applications(scene, mats)



def build_current_diagram(group,mats):
    """End-view circulation is distinct from the axial magnetic-field arrow."""
    center=(-5.3,11.0,4.68)
    points=[(center[0]+.25*math.cos(i*math.tau/64),center[1],
             center[2]+.25*math.sin(i*math.tau/64)) for i in range(65)]
    ring=g.line("Board conventional current around winding",points,.018,mats["ink_gold"],group)
    objects=[ring]
    # Counterclockwise as seen looking at the north end; field points out of it.
    objects += g.arrow("Board current circulation",(-5.05,11,4.55),(-5.05,11,4.8),
                       .028,mats["ink_gold"],group)
    objects += [g.text("Board current caption","Current around coil (viewed from N end)",
                (.2,11,4.65),.28,mats["ink_gold"],group,rotation=(math.pi/2,0,0),align="CENTER")]
    for obj in objects:
        obj["board_current_cue"]=True
        chalkboard.show_between(obj,86,90,demo.FPS,demo.DURATION)


def picture(group, image, index, center, size):
    """UV windows show each panel without editing the source triptych."""
    x, z = center
    width, height = size
    mesh = bpy.data.meshes.new("Application picture")
    mesh.from_pydata([(x-width/2, 11.025, z-height/2), (x+width/2, 11.025, z-height/2),
                      (x+width/2, 11.025, z+height/2), (x-width/2, 11.025, z+height/2)], [], [(0,1,2,3)])
    uv = mesh.uv_layers.new()
    coordinates = ((index/3, 0), ((index+1)/3, 0), ((index+1)/3, 1), (index/3, 1))
    for loop, coordinate in zip(mesh.loops, coordinates):
        uv.data[loop.index].uv = coordinate
    obj = bpy.data.objects.new("Application picture | " + str(index), mesh)
    group.objects.link(obj)
    material = bpy.data.materials.new("Application picture emission")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs[0], out.inputs[0])
    mesh.materials.append(material)
    chalkboard.show_between(obj, 125, demo.DURATION, demo.FPS, demo.DURATION)


def build_applications(scene, mats):
    image = bpy.data.images.load(str(ROOT/"assets/lesson-applications/electromagnetism-applications.png"), check_existing=True)
    image.pack()
    group = g.collection("Coil | Applications on the laboratory board", scene)
    subjects = [("Scrapyard crane", "Lifting electromagnet", (-4.4,3.2), (.46,.46)),
                ("Dynamic microphone", "Moving coil + permanent magnet", (0,3.2), (.48,.45)),
                ("MRI machine", "Magnet coils around the bore", (4.4,3.2), (-.70,1.15))]
    for i, (title, caption, center, cue) in enumerate(subjects):
        picture(group, image, i, center, (3.85,3.85))
        x, z = center
        for body, height, font in ((title,.92,.34),(caption,.63,.23)):
            obj = g.text("Application caption | "+title, body, (x,11.015,height), font,
                         mats["ink_white"], group, rotation=(math.pi/2,0,0), align="CENTER")
            chalkboard.show_between(obj, 125, demo.DURATION, demo.FPS, demo.DURATION)
        start, end = demo.APPLICATIONS_START, demo.APPLICATIONS_START+demo.APPLICATIONS_DURATION
        border = g.line("Application focus | "+title, [(x+a,11.0,z+b)
                       for a,b in ((-2,-2),(2,-2),(2,2),(-2,2))], .028, mats["ink_gold"], group, cyclic=True)
        chalkboard.show_between(border,start,end,demo.FPS,demo.DURATION)
        halo = g.line("Magnetic component contrast halo | "+title,
                      [(x+cue[0]+.65*math.cos(j*math.tau/96),11.002,
                        z+cue[1]+.53*math.sin(j*math.tau/96)) for j in range(96)],
                      .063,mats["ink_navy"],group,cyclic=True)
        chalkboard.show_between(halo,start,end,demo.FPS,demo.DURATION)
        ring = g.line("Magnetic component highlight | "+title,
                      [(x+cue[0]+.65*math.cos(j*math.tau/96),10.90,
                        z+cue[1]+.53*math.sin(j*math.tau/96)) for j in range(96)],
                      .035,mats["ink_gold"],group,cyclic=True)
        ring["application_highlight"] = title
        chalkboard.show_between(ring,start,end,demo.FPS,demo.DURATION)
