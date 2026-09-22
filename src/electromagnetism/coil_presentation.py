"""Case 2 readability and comparison cues, isolated from the frozen Case 1."""
import math
import bpy
from mathutils import Vector
from . import geometry as g, coil_demo as demo, chalkboard


def brighten(mats):
    for name,color in {'ink_white':(1,1,1,1), 'ink_muted':(.68,.80,.90,1),
                       'ink_cyan':(.12,.95,.88,1), 'ink_gold':(1,.80,.10,1)}.items():
        mat=mats[name]
        mat.diffuse_color=color
        next(n for n in mat.node_tree.nodes if n.type=='EMISSION').inputs['Color'].default_value=color


def finish(scene,mats,camera):
    group=g.collection('Coil | Clear readings and comparison',scene)
    # The resistor and both adjoining leads share one straight axis.
    a,b=Vector((5,2.2,demo.CENTER[2])),Vector((5,-2.2,.7))
    def site(y):return a.lerp(b,(2.2-y)/4.4)
    for obj in list(scene.objects):
        if obj.name.split('.')[0] in ('Copper conductor 2','Copper conductor 3') or obj.name.startswith(('Resistor body','Resistor colour band')):
            bpy.data.objects.remove(obj,do_unlink=True)
    # Existing resistor object names are deliberately checked below as well.
    for obj in list(scene.objects):
        if obj.type=='MESH' and obj.name.startswith(('Resistor','Resistance band','Current-limiting resistor')):
            bpy.data.objects.remove(obj,do_unlink=True)
    g.line('Copper conductor 2',[a,site(.5)],.115,mats['copper'],group)
    g.cylinder('Resistor body | straight axis',site(-.7),site(.5),.23,mats['ceramic'],group)
    for y,ink in ((-.38,'ink_gold'),(-.08,'ink_navy'),(.22,'ink_gold')):
        g.cylinder('Resistor colour band',site(y-.035),site(y+.035),.234,mats[ink],group)
    g.line('Copper conductor 3',[site(-.7),b,(3.8,-2.2,.7)],.115,mats['copper'],group)
    for obj in scene.objects:
        if obj.type=='FONT' and ('amperes' in obj or obj.name.startswith('Ammeter measured')):
            obj.data.size=.23
        if obj.name.startswith('Ammeter scale graduation'):
            obj.data.bevel_depth=.005
    # A faint dashed needle records the actual previous model angle.
    for start,end,reference in ((58,66,34),(73,80,61),(90,99,61)):
        angle=demo.needle_angle_at(reference)
        for x,y,z in demo.COMPASS_CENTERS:
            for radius in (.17,.31,.45):
                points=[(x+r*math.cos(angle),y+r*math.sin(angle),z+.065)
                        for r in (radius,radius+.08)]
                marker=g.line('Previous compass position',points,.016,mats['ink_muted'],group)
                marker['previous_compass_reference_seconds']=reference
                chalkboard.show_between(marker,start,end,demo.FPS,demo.DURATION)
    degrees={t:round(abs(math.degrees(demo.needle_angle_at(t)-demo.NORTH_ANGLE))) for t in (34,61,76)}
    comparisons=[(58,66,f"Before: 10 turns / {degrees[34]}°   Now: 20 turns / {degrees[61]}°"),
                 (74,80,f"Before: air core / {degrees[61]}°   Now: iron core / {degrees[76]}°"),
                 (90,99,f"10 turns: {degrees[34]}°   20 turns: {degrees[61]}°   With iron: {degrees[76]}°")]
    board=g.collection('Chalkboard | Measurement comparisons',scene)
    for start,end,body in comparisons:
        obj=g.text('Compass before and now comparison',body,(0,11.06,1.5),.34,
                   mats['ink_gold'],board,rotation=(math.pi/2,0,0),align='CENTER')
        obj['localized_width']=12.
        chalkboard.show_between(obj,start,end,demo.FPS,demo.DURATION)
    scene['presentation_revision']='Prabhat / Swara; moving current; measured comparisons; highlighted applications'
