# Case 2: English and Hinglish interactive lesson

The current revision adds an opening narration choice, contact-synchronized
magnetic fields, the approved 60-degree right-hand nail view and four genuine
H5P prediction questions. The earlier fixed-camera English review and frozen
Case 1 remain preserved.

## Lesson behaviour

- The switch blade can move while the circuit remains open. Current, wire-field
  circles, solenoid field, pole labels and ON/OFF cues share one contact state.
  Closing the contact turns the field on; opening it turns the field off.
- The front view remains fixed except during source seconds 66–80. The camera
  moves right to 60 degrees, shows nail insertion with the switch OFF, holds for
  switch-on and the stronger field, then returns to the original front view.
- The 10/20-turn comparison keeps coil length, diameter and current unchanged.
- The magnetic-region explanation explicitly opens and closes the switch.
  Mixed directions appear while OFF. On closing, a gold circular current arrow
  appears, labelled as an end view from the north pole. A separate blue arrow
  shows the axial coil field. Gold arrows within fixed regions align with it.
  This distinguishes current circulation from magnetic-field direction.
- Clips lift from below the exposed nail ends and fall after switch opening.
- The summary and three application pictures remain; all magnetic-component
  highlights stay visible throughout the final 11 seconds.

## Narration and timing

`docs/coil-narration-english.json` and `docs/coil-narration-hinglish.json` contain
19 equivalent sections. Hinglish combines conversational Hindi with English
science terms. Both tracks use the same Indian male speaker, `hi-IN-MadhurNeural`.
The earlier `en-IN-PrabhatNeural` English voice omitted Devanagari words in a
mixed-language sample, so it is not used for either new track.

English lasts **255 seconds** and Hinglish **303.83 seconds**. A 301.5-second
visual master is rendered once; each export samples the equivalent explanation
progress for its own natural-speed narration. Nearest-frame sampling introduces
at most 1/12 second of master-picture quantization at 6 fps. Each language has
its own packed scene, caption times and H5P pauses, avoiding long English holds.
Neither voice is accelerated. The final applications window remains 11 seconds.
Speech preparation normalizes loudness and applies short cosine fades.
Hinglish says "switch ON" and "switch OFF" explicitly, avoiding the ambiguous
everyday meaning of "switch बंद" when discussing a closed circuit.
Word-boundary coverage checks detect omitted script words; they do not replace
a listening review of accent or pronunciation.

## Files

Working output is under `output/parts/02_coil_reversal/bilingual/`:

- `coil_bilingual_source.blend`: unretimed 136-second storyboard.
- `coil_visual_master.blend`: saved picture-render input with a guide soundtrack.
- `coil_english.blend` / `coil_hinglish.blend`: 24-fps editable scenes, packed speech.
- `coil_english_720p.mp4` / `coil_hinglish_720p.mp4`: 720p, 6-fps review exports.
- `audio_english/` / `audio_hinglish/`: recorded clips, provenance, prepared
  soundtracks, language-specific timing and audio verification.
- `render.json`, `verification-*.json`, `speech-verification.json` and
  `media-verification.json`: source, scene and delivery checks.
- `bilingual_frames/`: reproducible render cache, excluded from public archives.

The opening language choice is at `student-lesson/dist/coils/index.html`.
It loads only the selected H5P lesson and narration. Changing language restarts
the lesson; it does not continue at a mismatched point in another track.
Separate importable packages are `output/share/coil-english.h5p` and
`output/share/coil-hinglish.h5p`. The standalone webpage supplies language
selection; each importable H5P package is a single-language lesson.

## H5P behaviour

Four native `H5P.MultiChoice` interactions pause the `H5P.InteractiveVideo`:
current reversal, more turns, inserting soft iron and releasing the clips.
Each occurs in silence before the predicted result. The chosen language controls
the question wording and button labels as well as narration and captions.
Wrong answers receive feedback and Retry. Correct answers unlock H5P's native
Continue button. Compact panels retain a separate, non-scrolling button footer.
Answers remain in the session; names and scores are not submitted or stored.

The video is a guided prediction lesson, not a numerical simulation with
student-adjustable circuit parameters. Field-line counts, equal compass
deflections and soft-iron gain remain illustrative; see `SCIENCE.md`.

## Build and validate

### Saved media checks

The delivered English movie contains 1,530 frames; Hinglish contains 1,823.
All 38 speech sections passed text-coverage and decoded-audio alignment checks.
The maximum measured audio offset was zero at the verifier's sampling precision;
minimum waveform correlation exceeded 0.994. Both movies decode fully, and
sampled pictures match their recorded master-frame mapping.
Browser checks completed all four pauses in both languages, tested wrong-answer
retry, and confirmed visible native Continue controls on desktop and at 390×844.
Language changes restart at the opening choice. No browser errors were reported.

Thirty Python checks pass. The native H5P suites pass for Case 1 and both new
languages, including incorrect answers, retry, correct answers and Continue.
Both portable narration scenes reopen with packed assets and pass the scene
checks. Windows Blender emitted a thumbnail-cache warning while saving; the
saved scene contents and reopened files passed verification.

### Rebuild commands

Use the existing media Python environment and Blender. Unchanged recordings are
cached; no voice-model download is required. Generate only after script changes:

```sh
python scripts/generate_tutor_narration.py --script docs/coil-narration-english.json
python scripts/generate_tutor_narration.py --script docs/coil-narration-hinglish.json
python scripts/prepare_coil_bilingual.py
python scripts/verify_coil_languages.py --speech-only
python -m unittest discover -s tests
blender --background --python-exit-code 1 --python scripts/build_coil_bilingual.py
blender --background output/parts/02_coil_reversal/bilingual/coil_english.blend --python-exit-code 1 --python scripts/verify_coil_fixed_view.py
blender --background output/parts/02_coil_reversal/bilingual/coil_hinglish.blend --python-exit-code 1 --python scripts/verify_coil_fixed_view.py
blender --background --gpu-backend opengl output/parts/02_coil_reversal/bilingual/coil_visual_master.blend --python-exit-code 1 --python scripts/render_coil_bilingual.py -- --stills 6 70 76 83 89
blender --background --gpu-backend opengl output/parts/02_coil_reversal/bilingual/coil_visual_master.blend --python-exit-code 1 --python scripts/render_coil_bilingual.py
python scripts/render_coil_bilingual.py --encode
python scripts/verify_coil_languages.py
python student-lesson/scripts/build_coil_h5p.py
node --test student-lesson/tests/coil-language.test.cjs
node --test student-lesson/tests/h5p.test.cjs
```

Run the native H5P suite once more with `COIL_LANGUAGE=english`, then
`COIL_LANGUAGE=hinglish` (on PowerShell set `$env:COIL_LANGUAGE` before each run).
The default suite still checks Case 1. Clear the variable afterwards.
Preview with `python scripts/serve_lesson.py`, then open
`http://127.0.0.1:8765/coils/`. Check both language choices, all four pauses,
retry and Continue on desktop and mobile before deployment.

`coil_switch.py` is the single source for electrical contact timing.
`coil_camera.py` and `coil_orbit_labels.py` handle the temporary viewpoint.
`coil_board.py` owns the magnetic-region diagram. The narration preparation
allocates a render-master timeline and independent delivery timelines. One
render cache serves both languages without slowing or speeding their speech.
Never apply narration retiming to an already narrated scene.

For speech-only revisions with unchanged storyboard sections, use
`prepare_coil_bilingual.py --keep-master`, then `retime_coil_languages.py`
and encode again. The existing master scene, its timeline and frame cache stay
unchanged; revised speech gets its own delivery timeline. The final ON/OFF
wording update used this route. No picture render was repeated.
