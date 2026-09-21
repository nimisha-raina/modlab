"""Bring compass readouts in front of their stands during the nail orbit."""
import math
from mathutils import Vector
from . import coil_demo as demo
from .narration import curves


def animate(scene):
    objects=[o for o in scene.objects if 'display_degrees' in o]
    for obj in objects:
        base=obj.location.copy()
        for frame in range(66*demo.FPS+1,80*demo.FPS+2):
            amount=demo.orbit_fraction((frame-1)/demo.FPS)
            camera,_=demo.camera_pose((frame-1)/demo.FPS)
            # Move along the sightline and scale equally: same screen size and
            # position, but in front of the physical stand rather than through it.
            camera=Vector(camera)
            ratio=1-.3*amount
            right=Vector((.5,math.sqrt(3)*.5,0))
            anchor=base+right*(1.7 if base.x>0 else -1.7)*amount
            obj.location=camera+(anchor-camera)*ratio
            obj.scale=(ratio,)*3
            obj.keyframe_insert('location',frame=frame)
            obj.keyframe_insert('scale',frame=frame)
        for curve in curves(obj.animation_data.action):
            if curve.data_path in ('location','scale'):
                for key in curve.keyframe_points:key.interpolation='CONSTANT'
