# Part 2: six-turn coil and current reversal

This independent Blender case starts at frame 1. It lasts 28 seconds at 24 fps
and reuses the school laboratory, circuit, series ammeter and physical compass.
It is a silent visual draft; finalize narration and H5P after the visual sequence.

## Timeline

| Seconds | Demonstration |
| --- | --- |
| 0–2 | Read the physical board: making a six-turn coil. |
| 2–5 | Move to the wire and instruments. |
| 5–11 | Reconfigure the top wire in the earlier microscopic viewing area into six spaced turns. |
| 11–15 | Local wire guides become a combined solenoid field pattern. |
| 15–17 | Show N/S poles, compass deflection and 0.50 A. |
| 17–22 | Read the reversal heading, then return to the same apparatus view. |
| 22–22.5 | Open the knife switch; current and coil field fall to zero. |
| 22.5–24.5 | Lift and turn the disconnected cell to swap its circuit connections. |
| 24.5–25 | Close the switch; current flows in the opposite direction. |
| 25–28 | Show exchanged poles, reversed field arrows, changed needle and −0.50 A. |

The round analogue ammeter sits along the left copper branch. Its concealed rear
connections stay fixed, and its centre-zero needle crosses zero into the negative
half of the scale after reversal. The on-face minus sign indicates reverse current;
the magnitude is still 0.50 A. The cell's physical terminals retain their
chemical polarity; rotating the cell changes which circuit end is positive.

## Build and review

Run from the repository root, with Python and Blender on the executable path:

```sh
python -m unittest discover -s tests -v
blender --background --python-exit-code 1 --python scripts/build_coil_demo.py
blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/verify_coil_demo.py
blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --coil --stills 0 8 16 23.5 26
blender --background output/parts/02_coil_reversal/coil_reversal.blend --python-exit-code 1 --python scripts/render_current_demo.py -- --coil --draft-fps 6
python scripts/verify_compass_preview.py --coil --draft-fps 6
```

The editable file is `output/parts/02_coil_reversal/coil_reversal.blend`.
`--draft-fps 6` produces a small 640×360 motion review named
`coil_reversal_draft_6fps.mp4`. Omit it for the normal 12-fps preview, or use
`--full-quality` for 1280×720 at 24 fps. Rendering does not overwrite the `.blend`.

For a focused correction, `--coil --draft-fps 6 --range 17 20` renders only
that three-second source interval to a separately named segment movie. Range
endpoints must align with the selected frame rate. This leaves the full draft
movie unchanged and makes small visual corrections quicker to inspect.

The saved scene passed the Blender verifier, including both board headings,
pole visibility, disconnected cell reversal, compass response and signed meter
readings. All seventeen Python tests and both existing H5P tests passed. The
earlier silent 6-fps draft was fully decoded: 168 frames, 28 seconds, 640×360,
regular timestamps and no audio stream. Encoded views were inspected, including
the board, coil poles, switch-open cell turn and reversed state. Its validation
report is `output/parts/02_coil_reversal/preview-validation-6fps.json`.
That full-movie cache predates the round analogue meter and wider apparatus
view. Rebuild, inspect fresh stills and render the affected interval before
using a movie as evidence of those changes. The media verifier accepts the
same `--range START END` arguments as the renderer.

## Science and implementation

- `coil_demo.py` contains timings, the six-turn helix, circuit field calculation,
  fixed Earth field and compass angles, without Blender imports.
- `coil_chapter.py` assembles the apparatus, board headings, poles and animation.
- `morph_geometry.py` provides editable mesh shape keys for wire and guide poses.
- The winding's forward conventional current gives an internal field toward
  −X, with N on the left and S on the right. Reversal swaps these directions.
- Resultant guides are closed traces of an axisymmetric six-ring approximation
  to a finite coil. Arrows run S→N inside and N→S outside. Compass calculations
  include the actual helical segment, its connecting circuit and Earth's field.
- The needle follows the horizontal component of the total field. Reversal
  need not turn it exactly 180 degrees because Earth's field remains present.
- The wire morph represents reconfiguring a longer copper segment. Its changing
  drawn length is not a material-stretch simulation. Turns are spaced apart.
- The guide morph illustrates how contributions combine; field lines are a
  drawing convention, not objects physically transported by bending copper.
- This case has no iron core. Adding the nail and clips belongs to a later case.

Reference: [OpenStax: solenoids and toroids](https://openstax.org/books/university-physics-volume-2/pages/12-6-solenoids-and-toroids)
and [magnetic fields and lines](https://openstax.org/books/university-physics-volume-2/pages/11-2-magnetic-fields-and-lines).
