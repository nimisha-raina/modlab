"""Bake repeating current journeys efficiently into portable 24-fps actions."""
from mathutils import Vector
from . import coil_demo as demo
from .narration import curves


def write_channels(obj,channels):
    for curve in curves(obj.animation_data.action):
        key=(curve.data_path,curve.array_index)
        if key not in channels:continue
        values=channels[key]
        curve.keyframe_points.clear()
        curve.keyframe_points.add(len(values))
        curve.keyframe_points.foreach_set('co',[v for i,value in enumerate(values,1) for v in (i,value)])
        for point in curve.keyframe_points:point.interpolation='CONSTANT'
        curve.update()


def bake(scene):
    """Motion repeats while the contact visibility gates remain unchanged."""
    if scene.get('current_motion_revision')==1:return
    scene.frame_set(1)
    scene['current_motion_revision']=1
    n=demo.DURATION*demo.FPS
    phases=[i%48/48 for i in range(n)]
    for obj in scene.objects:
        if not obj.get('conventional_current_arrow') or obj.get('winding_arrow'):continue
        direction=obj.rotation_euler.to_matrix()@Vector((0,0,1))
        origin=obj.location+direction*.325
        channels={('location',axis):[origin[axis]+direction[axis]*(phase-.5)*.65 for phase in phases]
                  for axis in range(3)}
        write_channels(obj,channels)
    initial,dense=demo.wire_points(1),demo.dense_wire_points(1)
    for obj in scene.objects:
        if not obj.name.startswith('Conventional current on winding') or obj.type!='EMPTY':continue
        slot=next(child['winding_arrow'] for child in obj.children if child.get('winding_arrow'))
        sign=int(obj.name.rsplit('|',1)[1].strip())
        channels={(path,axis):[] for path,count in (('location',3),('rotation_quaternion',4)) for axis in range(count)}
        for i,phase in enumerate(phases):
            fraction=demo.dense_fraction(i/demo.FPS)
            index=110+round((25+(slot-1)*100-sign*100*phase)%500)
            def point(k):return Vector(initial[k]).lerp(Vector(dense[k]),fraction)
            position=point(index)+Vector((0,0,.11))
            tangent=(point(index+1)-point(index-1)).normalized()*-sign
            rotation=Vector((1,0,0)).rotation_difference(tangent)
            for axis,value in enumerate(position):channels[('location',axis)].append(value)
            for axis,value in enumerate(rotation):channels[('rotation_quaternion',axis)].append(value)
        write_channels(obj,channels)
    scene.frame_set(1)
