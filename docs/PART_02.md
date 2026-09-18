# Case 2: coils and electromagnets

This independent 136-second visual lesson starts at frame 1, with the switch OFF.
Its editable source has 3,264 frames at 24 fps. Case 1 remains frozen under
`output/parts/frozen_case_01/`, with SHA-256 checksums in its manifest.
The Case 2 preview is silent; narration and H5P can follow the visual review.

## Timeline

| Seconds | Demonstration |
| --- | --- |
| 0–9 | Show the laboratory and board; approach the straight copper wire. Switch OFF. |
| 9–14 | Form ten turns in five seconds. The winding occupies about half the screen; supply connections stay outside the crop. |
| 14–20 | Pull back, close the switch at 15–16 seconds, reveal upper/lower turn contributions, then crossfade to closed bar-magnet-like field guides. |
| 20–28 | Reveal N/S, place two smaller compasses, let needles settle, display deflection readings. Current: 0.50 A. |
| 28–44 | Read the reversal heading; open the switch, turn the cell while disconnected, close the switch. Poles, needles and arrows reverse. Gold arrows before, blue after. |
| 44–66 | Switch OFF; change 10 turns to 20 with unchanged axial length, smaller diameter and smaller gaps. Switch ON at the same current magnitude. Denser field guides and greater deflection. |
| 66–80 | Move compasses outward; approach from the right. Switch OFF; insert a soft-iron nail; switch ON. Stronger field and compass response. |
| 80–90 | Board close-up: fixed magnetic regions inside a nail outline; electron-flow and internal-field arrows explain alignment. |
| 90–94 | Return to the stronger electromagnet and compass readings. |
| 94–114 | Switch OFF, bring six paper clips, switch ON to attract them, switch OFF to release them onto the table. |
| 114–125 | Move to the summary board: poles, reversal, packed turns, iron core and controlled release. |
| 125–136 | All three application pictures appear together for 11 seconds: scrapyard crane, dynamic microphone and MRI. All magnetic components remain highlighted throughout. |

## Build and review

Run from the project root, using Blender and the media Python environment:

```sh
python -m unittest discover -s tests -v
python scripts/freeze_case_one.py
blender --background --python-exit-code 1 --python scripts/build_coil_demo.py
blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/verify_coil_demo.py
blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/render_coil_review.py
python scripts/render_coil_review.py --encode
python scripts/verify_compass_preview.py --coil --draft-fps 6
```

The media environment includes NumPy for the vectorized-field regression check,
Pillow for frame encoding, and imageio-ffmpeg. Blender supplies its own NumPy;
the basic Python suite skips the vectorized check if NumPy is absent.

The complete motion review is `output/parts/02_coil_reversal/coil_reversal_draft_6fps.mp4`
at 640×360 and 6 fps. It is a visual draft, not the final delivery encode.
The review renderer fingerprints visible geometry, evaluated transforms, wire/field
shape-key poses and guide opacity, and reuses identical stationary states.
Cached PNGs permit an interrupted render to resume. The saved source file's
checksum and output dimensions isolate caches across source revisions. Rebuild
and save the scene after changing geometry, lights, textures or materials.
`--width 1280` supports a
sharper review, with the same preview frame rate.
Validate that variant with `verify_compass_preview.py --coil --draft-fps 6 --width 1280`.

For selected 720p stills:

```sh
blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --coil --review-720p --stills 0 14 26 42 61 93 108 113.25 120 125 130 135.8
```

The efficient renderer also accepts `--stills 108 86 120` to make selected
720p images before the complete draft, sharing the same Blender process.
For camera-only changes on the same timeline, run
`blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/refresh_coil_camera.py`,
then rerun the saved-scene check. Geometry or experiment changes require the builder.
For board-only edits on an unchanged timeline, `scripts/refresh_coil_board.py`
replaces the timed writing, region model and application panels in the loaded
Case 2 scene. Render and validate again afterward. The builder applies the
same board content on a fresh scene.
`scripts/refresh_coil_annotations.py` applies the current inside/outside caption
layout and compass-reading clearance to an existing scene on the same timeline.

For a full 720p, 24-fps silent movie, use `render_current_demo.py -- --coil --full-quality`.
Render commands do not save over the editable scene. Earlier 48-second previews
are preserved as `coil_reversal_before_extended_experiments.blend` and `.mp4`.

## Validation of the complete visual draft

All 22 Python tests and the saved Blender scene checks pass. The encoded movie
decodes to 816 regularly timed frames: 136 seconds, 640×360, 6 fps, no audio.
The editable scene retains 24 fps. Its media report is
`output/parts/02_coil_reversal/preview-validation-6fps.json`.
The renderer used 530 distinct scene states. The 11-second applications
ending has 66 frames sharing one identical render; saved-scene checks confirm
all three component highlights remain visible on every source frame of that stage.
Rendered and encoded winding, local/resultant fields, forward/reversed poles,
dense coil, nail, region alignment, slower clip release, summary and applications
frames were inspected. Case 1's frozen checksums remain unchanged.
The previous complete draft is preserved as `*_before_field_spacing_revision.*`.
`coil_reversal_field_revision_6fps.mp4` is an identical copy of the latest preview,
with a distinct filename for review players that cache earlier versions.

Blender 5.2.0 LTS on Windows issued a nonfatal thumbnail-cache write warning when
saving. The saved file reopened successfully and passed the scene checks.

## Science and implementation

- `coil_demo.py`: timing, configuration, complete-circuit field and shared Earth field.
- `coil_keyframes.py`: every moving source frame plus stationary hold boundaries,
  avoiding redundant animation keys in the longer lesson.
- `coil_camera.py`: camera motion, independently refreshable after framing edits.
- `wire_winding.py`: cropped configuration transition, with fixed end connections
  and wire thickness. It does not conserve the drawn wire length. A real coil
  needs a longer wire, wound deliberately; current does not stretch the wire.
- `coil_chapter.py`: apparatus assembly, smaller compasses, readings, moving arrows
  and illustrative guide density (10 initial, 16 dense-coil, 24 iron-core guides).
- `coil_strength_guides.py`: interleaved, evenly spread stronger-field families.
- `coil_annotations.py`: comparison captions with clear space around the field
  drawing; clip close-ups retain the guides without extra comparison captions.
- `coil_field_transition.py` and `coil_upper_guides.py`: local upper/lower contributions
  fade into a resultant field; lines are drawings, not strings physically joining.
- `ring_field.py`: vectorized finite-segment field for the axisymmetric ring drawing.
  Compass calculations use the actual helix and complete connecting circuit.
- `coil_experiments.py`: physical switch state, nail insertion and six attracted/released clips.
- `coil_board.py`: headings, summary, magnetic-region model and packed application pictures.

Forward conventional current gives an internal field toward −X, left N and right S.
Both **MAGNETIC FIELD INSIDE COIL** and **MAGNETIC FIELD OUTSIDE COIL**
are labelled with large direction arrows. Finite-ring traces use fourth-order
integration; loop families are selected by evenly spaced outer extents and
redistributed when more guides appear. Guide density indicates relative strength,
not a count of physical lines. General visual changes require rebuilding.
Inside arrows run S→N, outside N→S. Reversal swaps these directions. A centre-zero
analogue meter shows −0.50 A afterward, indicating reversed current of the same
magnitude; its terminals and concealed rear connections remain fixed.
The compasses move 0.22 units outward during the nail stage; their readings
use those actual positions and retain the same common Earth field.
Deflection readings sit beneath the stands, clear of their dials and stems.
Both compass red north tips follow the resultant horizontal coil/circuit/Earth
field. They need not point opposite ways at opposite coil ends or turn exactly
180 degrees on reversal, since Earth's field remains. Degree values illustrate
this model; they are not measurements of a specified classroom apparatus.

The 20-turn coil has the same 3.2-unit axial length, radius 0.52 instead of 0.62,
and pitch 0.16 instead of 0.32. Wire diameter stays 0.13; final turns remain separated.
Both turn density and diameter change, so the comparison is not a controlled
measurement of turn count alone. A regulated supply maintains 0.50 A magnitude
while geometry and core change; a bare battery would not guarantee this.

Iron-core strength uses an illustrative threefold gain on the coil contribution,
leaving branch fields and Earth's field unchanged. It is not a calculation of a
real nail's permeability, saturation or hysteresis. The board's alignment sequence
is a magnified explanatory replay: magnetic directions of groups of atoms/domains
align, rather than iron atoms changing position. Fixed boundaries remain inside
a nail-shaped outline. After reversal, electron flow along the winding is right
to left, while the internal field and aligned magnetic north tips point right.
Electron flow alone does not determine an axial direction without specifying
the winding sense. A low-remanence soft-iron core
is assumed for clip release; a hardened steel nail may retain appreciable magnetism.
Clip attraction and the deliberately slowed 1.2-second release are teaching
animations, not force simulations. The final camera aims lower so the summary
and applications board sits higher in the picture.
During the core stage the meridional guide plane tilts by 0.35 radians, showing
depth around the solenoid. This changes the drawing viewpoint, not the axial
field direction or the compass calculation. The wider right-side camera retains
the battery and switch-state sign during insertion and the stronger-field view.

Application cutaways are conceptual pictures. A dynamic microphone uses a moving
coil and a permanent magnet to induce a signal; it is an application of
**electromagnetism**, not a powered iron-core lifting electromagnet. MRI magnet
windings are illustrated schematically. See the asset brief and sources in
[application artwork](../assets/lesson-applications/README.md).
