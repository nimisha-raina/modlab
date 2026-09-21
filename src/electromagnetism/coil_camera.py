"""Stable teaching view, with the approved brief right-hand nail orbit."""
from . import coil_demo as demo, stage
from .coil_keyframes import frames
from .narration import curves


def animate(scene):
    camera = scene.camera
    camera.animation_data_clear()
    camera.data.animation_data_clear()
    for frame in frames((66,80),(0,0),(136,136)):
        seconds = (frame-1)/demo.FPS
        camera.location,target = demo.camera_pose(seconds)
        camera.data.lens = 40+5*demo.orbit_fraction(seconds)
        stage.point_at(camera,target)
        camera.keyframe_insert('location',frame=frame)
        camera.keyframe_insert('rotation_euler',frame=frame)
        camera.data.keyframe_insert('lens',frame=frame)
    for block in (camera,camera.data):
        for curve in curves(block.animation_data.action):
            for key in curve.keyframe_points:
                key.interpolation='LINEAR'
