"""Compose one self-contained lesson, without changing other Blender scenes."""

import json
import bpy
from . import circuit, fields, microscope, overlays, stage, narration
from .config import LESSON, OUTPUT, SCENE_NAME
from .lesson_text import CAPTIONS
from .materials import make_materials


def clean_previous_lesson():
    """Remove only objects from the scene owned by this project on rebuild."""
    previous = bpy.data.scenes.get(SCENE_NAME)
    if previous:
        owned_collections = list(previous.collection.children)
        for obj in list(previous.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.scenes.remove(previous)
        for group in owned_collections:
            if group.users == 0:
                bpy.data.collections.remove(group)


def build_lesson(quality="preview"):
    clean_previous_lesson()
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    materials = make_materials()
    camera = stage.setup(scene, materials, quality)
    circuit.build(scene, materials, camera)
    microscope.build(scene, materials, camera)
    fields.build(scene, materials)
    overlays.build(scene, materials, camera)
    scene["lesson"] = "A Class 8 introduction to the magnetic effect of electric current."
    scene["model_note"] = "Illustration only: sizes, motion and particle counts are not to scale."
    scene["electron_direction"] = "External circuit: negative to positive; sample: +X."
    scene["current_direction"] = "External circuit: positive to negative; sample: -X."
    scene["switch_on_frame"] = LESSON.frame(LESSON.switch_on)
    scene["switch_off_frame"] = LESSON.frame(LESSON.switch_off)
    scene["reference_frame"] = "Laboratory frame throughout. No relativistic contraction is shown."
    scene["version"] = 4
    timing = narration.attach(scene)
    scene.render.filepath = str(OUTPUT / "frames" / "lesson_")
    (OUTPUT / "frames").mkdir(parents=True, exist_ok=True)
    scene.frame_set(1)

    # Opening the saved project starts in camera view with the lesson selected.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.overlay.show_overlays = False
                area.spaces.active.shading.type = "MATERIAL"
    export_supporting_files(timing)
    return scene


def export_supporting_files(timing=None):
    OUTPUT.mkdir(parents=True, exist_ok=True)

    def stamp(seconds):
        millis = round(seconds*1000)
        return f"{millis//3600000:02}:{millis//60000%60:02}:{millis//1000%60:02},{millis%1000:03}"

    transform = (lambda t: narration.map_time(t,timing)) if timing else (lambda t:t)
    blocks = [f"{i}\n{stamp(transform(start))} --> {stamp(transform(end))}\n{title}\n{subtitle}\n"
              for i, (start, end, title, subtitle) in enumerate(CAPTIONS, 1)]
    (OUTPUT / "lesson.srt").write_text("\n".join(blocks), encoding="utf-8")
    (OUTPUT / "web-captions.json").write_text(json.dumps([
        [transform(start),transform(end),title,subtitle]
        for start,end,title,subtitle in CAPTIONS],indent=2)+"\n")
    (OUTPUT / "build-info.json").write_text(json.dumps({
        "blender": bpy.app.version_string, "fps": LESSON.fps,
        "frames": timing["frames"] if timing else LESSON.last_frame,
        "duration_seconds": timing["duration"] if timing else LESSON.duration,
        "scene": SCENE_NAME, "audio": "Indian English / Thoma" if timing else "No narration attached",
    }, indent=2)+"\n", encoding="utf-8")
