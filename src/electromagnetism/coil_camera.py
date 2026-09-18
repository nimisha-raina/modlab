"""Refresh camera motion without rebuilding the experiment's geometry."""
from . import coil_demo as demo, stage
from .coil_keyframes import frames


def animate(scene):
    camera = scene.camera
    camera.animation_data_clear()
    for frame in frames((4,9),(14,18),(28,34),(44,50),(66,72),(80,83),
                        (89,92),(94,100),(105,107),(111,113),(114,117)):
        camera.location,target = demo.camera_pose((frame-1)/demo.FPS)
        stage.point_at(camera,target)
        camera.keyframe_insert("location",frame=frame)
        camera.keyframe_insert("rotation_euler",frame=frame)
