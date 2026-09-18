# Modlab · Electricity makes magnetism

A Class 8 science lesson built with Python and Blender's `bpy` API. A copper
circuit in a school laboratory leads into an enlarged view of vibrating copper
ions and mobile electrons, then returns to the magnetic field around the wire.

The first-case lesson includes **86 seconds of male Indian-English narration**,
English captions and **two native H5P questions inside the video**. Video and
voice pause together. A compact question panel keeps Check, Try again and
Continue accessible while the scene remains visible behind it.

## Public student lesson

[Open the published reference lesson](https://nimisha-raina.github.io/modlab/).
The frozen 86-second first case with apparatus highlights, compass/current
comparison and spoken summary is available locally; its publication needs GitHub
write access. Share the public link or the
[printable QR image](student-lesson/dist/share/lesson-qr.png)
([SVG version](student-lesson/dist/share/lesson-qr.svg)). Students can watch and
answer questions in their browser without an account or Blender.

## Try the interactive lesson locally

Install Python 3, Node.js and pnpm, then run:

```sh
cd student-lesson
pnpm install --frozen-lockfile
pnpm build
pnpm test
cd ..
python3 scripts/serve_lesson.py
```

Open `http://127.0.0.1:8765/`. The finished video is included, so this requires no
Blender render or voice-model account. Students need no sign-in. Answers remain
in the open page and reset on reload; scores are not collected.

## Open or rebuild the Blender scene

The completed scene is in `assets/scene/electromagnetism_intro.blend`. Open it in
**Blender 5.2.1 LTS**, enter the camera view with **Numpad 0** (or **View → Cameras
→ Active Camera**) and press **Space**. Audio is packed into the file. Real-time
viewport playback may be slower than the finished video.

To rebuild from Python:

```sh
python3 scripts/restore_assets.py
bash scripts/blender.sh --quality preview
```

The launcher finds Blender on macOS/Linux; set `BLENDER_BIN` to the installed
Blender executable if needed. On Windows, run that executable with
`--background --python-exit-code 1 --python run.py -- --quality preview`.
Alternatively, open `run.py` in Blender's **Scripting → Text Editor** and choose
**Run Script**.

The build saves `output/electromagnetism_intro.blend`, with 1,970 frames at 24 fps.
Python is the source of truth: rebuilding replaces manual edits inside the
generated lesson scene. Other scenes are retained.

The independent [compass and current section](docs/PART_01.md) has its own
Blender builder, scene checks and short silent preview renderer. It is a visual
section for the extended lesson. The connected first case now includes narration
and two H5P quiz pauses; the standalone Blender sections remain visual drafts.

Build the connected visual draft with the opening, series ammeter and compass:

```sh
blender --background --python-exit-code 1 --python scripts/build_compass_sequence.py
```

This saves `output/parts/01_compass_current/opening_and_compass.blend`.

The separate [coils and electromagnets case](docs/PART_02.md) starts at frame 1.
Its 136-second visual sequence includes winding, current reversal, more turns,
an iron core, attracted/released clips, a summary and illustrated applications:

```sh
blender --background --python-exit-code 1 --python scripts/build_coil_demo.py
```

This saves `output/parts/02_coil_reversal/coil_reversal.blend`.

For the approved checkpoint, archived media and restoration steps, read
[RESUME.md](docs/RESUME.md). [CONTINUE.md](docs/CONTINUE.md) contains a prompt for
the next development session. [The saved archive](archive/README.md) includes
movies, portable editable scenes, narration, H5P and historical revisions.

## Project map

| Path | Purpose |
| --- | --- |
| `run.py` | Blender entry point |
| `src/electromagnetism/` | Geometry, laboratory, circuit, particles, fields, camera, captions and timing |
| `scripts/` | Build, render, audio preparation, preview and verification tools |
| `docs/narration.json` | Ten spoken explanations and their source timing |
| `assets/narration/` | Recordings, normalized audio, timing and verification reports |
| `assets/scene/` | Completed portable Blender scene |
| `assets/reference/` | Build metadata and subtitles |
| `student-lesson/` | H5P questions, static webpage, completed video and pinned libraries |
| `tests/` | Pure Python motion checks |
| `output/` | Ignored working scenes, audio, renders and H5P exports |

## Continue development

The Python source currently builds a revised Blender draft with fewer overlay
panels, particles visible only in the magnified cutaway, and field guides around
all four circuit sides. The local student website now uses the approved connected
first case with narration and two quizzes. Original scene and narration assets
remain as reference material; the public website requires a separate publishing
step. See [the handoff](docs/HANDOFF.md) for current outputs and export status.

- [Handoff guide](docs/HANDOFF.md): deliverables, editing map and known limits.
- [Development guide](docs/DEVELOPMENT.md): setup, rendering, narration and checks.
- [Website guide](student-lesson/README.md): H5P content, layout and static hosting.
- [GitHub Pages guide](docs/PUBLISHING.md): activate the public site and publish updates.
- [Storyboard](docs/STORYBOARD.md): teaching sequence and source timing.
- [Science notes](docs/SCIENCE.md): physical interpretation and simplifications.
- [Reference frames](docs/RELATIVITY.md): an optional special-relativity extension.

## Licensing

Third-party components retain their upstream licences and notices. See
[THIRD_PARTY_NOTICES.md](student-lesson/THIRD_PARTY_NOTICES.md). A licence for the
original project code and lesson media has not yet been selected; public access
to this repository does not itself grant an open-source licence.
