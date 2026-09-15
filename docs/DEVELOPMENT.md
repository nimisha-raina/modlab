# Developing this project

## Architecture

**Python is the source of truth.** Every scene object is made by `bpy`, so a clean
checkout can regenerate the project. Small files group related responsibilities.

**Simple package structure.** A normal Python package
with a short entry script is easier to understand than registration hooks and
custom panels. Later chapters can reuse its modelling and motion helpers.

**Baked animation.** Particle positions are stored as ordinary keyframes. The
saved `.blend` plays without running Python callbacks or enabling script
auto-execution. This costs some file size but makes sharing much simpler.

**CPU Cycles rendering.** Soft light and metallic copper work consistently in
headless rendering. Preview quality uses 1280×720 and 24 samples; final quality
uses 1920×1080 and 64 samples. Choose a GPU manually in Blender if supported.
The web-video export script uses EEVEE at 1280×720, 24 fps and 32 samples to keep
full animation renders practical; it does not change the saved scene's settings.

**Procedural laboratory.** Furniture, window frames, the chalkboard, battery
holder, switch screws, and material textures are built by Python. No external
3D models or image textures are required.

**Narration first.** `docs/narration.json` contains ten short explanations.
`scripts/generate_narration.py` uses AI4Bharat's official public Indic Parler-TTS
demo to generate Thoma's male Indian-English voice. It reuses completed clips.
The demo may have capacity or account limits. It is only used while authoring;
students receive an ordinary video with a pre-recorded audio track.

`scripts/prepare_narration.py` normalizes the clips and records their measured
lengths. `src/electromagnetism/narration.py` stretches the matching Blender
animation sections, including camera, particles, captions, and material fades,
then adds the audio to Blender's sequencer. Speech is never accelerated to fit.
The sounds are packed inside the saved `.blend`, keeping playback portable.
The original 48-second storyboard remains the motion source; rendered timing
is recorded in `output/audio/narration-timing.json` and `output/build-info.json`.

The scene was tested with Blender 5.2.1 LTS on macOS with Apple silicon.
The website was tested with Node.js 24.19.0 and pnpm 11.19.0. Other operating systems
and GPU configurations may produce different render timings or appearance.

Use Python 3.12 in a separate environment for `requirements-media.txt`. Blender still
supplies `bpy`; it should not be installed with pip.

**Local voice generation.** If the public demo is unavailable, accept the model's
access conditions on Hugging Face and connect its official CLI using your usual
browser. The connection and model weights stay in ignored `.cache/` folders.
The account is used to download the voice model; inference runs offline and
does not send the lesson text or credentials to a speech service.

Keep the newer authentication client in `.venv-media` and the model's pinned
Transformers dependencies in `.venv-voice`. This avoids a dependency conflict:
the original Parler library requires Transformers 4.46.1, while the current
Hugging Face client supports browser connection codes.

```sh
HF_HOME="$PWD/.cache/huggingface" .venv-media/bin/hf auth login --no-add-to-git-credential
.venv-media/bin/python scripts/download_voice_model.py
python3 -m venv .venv-voice
.venv-voice/bin/python -m pip install -r requirements-voice.txt
.venv-voice/bin/python scripts/generate_narration_local.py
```

Both generators preserve existing clips. `output/audio/provenance.json` records
which clips came from the public demo and which were generated locally. Never
put a token in source code, a command argument, or the student website.
`requirements-voice.lock.txt` records the complete working package versions.
To replace a spoken line, edit `docs/narration.json`, move its corresponding
`output/audio/narration_XX.mp3` to a backup folder, and rerun a generator. Then
repeat preparation, the Blender build, rendering and verification.

## Build versus render

Building creates the models and animation and writes the `.blend` file.
Rendering computes each finished image. A quick build does not mean a full
1,970-frame narrated video will render quickly. Use one frame, then storyboard stills,
then a complete render when the lesson's content is approved.

For a saved scene, Blender's background render can resume a frame range:

```bash
blender --background output/electromagnetism_intro.blend --frame-start 601 --frame-end 900 --render-anim
```

## Source frame numbers (before narration retiming)

| Frame | State |
| --- | --- |
| 1 | Circuit visible; switch open |
| 13 | Camera begins its zoom |
| 121 | Magnified view reached |
| 217 | Switch closes; electron drift starts |
| 385 | Clear electron entry and exit |
| 505 | First of three concentric field guides begins appearing |
| 649 | Slow pullback begins |
| 889 | Original circuit view restored |
| 1009 | Wider field view reached |
| 1057 | Switch opens |
| 1152 | End |

The camera is baked every frame from `camera_path.py`. No timeline marker
switches cameras. Its target stays on the sample through the early pullback.
In a narrated build, use the
timeline markers in Blender; the source frame numbers above are remapped to
the measured speech lengths.

## Narrated video workflow

```sh
python3 -m venv .venv-media
.venv-media/bin/python -m pip install -r requirements-media.txt
python3 scripts/restore_assets.py
# Generate clips only if spoken text has changed.
.venv-media/bin/python scripts/verify_narration.py
.venv-media/bin/python scripts/prepare_narration.py
blender --background --python-exit-code 1 --python run.py -- --quality preview
blender --background output/electromagnetism_intro.blend --python-exit-code 1 --python scripts/verify_scene.py
blender --background output/electromagnetism_intro.blend --python-exit-code 1 --python scripts/render_video.py
.venv-media/bin/python scripts/verify_narrated_video.py
.venv-media/bin/python scripts/sync_student_lesson.py
```

Then run `pnpm build` and `pnpm test` inside `student-lesson`. The site checkout
contains its own copied timing and captions, so it can rebuild independently.
The first speech-recognition check downloads its public recognition model.
The check flags wording changes; it does not certify accent
quality or replace a human listening review.

## Reference assets and distribution

The repository includes approved narration under `assets/narration/`, a portable
scene under `assets/scene/`, and the finished video under
`student-lesson/dist/assets/`. Run `python3 scripts/restore_assets.py` to prepare
working copies in `output/`. Existing work is preserved unless `--overwrite`
is passed. No voice-model login is needed to reuse the included recordings.

The `output/` directory is disposable working output. After approving changed
media, update the matching reference assets, build metadata and verification
reports so a fresh checkout can reproduce the current lesson. Use
`scripts/export_portable_scene.py` through Blender to refresh the shared scene.

Dependencies, model weights, credentials and local hosting configuration remain
ignored. The existing binary assets are each below GitHub's file-size limit.
Use Git LFS or release assets if future chapters make binary history large.

## Validation scope

The pure Python tests check switch timing, bounded particle motion and drift
direction. The Blender verification checks the generated scene's cameras,
switch/field timing and actual particle movement before current starts.
Rendered keyframes should be inspected for readability whenever geometry,
camera positions or caption layout change.

The scene checks also cover camera continuity, fixed ion spacing, equal electron
marker radii, concentric field guides, packed audio and premature field visibility.
After changes, review rendered frames, listen to the complete lesson and check all
three questions on desktop and phone. Behaviour tests do not replace layout review.
