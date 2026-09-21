# Developing this project

## Current Case 2 workflow

See [PART_02_BILINGUAL.md](PART_02_BILINGUAL.md) for the English/Hinglish coil
lesson with contact-synchronized fields, nail orbit and H5P questions. It has
separate scripts, packed scenes, a shared picture track and two soundtracks.
It does not modify the frozen first case or its H5P package.

## Current first-case narration workflow

The website uses the revised 86-second opening, compass comparison and
summary, with two quiz pauses. `docs/first-case-narration.json` contains fourteen
short tutor lines. The original ten-section workflow below remains a reference.

From the project root in the media environment:

```sh
python scripts/restore_assets.py
# Install the optional authoring client only when speech changes.
python -m pip install -r requirements-narration.txt
python scripts/generate_tutor_narration.py
python scripts/prepare_first_case_narration.py
python scripts/verify_narrated_video.py --timing output/parts/01_compass_current/audio_tutor/narration-timing.json --video output/parts/01_compass_current/opening_and_compass_narrated_720p.mp4
python student-lesson/scripts/build_h5p.py
node --test student-lesson/tests/h5p.test.cjs
python scripts/serve_lesson.py
```

Generation sends only the public script to Microsoft's Edge speech service and
caches each line by its text and voice-description hash. Completed unchanged lines
are reused. The male Indian-English voice is `en-IN-PrabhatNeural`, at its natural
rate. The AI4Bharat demo failed for revised speech, so the entire tutor revision
uses this one consistent voice. No voice-model download is required.

Preparation preserves 150 ms of sentence-tail silence, normalizes loudness and
measures each clip. It applies 20 ms/100 ms raised-cosine fades to smooth waveform
joins, and leaves short natural pauses between neighbouring explanations.
It rejects stale recordings or speech too long for its window. Shorten the text
and regenerate that line rather than speeding up the voice. It mixes speech into
the revised silent movie with video stream copying, retaining 1,032 frames at
12 fps and the eight-second electron-flow section. Narration is not repacked
into the saved Blender draft. Preparation also synchronizes the website media,
captions and timing; the H5P build supplies the two native pauses at 30.7 and
68.7 seconds. Correct answers unlock Continue; incorrect answers allow retry.

The video verifier checks actual decoded audio against all prepared recordings,
and checks silence around each quiz pause. Optional word checking uses
`verify_narration.py --script docs/first-case-narration.json --output output/parts/01_compass_current/audio_tutor`.
It downloads a small speech-recognition model on first use. Recognition can
miss repeated words or transcribe spoken numbers as digits; it does not establish
accent quality. Listen to the finished movie before publishing. GitHub Pages
still serves the earlier reference; publishing this revision needs the separate publishing
step described in [PUBLISHING.md](PUBLISHING.md).

Recordings, normalized WAV files, provenance and verification reports are
included under `assets/tutor-narration/`. The earlier 76-second Thoma recordings
remain under `assets/first-case-narration/`. Run `restore_assets.py` to restore
working copies without overwriting existing files; unchanged narration needs no
service request. Preparation also restores missing copies automatically. If the
silent review movie is absent, it copies the video stream from the included
narrated movie if its duration matches the authored timeline. The original
reference recordings remain in `assets/narration/`; their timing does not apply
to the current first case.

### Tutor visual build

The base `build_compass_sequence.py` remains the reviewed 76-second source.
`tutor_timing.py` maps its opening onto the apparatus tour and shorter overview;
the compass experiment keeps its timing, with four additional seconds holding
the final summary board. To rebuild revised visuals after restoring
the base scene and reviewed frame cache:

```sh
python scripts/prepare_apparatus_cues.py
blender --background --python-exit-code 1 --python scripts/build_tutor_sequence.py
blender --background output/parts/01_compass_current/opening_and_compass_tutor.blend --python-exit-code 1 --python scripts/verify_tutor_sequence.py
blender --background output/parts/01_compass_current/opening_and_compass_tutor.blend --python-exit-code 1 --python scripts/render_tutor_sequence.py
python scripts/render_tutor_sequence.py --encode
python scripts/prepare_first_case_narration.py
```

Apparatus cues use recorded word boundaries, aligned to the normalized setup
clip by waveform correlation. Warm yellow arrows identify the named component;
they are separate from green magnetic-field guides. The renderer computes five
new pointer stills for the stationary opening camera and resamples the reviewed
12-fps frames for the rest using nearest-frame selection (at most 1/24-second
source-time quantization). The editable scene has continuously retimed keyframes.
When only timing changes, use `python scripts/render_tutor_sequence.py --reuse-highlights`
in place of the Blender render command, followed by encoding and audio preparation.
This reuses the existing pointer stills and reviewed frames. The summary opens
with "To summarize what we have learned" and ends at second 86; the two quiz
pauses and all experiment events keep their timing.
The zoom and electron-flow intervals each remain eight seconds. The overview
transition becomes seven seconds instead of ten. Geometry or lighting changes
require a full new render rather than reusing those source frames. For a fresh
checkout, rebuild the base scene and its frame cache using [PART_01.md](PART_01.md).

## Original reference architecture

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

## Windows preview and checks

`pnpm build` first uses `PYTHON` when set, then the project's `.venv-media`
interpreter, and finally a system Python 3 command. This avoids inaccessible
Microsoft Store command aliases on Windows:

```powershell
cd student-lesson
pnpm install --frozen-lockfile
pnpm build
pnpm test
cd ..
python -m unittest discover -s tests -v
python scripts/restore_assets.py
python scripts/serve_lesson.py
```

Open `http://127.0.0.1:8765/`. This preview uses the included video and narration.
For media checks, Windows virtual environments use
`.venv-media/Scripts/python.exe` in place of `.venv-media/bin/python`.
After installing `requirements-media.txt` and restoring assets, run
`python scripts/verify_narrated_video.py --timing output/parts/01_compass_current/audio_tutor/narration-timing.json --video output/parts/01_compass_current/opening_and_compass_narrated_720p.mp4`
with that environment to check the current video's soundtrack alignment and
silent question pauses after restoring assets.
`verify_narration.py` downloads a speech-recognition model on its first run;
reuse the included transcript report for unchanged recordings when avoiding
model downloads.

Blender 5.2.0 LTS on Windows also passes the preview scene build and
`scripts/verify_scene.py`. The reference media was made with 5.2.1 LTS;
this compatibility check does not establish identical rendered output.

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
| 73 | Camera begins its zoom |
| 265 | Magnified view reached |
| 337 | Switch closes; electron drift, field reveal and gentle camera turn start |
| 433 | Camera reaches the oblique field view |
| 481 | Clear electron entry and exit |
| 505 | Three concentric field guides remain visible |
| 529 | Slow pullback begins after eight seconds of visible flow |
| 769 | Original circuit view restored; original circles remain visible |
| 1009 | Wider field view reached |
| 1057 | Switch opens |
| 1152 | End |

The camera is baked every frame from `camera_path.py`. No timeline marker
switches cameras. Its target stays on the sample through the early pullback.
In a narrated build, use the
timeline markers in Blender; the source frame numbers above are remapped to
the measured speech lengths.

## Independent compass section

[PART_01.md](PART_01.md) documents the independent compass/current builder,
34-second timeline, silent draft renderer and scene verification. The modules
reuse the laboratory and circuit while keeping the new chapter's timing and
physics separate from the opening animation. Review these visual sections before
recording revised narration and assembling the final H5P video. The connected
builder preserves the opening motion, cuts before its switch-off finale and
adds a series ammeter and compass continuation. Its separate saved assembly
retains current through the join; see the chapter guide for commands.

## Original narrated video workflow

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
.venv-media/bin/python scripts/verify_narrated_video.py --questions assets/reference/questions.json
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
marker radii, shared ion/electron visibility, compact label backplates,
concentric close-up guides, six overview guide locations and their right-hand
rule, packed audio and premature field visibility.
After changes, review rendered frames, listen to the complete lesson and check all
questions on desktop and phone. Behaviour tests do not replace layout review.

## Reviewing the Blender draft before web export

The first connected case holds a farther view of the experiment board, table
and full circuit for three seconds, then approaches copper over eight seconds.
Visible electron drift runs from second 14 to 22. Its cutaway becomes
opaque during the first second of pullback; cutaway geometry is hidden once
closed. The round black analogue ammeter sits over the left branch, with
concealed rear connections, a white centre-zero scale and animated pointer.
The dial uses explicit triangles and separated depth layers; the 0.05-unit
camera near plane improves depth precision during wide views. The resistor
label sits beside its component. Three circles persist at the microscope site,
with five additional sites completing the layout. A compass arc and degree
reading show the current comparison. The summary replaces the previous board
heading as the final return begins at global second 66. Rebuild the
connected scene after these geometry changes; `--reuse-opening` intentionally
retains the loaded opening and cannot apply changes to it.

[PART_02.md](PART_02.md) documents the separate 136-second, frame-one coil,
reversal, iron-core, clip and application sequence. The efficient
`render_coil_review.py` renderer reuses identical stationary scene states;
its `--encode` mode uses the media environment. The existing `render_current_demo.py`
accepts `--coil` and `--draft-fps 4`, `6` or `12`; low-rate review movies are
explicitly named drafts and retain the source duration. Full quality stays
at 24 fps. Previous movie caches remain unchanged until rendered again.
Use 12 or 24 fps to judge the faster electron drift; lower sampling rates can
make repeated markers appear to travel backwards. Both the renderer and
`verify_compass_preview.py` accept `--range START END` for separately named
focused exports and decoding reports. `render_complete_preview.py` exports the
complete 76-second first case, including its summary-board ending, at 720p and
12 fps; use its media-environment `--encode` stage and the media verifier
`--combined --review-720p` option. Identical evaluated visible states reuse a
PNG, preserving every frame and its full duration. See [PART_01.md](PART_01.md)
for commands.

Build the scene from Python and verify it first. Render selected storyboard
times with the saved scene; the probe command maps source times to the attached
narration automatically:

```sh
blender --background output/electromagnetism_intro.blend --python-exit-code 1 --python scripts/render_video.py -- --probe-source-times 0 10.8 11.2 17 30 41
```

This writes review PNGs under `output/video/`, preserves the `.blend` settings,
and leaves the included MP4 untouched. On Windows, invoke the installed Blender
executable with the same arguments. Use the `.blend` timeline for motion review.
The Blender draft retains the original narration as a guide track. The current
first-case movie and local H5P player use the new fixed-timeline narration above.
