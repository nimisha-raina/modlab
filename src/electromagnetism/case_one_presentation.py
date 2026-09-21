"""Readable headings, travelling current guides and instrument comparisons."""
import math
import bpy
from mathutils import Vector
from . import geometry as g, overlays, current_demo as demo
from .chalkboard import show_between
from .narration import curves

HEADINGS = {
    'EXPERIMENT  /  ELECTRICITY AND MAGNETISM': 'MAGNETIC EFFECT OF ELECTRIC CURRENT',
    'Magnetic effect of electric current': 'A Wire Can Produce a Magnetic Field',
    'Close the circuit. Observe the magnetic field.': 'Close the switch and observe the compass.',
    'CURRENT AND COMPASS': 'DETECTING THE MAGNETIC FIELD',
    'A compass detects the magnetic field': 'The Compass Needle Deflects',
    'The current is already flowing.': 'Current in the wire changes the needle direction.',
    'DOUBLING THE CURRENT': 'INCREASING THE CURRENT',
    'More current. Stronger magnetic field.': 'More Current, Stronger Magnetic Field',
    'Same wire. Same compass position.': 'Keep the wire and compass in the same positions.',
    'EXPERIMENT SUMMARY': 'KEY OBSERVATIONS',
    'What we learned': 'What We Learned',
    '1. Electrons drift from negative to positive.': '1. Electrons drift from the negative to the positive terminal.',
    '2. Electric current creates a magnetic field.': '2. Electric current produces a magnetic field around the wire.',
    "3. A compass detects the wire's magnetic field.": '3. A compass needle detects the magnetic field.',
    '4. More current: stronger field, greater needle deflection.': '4. Increasing the current strengthens the magnetic field.',
}


def ink(name, colour):
    material=bpy.data.materials.new('Case 1 clear ink | '+name)
    material.diffuse_color=(*colour,1)
    material.use_nodes=True
    nodes=material.node_tree.nodes
    nodes.clear()
    emission=nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value=(*colour,1)
    emission.inputs['Strength'].default_value=1.25
    output=nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    return material


def palette():
    return {'ink_white':ink('white',(1,1,1)),
            'ink_gold':ink('current yellow',(1,.72,.015)),
            'ink_mint':ink('field green',(.05,1,.45)),
            'ink_cyan':ink('electron blue',(.02,.65,1)),
            'ink_copper_light':ink('copper label',(1,.48,.10)),
            'ink_muted':ink('reference',(.55,.73,.9)),
            'ink_panel':ink('dark blue',(.007,.018,.038))}


def restyle(scene,mats):
    for obj in scene.objects:
        if obj.type!='FONT':continue
        body=obj.data.body
        if body in HEADINGS:
            obj.data=obj.data.copy()
            obj.data.body=HEADINGS[body]
            colour='gold' if obj.data.size<.4 and not body[:1].isdigit() else 'white'
            obj.data.materials.clear();obj.data.materials.append(mats['ink_'+colour])
            bpy.context.view_layer.update()
            if obj.dimensions.x>12:obj.data.size*=12/obj.dimensions.x
        elif obj.name.startswith('Ammeter printed') or obj.name.startswith('Ammeter reading'):
            # The white dial needs dark, sharp numerals; preserve their contrast.
            if obj.name.startswith('Ammeter reading'):obj.data.size*=1.12
        else:
            old=obj.data.materials[0].name if obj.data.materials else ''
            colour=next((c for c in ('cyan','gold','mint','copper_light','muted') if c in old),'white')
            obj.data.materials.clear();obj.data.materials.append(mats['ink_'+colour])


def travel_arrow(objects,a,b,start,end,duration):
    """A short arrow repeatedly advances along the conductor, never around it."""
    a,b=Vector(a),Vector(b)
    midpoint=(a+b)/2
    direction=(b-a).normalized()
    distance=(b-a).length
    for obj in objects:
        obj.location=midpoint+(obj.location-midpoint)*.52
        obj.scale*=.52
        origin=obj.location.copy()
        obj['conventional_current']=True
        obj['current_vector']=list(direction)
        obj['travelling_current_arrow']=True
        show_between(obj,start,end,24,duration)
        for frame in range(1,round(duration*24)+1):
            progress=((frame-1)%36)/36
            obj.location=origin+direction*distance*.48*(progress-.5)
            obj.keyframe_insert('location',frame=frame)
        for curve in curves(obj.animation_data.action):
            if curve.data_path=='location':
                for key in curve.keyframe_points:key.interpolation='LINEAR'


def comparison(scene,mats):
    """Live values come from the existing instrument animation, not duplicate physics."""
    group=g.collection('Case 1 | Reading comparison',scene)
    camera=scene.camera
    def text(body,x,y,size=.10,colour='white',align='LEFT'):
        obj=overlays.label(camera,group,mats,body,x,y+.16,size,colour,align)
        obj['localized_height']=.105 if size>=.095 else .095
        obj['localized_width']=2.35 if len(body)>12 else .64 if align=='CENTER' else .95
        show_between(obj,5,24,24,38)
        return obj
    panel=overlays.panel(camera,group,mats,'Reading comparison panel',1.67,1.28,2.52,.93,'panel')
    show_between(panel,5,24,24,38)
    text('COMPARE THE READINGS',.50,1.48,.10,'gold')
    text('BEFORE',1.72,1.28,.083,'muted','CENTER')
    text('NOW',2.51,1.28,.083,'gold','CENTER')
    text('Ammeter',.50,1.07)
    text('Compass',.50,.86)
    text('0.50 A',1.72,1.07,.12,'muted','CENTER')
    text('25°',1.72,.86,.12,'muted','CENTER')
    originals=[o for o in scene.objects if o.name.startswith(('Ammeter reading |','Compass deflection reading |'))]
    visible={o.name:set() for o in originals}
    for frame in range(5*24+1,24*24+1):
        scene.frame_set(frame)
        for original in originals:
            if not original.hide_render:visible[original.name].add(frame)
    for prefix,y,key in [('Ammeter reading |',1.07,'amperes'),('Compass deflection reading |',.86,'display_degrees')]:
        for original in originals:
            if not original.name.startswith(prefix):continue
            body=f"{original[key]:.2f} A" if key=='amperes' else f"{original[key]}°"
            obj=text(body,2.51,y,.14,'gold','CENTER')
            obj['instrument_mirror']=key
            obj['measurement']=original[key]
            obj.animation_data_clear()
            previous=None
            for frame in range(1,38*24+1):
                hidden=frame not in visible[original.name]
                if previous!=hidden:
                    obj.hide_render=obj.hide_viewport=hidden
                    obj.keyframe_insert('hide_render',frame=frame)
                    obj.keyframe_insert('hide_viewport',frame=frame)
                previous=hidden
    note=text('Needle moved about 18° further',1.67,.69,.084,'mint','CENTER')
    show_between(note,15,21,24,38)
    # The fixed starting marker remains when the physical red needle advances.
    needle=next(o for o in scene.objects if o.name.startswith('Compass needle |'))
    scene.frame_set(5*24+1)
    angle=needle.rotation_euler.z
    x,y,z=demo.COMPASS_CENTER
    for r0,r1 in ((.15,.25),(.31,.41),(.47,.60)):
        obj=g.line('Compass original 25 degree marker',
            [(x+r*math.cos(angle),y+r*math.sin(angle),z+.026) for r in (r0,r1)],.011,mats['ink_cyan'],group)
        obj['initial_compass_degrees']=25
        show_between(obj,5,24,24,38)
    scene.frame_set(1)
