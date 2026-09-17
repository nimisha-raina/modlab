# Part 1: Compass and current

This 34-second Blender continuation extends the opening lesson. It uses
the same laboratory and copper circuit, with headings on the physical chalkboard.
The standalone Blender section is a silent visual draft. The connected tutor
revision is 86 seconds, with male Indian-English narration and two H5P
quiz pauses in the local website. The public deployment remains the reference
release until a separate publishing step.

## Sequence

| Time | Action |
| --- | --- |
| 0–0.5 s | Continue from the opening's wide camera pose with the switch closed and guides at six locations, including the original three circles. |
| 0.5–5 s | Compass moves into place beside the wire; its needle follows the combined field as it approaches. Camera moves closer. |
| 5–9 s | Hold the reference-current comparison; series ammeter reads 0.50 A. |
| 9–13.5 s | Camera visits the second board heading and returns to the same close-up. |
| 14–14.8 s | Current increases to 1.00 A; drawn circles double at every location and compass deflection increases from 25° to approximately 43°. |
| 14.8–21 s | Hold the doubled-current comparison. |
| 21–24 s | Restore 0.50 A and hold the apparatus view. |
| 24–26 s | Return smoothly to the laboratory board; summary replaces the previous heading as this movement starts. |
| 26–34 s | Hold four summary points on the board. |

After placement, the compass position and the two comparison camera poses are
identical. A round black analogue ammeter sits along the left-side copper branch,
connected in series through a real gap with short connections concealed behind
the housing. No red or black leads appear across the front of the circuit.
Its white dial has a centre-zero −1 to +1 A scale and an animated red pointer.
A compact on-face numerical reading also tracks the current ramps. The selected
0.50 A and 1.00 A values are illustrative readings rather than measurements from
a specified real battery and resistor. The series limiter has an animated
control. Microscopic electrons and ions belong
to the opening cutaway and are not shown in this section.

## Reviewed base build

The base connected opening holds a wide view of both the physical experiment board
and the full table for three seconds from a farther viewpoint, then approaches
the atoms over eight seconds, reaching them at second 11. Switch closure at
second 14 starts an eight-second electron-flow close-up; particle movement and
marker size are unchanged. Particles hide as pullback begins at second 22;
the copper surface closes by second 23 and cutaway shell/rims hide then. The
overview therefore shows a solid continuous wire. Concealed rear connections join the
instrument terminals to the separated ends of the left-side copper conductor. The round housing, white scale and needle
are modelled geometry; no reference photograph is distributed as an asset.
Making a coil and reversing current are a separate frame-one case described
in [PART_02.md](PART_02.md).

The connected visual assembly retains the opening's zoom, copper cutaway,
electron drift, field generation and zoom-out. It ends that opening at source
second 42, before the original switch-off finale, then continues directly to
compass placement. The ammeter is already in the opening circuit: it reads zero
with the switch open and 0.50 A after closure. The resulting silent draft lasts
76 seconds at source timing, including the ten-second summary ending. The tutor
revision below retimes this base to fit the spoken tour without accelerating speech.
The normal `run.py` build still retains its original ending.

Run from the repository root with Python and Blender available on PATH:

```sh
python -m unittest discover -s tests
blender --background --python-exit-code 1 --python scripts/build_current_demo.py
blender --background output/parts/01_compass_current/compass_current.blend --python-exit-code 1 --python scripts/verify_current_demo.py
blender --background output/parts/01_compass_current/compass_current.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --stills 0 8 11 18
blender --background output/parts/01_compass_current/compass_current.blend --python-exit-code 1 --python scripts/render_current_demo.py
```

To build, check and render the connected preview:

```sh
blender --background --python-exit-code 1 --python scripts/build_compass_sequence.py
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/verify_compass_sequence.py
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/verify_current_demo.py
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --combined
```

The connected `.blend` holds two camera scenes and a sequencer assembly of those
scenes. This keeps each section separately editable with a continuous camera at
the join. The connected file opens in the sequencer preview. For 3D editing,
switch to the Modeling workspace and select the opening or compass scene.
Viewport playback can be slower than the exported MP4; use the video to judge
camera pacing. The connected draft uses EEVEE with eight samples for practical
review. `--combined --stills 5 12 41.9 42 50 60` renders selected assembly views.
When only the continuation changes, load that connected `.blend` and run
`scripts/build_compass_sequence.py -- --reuse-opening` to preserve the existing
opening scene. Rebuild both sections if the laboratory, circuit or opening changes.

For faster video export, render each camera scene directly, then join the two
MP4s without re-encoding. The join and media check use the optional media
environment; substitute its Windows `Scripts/python.exe` path when needed:

```sh
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --opening-only
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/render_current_demo.py
.venv-media/bin/python scripts/join_compass_preview.py
.venv-media/bin/python scripts/verify_compass_preview.py --combined
.venv-media/bin/python scripts/verify_compass_preview.py
```

Use `--full-quality` consistently on both renders, the join and validation for
the 720p version. The saved sequencer assembly remains the editing timeline.
After the first export, reuse `opening_preview.mp4` while editing only the
compass continuation: render that section and join again. Refresh the opening
clip when its appearance or timing changes. This keeps incremental review practical.

On Windows, invoke the installed Blender executable using PowerShell's `&`
operator when it is not on PATH. No additional Python packages, voice downloads
or website rebuild are needed for these commands.

Outputs are in ignored `output/parts/01_compass_current/`:

- `compass_current.blend`: editable scene with baked motion at 24 fps.
- `review_*.png`: selected layout checks.
- `compass_current_preview.mp4`: silent 640×360, 12 fps draft.
- `build-info.json`: duration, frame rate and compass deflections.
- `opening_and_compass.blend`: editable connected visual assembly.
- `opening_and_compass_preview.mp4`: connected silent draft at source timing.

Pass `--full-quality` to the render script for a 1280×720, 24 fps MP4 named
`compass_current_720p.mp4`. Rendering leaves the saved scene's settings intact.
Review motion, board readability, field arrows and both needle positions before
producing final media. Automated checks do not replace watching the preview.

## Validation status

The section was built and checked with Blender 5.2.0 LTS on Windows. All seventeen
Python tests passed, including finite-wire direction, field scaling, compass
angle, coil winding/polarity, series conductor route, settled compass position and continuous camera
motion. The Blender verifier passed compass placement, 6/12 guide counts, closed
switch, frame-accurate ammeter readings, repeated comparison framing and board
visibility checks. The assembly verifier checks the complete timeline and camera,
switch and current continuity at the join. Rendered views are also inspected.

The earlier compass-build MP4 caches were decoded and verified at 12 fps and 640×360 pixels, with
regular frame timestamps and no audio stream: 504 frames / 42 seconds for the
opening, 288 frames / 24 seconds for the compass continuation, and 792 frames /
66 seconds for the connected preview. Metadata and recording hashes are in
`opening-preview-validation.json`, `preview-validation.json` and
`connected-preview-validation.json`. Selected encoded frames were reviewed.
Final narrated assembly requires new synchronization checks.
Those full-movie caches precede the round analogue meter, wide opening and
faster visible drift. Rebuilding a scene does not refresh a movie. Use focused
exports to review these revisions without rendering the whole lesson:

```sh
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --opening-only --range 0 15
python scripts/verify_compass_preview.py --opening-only --range 0 15
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --range 8 18 --draft-fps 6
python scripts/verify_compass_preview.py --range 8 18 --draft-fps 6
```

The first focused clip is 15 seconds at 12 fps and covers the wide opening,
zoom, random motion and rightward drift after switch closure. The second is
10 seconds at 6 fps and compares the analogue readings and compass. Use the
media environment for decoding checks. Segment exports and their validation
reports are named with their source-time intervals. Review electron motion at
12 or 24 fps: 4/6-fps sampling can make repeated markers appear to move backwards.

The previous apparatus version of both focused clips was fully decoded and passed the duration, dimensions,
silence and timestamp checks: 180 frames / 15 seconds at 12 fps for the opening,
and 60 frames / 10 seconds at 6 fps for the current comparison. Selected encoded
frames were inspected. The interval-specific validation reports sit beside
their movies in the output directory. These clips predate the concealed rear
connections and revised panel-meter face. For apparatus review, load the rebuilt
`compass_current.blend` and run `scripts/render_apparatus_review.py`; this writes
1600×900 circuit and detail stills without exporting video.

## Physics and limitations

The horizontal compass needle follows the sum of a fixed horizontal Earth field
and the field calculated from the finite straight segments of the entire closed
circuit, including the ammeter's series lead route. The supply and ammeter's
internal conductor are idealized straight connections. Geometry uses relative
units; reference current corresponds to the illustrative 0.50 A reading. The
chosen Earth-field orientation and relative
strength give a 25° deflection at I and approximately 43° at 2I.

Doubling current doubles the wire's field at the same point; it does not double
the compass angle. With perpendicular horizontal fields, `tan(angle)` is
proportional to current. The needle is animated smoothly along the calculated
equilibrium direction; inertia, oscillations, magnetic dip and switch transients
are not simulated.

Six local guide circles at I become twelve at 2I. This is a drawing convention
for increased field strength, not a count of physical objects. These local
circles are not numerical traces of the complete circuit's resultant field.
Earth's field affects the needle but is not drawn as additional lines. See
[SCIENCE.md](SCIENCE.md) for source references and the opening lesson's assumptions.

## Source map and next sections

- `current_demo.py`: pure timing, camera poses and compass field calculation.
- `current_chapter.py`: assembly, current control, guides and baked animation.
- `compass.py`: reusable dial, pivot and red north-seeking needle.
- `chalkboard.py`: reusable, fitted physical board headings.
- `ammeter.py`: series circuit insertion, physical meter and animated readings.
- `scripts/verify_current_demo.py`: checks the generated scene, fixed compass,
  current cases, guide counts, camera continuity and board framing.
- `scripts/build_compass_sequence.py` and `verify_compass_sequence.py`: visual
  assembly and continuity checks for the opening and compass join.

These modules live under `src/electromagnetism/`. The opening lesson still builds
through `run.py`; this section has its own entry point and output directory.

The six-turn coil, combined field, poles, compass and reversal are implemented
as the separate case in [PART_02.md](PART_02.md). Subsequent sections will add
a soft iron core and paper clips, switch off and release the clips, and show
practical applications. Narration and paused-video H5P questions for subsequent
cases follow review of those Blender sections. The first case is integrated below.

## Complete visual review

The complete first case contains the existing 66-second demonstration followed
by a two-second camera return and eight-second summary-board hold. The summary
covers electron drift direction, current creating a magnetic field, compass
detection and increased field strength with increased current. The numeric
current reading is enlarged on the dial. Both comparison poses are identical;
the scene verifier also checks projected reading size at 720p and summary framing.
The original three circles remain through the pullback and compass join at
the same wire location. Five other sites complete the six-location layout:
eight baseline circles become sixteen at twice the current. The nearby compass
reading and arc measure deflection relative to its fixed north reference;
displayed whole degrees are illustrative, not a universal current-to-angle law.
Headings omit case numbers. The summary is active from global second 66,
including the camera return, and the current-limiting component is labelled
"Resistor". The white dial, printed ink and pointer have separated depth layers;
the camera's 0.05-unit near plane improves depth precision in distant views.

```sh
blender --background output/parts/01_compass_current/opening_and_compass.blend --python-exit-code 1 --python scripts/render_complete_preview.py
python scripts/render_complete_preview.py --encode
python scripts/verify_compass_preview.py --combined --review-720p
```

Run the encode and decoding commands in the media environment. This produces
`opening_and_compass_review_720p.mp4`: a 1280×720, 12-fps silent visual review.
The complete 76-second interval contains 912 encoded frames. Each source frame
is evaluated; identical visible states reuse the preceding PNG while preserving
its full duration. Pose, text, shape-key and animated shader states are included
in this check. Frame PNGs and the render count report stay in the ignored output
folder. Rendering leaves the editable 24-fps project intact. Final spoken timing
and H5P authoring follow the visual review.

The current complete review passed the encoded-media check: 912 frames,
76.0 seconds, 1280×720, 12 fps, regular timestamps and no audio stream. Its
render report records 603 rendered frames and 309 reused stills. Encoded frames
were inspected at the opening, copper close-up, solid-wire return, compass
join, both current readings and final summary. The Blender scene checks passed
for current and camera continuity, persistent circles at six locations,
eight/sixteen drawn circles, compass angles and degree readings, meter
readings and summary visibility. The projected numerical readings measure
37.5 and 36.0 pixels high at 720p in the comparison shots. Validation reports
remain beside the movie in the ignored output directory.
An additional encoded-image check sampled the projected dial interior in 483
visible frames. At least 95.3% of samples stayed light in every tested frame,
allowing for printed markings and the pointer; no large dark face patches were
detected. This is a sampled check, supplemented by inspection of keyframes.
All 17 pure Python tests and the main scene verifier also passed.

## Tutor revision and H5P

`docs/first-case-narration.json` supplies fourteen short male Indian-English tutor
lines. The final movie is `opening_and_compass_narrated_720p.mp4`, with normalized,
faded AAC speech and five spoken-name apparatus pointers. The tutor scene is
`opening_and_compass_tutor.blend`; the reviewed base scene remains 76 seconds.
The revised opening holds the board/apparatus for ten seconds, zooms during the
atomic-level introduction over eight seconds, explains random electron motion
and copper-ion vibration over five seconds, and closes the switch at second 23.
The visible drift lasts eight seconds. The overview transition is shortened from
ten seconds to seven; compass placement begins at 48 and the unchanged compass
experiment keeps its timing. The laboratory summary begins at 72, opening with
"To summarize what we have learned". After the camera arrives at second 74, the
board holds to second 86 so the spoken recap fits without accelerating speech.
The local H5P lesson pauses at 30.7 and 68.7 seconds for two native questions on
current producing a field and increased current strengthening it. The compact
upper-right panel leaves the apparatus visible on desktop, and its native action
footer stays separate from scrolling question content. See
[DEVELOPMENT.md](DEVELOPMENT.md#current-first-case-narration-workflow) for commands.

Re-render after future camera, dial or compass-indicator changes. Check
apparatus and transition stills first with
`scripts/render_complete_preview.py -- --stills-only` in Blender. A rebuild
does not update the prior movie or its validation report.
