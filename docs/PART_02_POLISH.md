# Case 2 bilingual presentation revision

## Scope

Case 1 is frozen at source revision `43d667a94a4aa788eae8ccc51971aba55c65e853`.
This revision changes Case 2 only: brighter headings and labels, travelling
yellow conventional-current arrows, clearer turquoise field arrows, improved
instrument readings, previous-position compass markers and measurement
comparisons. The right-hand resistor and its adjoining leads share a straight
axis. The three application pictures retain high-contrast component circles
throughout the final 11 seconds.

The geometry still compares 10 turns, 20 turns of the same length and diameter,
and 20 turns with a soft-iron core, all at the same current magnitude. The
illustrative compass readings are 30°, 51° and 79°. They are outputs of the
teaching model, not predictions for a particular laboratory instrument.

English uses the approved polished Prabhat voice and its Case 1 delivery
settings. Hindi uses Swara and the approved तांबे speech spelling; displayed
Hindi retains ताँबे. The student-facing language name is हिंदी. Legacy internal
`hinglish` paths remain compatible with saved lessons and restoration scripts.
English narration lasts 239.167 seconds; Hindi lasts 289 seconds. No speech is
accelerated. Each language receives its own localized picture track. The video
exports are 1280 × 720 at 12 frames per second; editable scenes use 24 frames
per second, with animation timing mapped to each narration track.

## Build

Use the existing media Python environment and Blender installation. Run:

```sh
python scripts/generate_tutor_narration.py --script docs/coil-narration-english.json
python scripts/generate_tutor_narration.py --script docs/coil-narration-hinglish.json
python scripts/prepare_coil_bilingual.py
blender --background --python-exit-code 1 --python scripts/build_coil_bilingual.py -- --source-only
python scripts/prepare_coil_text.py
blender --background --python-exit-code 1 --python scripts/build_coil_language_scene.py
python scripts/render_coil_languages.py --language english --blender /path/to/blender
python scripts/render_coil_languages.py --language hinglish --blender /path/to/blender
python scripts/verify_coil_languages.py
python student-lesson/scripts/build_coil_h5p.py
```

Render scripts use independent, resumable batches and validate cached PNGs
before reuse. Cache identity includes source-scene hashes, visible transforms,
shader states and absolute winding shape-key time. Hindi letters are shaped
with the existing Windows text renderer and packed into Blender; no font
installation is required for playback or reopening a packed scene.

Run `verify_coil_fixed_view.py` inside each delivered Blender scene. It checks
switch/field timing, right-hand directions, three field strengths, equal
compass readings, framing, packed speech and the applications interval.
Run the Python suite, both language-selection tests and the native H5P suite
with `COIL_LANGUAGE=english` and `COIL_LANGUAGE=hinglish`. Check playback,
question retry and Continue in the browser before publishing.

## Checkpoint

The localized videos and H5P packages are complete. Both narration tracks pass
word-coverage checks for all 19 sections. The source and packed narration scenes
pass physics, contact-timing and framing checks. English and Hindi keyframes were
visually inspected, including the corrected application-highlight layering.
The 31 Python checks and the complete 14-test lesson suite pass. Encoded-media
verification confirms every narration section, the exact scene-picture mapping,
12-fps frame counts and silence at all eight question pauses. Browser checks
confirm language selection, the final movie durations, retry and Continue, and
a visible Continue footer at 390 × 844. The source and media are saved on the
main branch; publish the verified build to `gh-pages` for the public lesson.

Working assets are in `output/parts/02_coil_reversal/bilingual/`. A local copy
of the previous delivery is preserved under
`backups/case-two-before-polish-20260922/`; the public archive and Git history
also retain that release. Update this checkpoint after final verification.
