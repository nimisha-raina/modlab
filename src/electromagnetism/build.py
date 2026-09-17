"""Compose one self-contained lesson, without changing other Blender scenes."""

import json
import bpy
from . import circuit, fields, microscope, overlays, stage, narration, ammeter, chalkboard
from .camera_path import opening_pose
from .field_layout import OVERVIEW_GUIDES, first_case_guides
from .config import LESSON, OUTPUT, SCENE_NAME
from .lesson_text import CAPTIONS
from .materials import make_materials


def clean_previous_lesson(scene_name=SCENE_NAME):
    """Remove only objects from the scene owned by this project on rebuild."""
    previous = bpy.data.scenes.get(scene_name)
    if previous:
        owned_collections = list(previous.collection.children)
        for obj in list(previous.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.scenes.remove(previous)
        for group in owned_collections:
            if group.users == 0:
                bpy.data.collections.remove(group)


def build_lesson(quality="preview", *, attach_audio=True, series_ammeter=False, export_files=True):
    clean_previous_lesson()
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
    materials = make_materials()
    camera = stage.setup(scene, materials, quality)
    circuit.build(scene, materials, camera)
    if series_ammeter:
        reading = ammeter.build(scene, materials)
        reading.data.body = "0.00 A"
        ammeter.animate(reading, LESSON.fps, LESSON.duration,
                        lambda t: 1 if LESSON.switch_on <= t < LESSON.switch_off else 0)
        chalkboard.build(scene, materials, [{"start": 0, "end": LESSON.duration,
            "case": "EXPERIMENT  /  ELECTRICITY AND MAGNETISM",
            "heading": "Magnetic effect of electric current",
            "observation": "Close the circuit. Observe the magnetic field."}])
        camera.animation_data_clear()
        for frame in range(1, LESSON.last_frame+1):
            camera.location, target = opening_pose((frame-1)/LESSON.fps)
            stage.point_at(camera, target)
            camera.keyframe_insert("location", frame=frame)
            camera.keyframe_insert("rotation_euler", frame=frame)
    microscope.build(scene, materials, camera)
    fields.build(scene, materials, first_case_guides() if series_ammeter else OVERVIEW_GUIDES)
    overlays.build(scene, materials, camera, board_until=LESSON.zoom_start if series_ammeter else 0)
    scene["lesson"] = "A Class 8 introduction to the magnetic effect of electric current."
    scene["model_note"] = "Illustration only: sizes, motion and particle counts are not to scale."
    scene["electron_direction"] = "External circuit: negative to positive; sample: +X."
    scene["current_direction"] = "External circuit: positive to negative; sample: -X."
    scene["switch_on_frame"] = LESSON.frame(LESSON.switch_on)
    scene["switch_off_frame"] = LESSON.frame(LESSON.switch_off)
    scene["reference_frame"] = "Laboratory frame throughout. No relativistic contraction is shown."
    scene["version"] = 6
    scene["microscopic_flow_seconds"] = LESSON.microscope_out-LESSON.switch_on
    scene["narration_status"] = ("Reference guide track: sections 6 and 8 need revision for the updated visuals."
                                  if attach_audio else "Silent visual draft; narration pending sequence review.")
    timing = narration.attach(scene) if attach_audio else None
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
    if export_files:
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
