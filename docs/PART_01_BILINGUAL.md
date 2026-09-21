# Case 1: English and Hindi

This revision develops the preserved 86-second first case. It adds travelling conventional
current arrows, a gradual rightward camera view at 60° azimuth, fuller particle
explanations, and a language choice before playback. The original remains under
`output/parts/frozen_case_01/`; Case 2 is unchanged.

## Student experience

- English: 156.083 seconds. Hindi: 187.833 seconds. Speech runs at its natural
  rate; each language has an independently measured timeline.
- English uses the Indian male voice `hi-IN-MadhurNeural`. Hindi uses the
  Indian female voice `hi-IN-SwaraNeural`.
- Hindi uses Devanagari board prose, apparatus labels, narration, captions,
  questions and player controls. The selector reads **हिंदी**. SI units remain
  standard. The internal `hinglish` key and filenames are retained for compatibility.
- Approved pronunciation substitutions live in optional `speech_text` fields.
  Swara receives तांबे while the visible captions and labels retain ताँबे.
  Speech caching checks both the actual spoken input and voice identifier.
- Dark label backplates are fitted to the translated lettering, keeping their
  margins compact even where Hindi occupies less width than the English label.
- Two genuine H5P Multiple Choice pauses follow the electron-flow explanation
  and the stronger-current comparison. Questions pause picture and sound together.
  Native Check, Retry and Continue controls remain in the compact panel footer.
- The page shows a language choice, the lesson, captions and a link to Case 2.
  Question-count slogans, the narration/caption disclaimer and the old footer
  slogans have been removed.

| Event | English | हिंदी |
| --- | ---: | ---: |
| Approach the atomic model | 13.500 s | 19.083 s |
| Switch ON / net electron flow | 46.417 s | 59.167 s |
| First H5P pause | 56.200 s | 71.867 s |
| Introduce the compass | 77.917 s | 100.917 s |
| Increased current comparison begins | 110.500 s | 135.000 s |
| Second H5P pause | 129.117 s | 154.950 s |
| Return to the summary | 136.083 s | 163.667 s |

## Teaching details

Small blue dots represent conduction electrons; copper-coloured spheres
represent copper ions vibrating near fixed positions. Colours and magnification
are teaching conventions. Random electron motion continues with the switch OFF;
closing the circuit establishes net drift and the wire's current-generated field.
Moving yellow arrows show conventional current from positive to negative, opposite to
electron drift. Green arrows follow the magnetic field, perpendicular to the
straight wire. The 60° view makes those circular guides easier to see in depth.

The circuit and compass stay in their approved positions. At the same location,
doubling current doubles the wire's field; the illustrated compass angle changes
from about 25° to 43°, rather than doubling. The compass also responds to Earth's
field. More drawn circles illustrate greater strength, not discrete physical
lines or a quantitative field-line count. The final summary remains on the board.

Bright, consistent label colours separate electrons (blue), conventional
current (yellow) and magnetic fields (green). English and Hindi board headings
use a clear title, observation and summary hierarchy. A compact Before/Now card
mirrors the physical instruments: 0.50 A / 25° becomes 1.00 A / 43°. A dashed
blue marker retains the initial needle direction; the comparison states that
the needle moved about 18° further. The card disappears for the summary.

## Files

All generated revision files are under
`output/parts/01_compass_current/bilingual/`:

- `case_one_english_720p.mp4`, `case_one_hinglish_720p.mp4`: finished movies.
- `case_one_english.blend`, `case_one_hinglish.blend`: editable, narrated,
  24-fps assemblies with packed sound and Hindi lettering textures.
- `case_one_source.blend`: revised 86-second source storyboard.
- `case_one_<language>_source.blend`: localized source for rendering.
- `audio_<language>/`: speech recordings, word boundaries, provenance, prepared
  WAV files, measured timing, and verification reports.
- `text/`: shaped text PNGs and a label manifest. Fonts are not redistributed.
- `case_one_frames/`: regenerable render caches, excluded from GitHub archives.

Importable packages: `output/share/case-one-english.h5p` and
`output/share/case-one-hinglish.h5p`. Readable questions are in
`student-lesson/content/case-one/`. The frozen original H5P package remains available.

## Build

Use included movies for ordinary web development. A fresh checkout can restore
the generated files with `python scripts/archive_project.py restore`.

Only regenerate speech when its script changes:

```sh
python scripts/generate_tutor_narration.py --script docs/case-one-english.json
python scripts/generate_tutor_narration.py --script docs/case-one-hinglish.json
python scripts/prepare_case_one_languages.py
python scripts/prepare_case_one_cues.py
blender --background --python-exit-code 1 --python scripts/build_case_one_revision.py
python scripts/prepare_case_one_text.py
```

New Hindi lettering uses Windows WPF shaping with the installed Nirmala UI font.
The preparation command runs its locally authored PowerShell command in an STA
process without changing the computer's execution policy. Existing shaped PNGs
and packed scenes work without that authoring dependency. Do not replace this
step with unshaped Blender text: Devanagari requires joined glyph shaping.

For each language, substitute `english` or `hinglish` below:

```sh
blender --background --python-exit-code 1 --python scripts/build_case_one_language_scene.py -- --language english
blender --background output/parts/01_compass_current/bilingual/case_one_english_source.blend --gpu-backend opengl --python-exit-code 1 --python scripts/render_case_one_languages.py -- --language english --stills
blender --background output/parts/01_compass_current/bilingual/case_one_english_source.blend --gpu-backend opengl --python-exit-code 1 --python scripts/render_case_one_languages.py -- --language english
python scripts/render_case_one_languages.py --language english --encode
blender --background --python-exit-code 1 --python scripts/verify_case_one_scenes.py -- --language english
```

Run one GPU render at a time. Movies are 1280×720 at 12 fps; editable scenes keep
24-fps animation. The renderer caches identical evaluated states, including
camera pose, visible labels, geometry and animated materials. Encoding maps the
86-second storyboard onto each spoken timeline, with at most 1/24-second source
sampling error. Speech is not accelerated. Source hashes invalidate stale caches.
This extends some visual holds and the electron-flow section to fit the fuller
explanation. Particle speeds remain illustrative rather than physical measurements.

For long exports on a modest graphics device, use the resumable batch runner
after building both localized source scenes:

```sh
python scripts/render_case_one_batches.py --blender /path/to/blender
```

It renders 192 source frames per Blender process, reuses complete cached PNGs,
checks for interrupted writes, retries failed batches and encodes both movies.
Use `--language english` or `--language hinglish` to resume only one version.
Do not rebuild source scenes merely to resume rendering: their file hashes
deliberately invalidate the old cache. A long single-process export stopped on
the authoring computer; the shorter-batch workflow preserves completed pictures.

```sh
python scripts/verify_case_one_languages.py
python student-lesson/scripts/build_case_one_h5p.py
node --test student-lesson/tests/case-one-language.test.cjs
```

Run the native H5P scoring tests once with `CASE_ONE_LANGUAGE=english` and once
with `CASE_ONE_LANGUAGE=hinglish`, using `node --test student-lesson/tests/h5p.test.cjs`.
In PowerShell set `$env:CASE_ONE_LANGUAGE` before each invocation, then remove it.
The normal website build also rebuilds both Case 1 packages and both Case 2 packages.
Publishing remains a separate step; see [PUBLISHING.md](PUBLISHING.md).

## Validation and preservation

The scene verifier compares visibility and world-space poses between source and
narrated edits, checks the camera angle, packed resources and switch metadata.
It also verifies that the travelling arrows advance along the conductor and
that the comparison card matches the actual ammeter and compass readings.
The media verifier decodes every frame, compares sampled pictures with their
rendered source when the local frame cache is available, checks every speech segment against the actual AAC soundtrack,
and verifies that both question pauses fall in silence. Speech word-boundary
coverage checks service output against the script; it is not a listening assessment.
Browser checks additionally cover language selection, native wrong-answer retry,
correct-answer Continue, captions and narrow-screen layout.
Scene identity checks accept either the original render source or its packed
archive copy, provided both checksums match the archive manifest.

Archive selected revision files with `archive_project.py prepare --paths`, pack
the public Blender copies with `pack_archive_scenes.py`, then finalize and verify
the archive. Keep exact frozen masters unchanged and preserve third-party licences.
