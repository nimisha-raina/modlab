"""One fixed camera keeps the whole experiment and board visible."""
from . import coil_demo as demo, stage


def animate(scene):
    camera = scene.camera
    camera.animation_data_clear()
    camera.location,target = demo.camera_pose(0)
    camera.data.lens = 40
    stage.point_at(camera,target)
