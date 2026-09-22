# Maintainer handoff

## Current bilingual Case 1

Read [PART_01_BILINGUAL.md](PART_01_BILINGUAL.md) first for the revised first case.
It offers English (144.417 s, polished Prabhat male voice) and हिंदी (187.833 s,
Swara female voice), fully Hindi board text and labels, brighter lettering,
travelling yellow current arrows, a gradual 60° rightward close-up, and two
compact native H5P questions. The Before/Now card mirrors 0.50 A / 25° and
1.00 A / 43°; a dashed marker retains the initial compass direction.
Hindi speech uses the approved तांबे pronunciation input while visible text
retains ताँबे. Optional `speech_text` is included in voice cache validation. The webpage has been simplified and starts with a
language choice. The frozen 86-second original and Case 2 remain preserved.
Prabhat's English delivery uses sentence-level generation, loudness matching,
clean edge fades and one final encode. This avoids volume dips and noisy joins.
Use the verification reports beside the generated files to check completion;
the older first-case workflow below describes the preserved reference.

Both complete movies and both native H5P question paths have passed browser
playback, wrong-answer retry, correct-answer Continue and phone-width checks.
The final validation includes 31 Python tests and 14 H5P tests across five
lesson configurations. Verification reports are preserved with the bilingual
media archive; final playback ends on the localized summary board.

## Current bilingual Case 2

Read [PART_02_BILINGUAL.md](PART_02_BILINGUAL.md) for the current English/Hinglish
lesson, contact-synchronized fields, temporary 60-degree nail view, magnetic-region
diagram and four native H5P questions. English lasts 255 seconds and Hinglish 303.83 seconds.
The fixed-view checkpoint below remains available as the previous revision.

## Resume checkpoint and preservation

Read [RESUME.md](RESUME.md) for the approved checkpoint and restoration steps.
[CONTINUE.md](CONTINUE.md) supplies a continuation prompt.
The public media archive is documented in [archive/README.md](../archive/README.md).
Private local snapshots under `backups/` preserve original scenes, all working
output and render caches. Public scene copies are packed and portable; original
frozen masters remain unchanged locally.

The previous Case 2 revision used one fixed camera with the board and whole
circuit visible. It compares 10 turns, 20 turns at unchanged length and diameter,
and a soft-iron core at the same current. Yellow arrows follow conventional
current; turquoise guides show magnetic field direction. Both fixed compasses
have visible arcs and degree readings. Measured Indian male narration extends
the lesson to 231.5 seconds, including an 11-second applications display.
See [PART_02_FIXED_VIEW.md](PART_02_FIXED_VIEW.md) for that revision’s files, build,
validation and then-deferred H5P plan. Case 1 and older Case 2 media remain preserved.
The visible clip attachment points are at the exposed nail ends, beyond the
winding, with board headings for switch OFF, attraction and release. The complete
movie is a 720p 6-fps review; the packed editable scene retains 24-fps animation.

## Preserved 86-second first-case reference

The approved first case is now narrated and integrated with genuine H5P:

- 86 seconds, 1280×720, 12 fps, 1,032 frames. The original 76-second review is
  retimed for the spoken apparatus tour; five new yellow pointer stills identify
  components as their names are spoken. The eight-second electron flow is unchanged.
- Fourteen male Indian-English tutor sections, Microsoft Edge voice
  `en-IN-PrabhatNeural`, normalized speech embedded as AAC. The earlier AI4Bharat
  service was unavailable for revised speech. One voice is used throughout.
  No speech acceleration or voice-model
  download was required. `docs/first-case-narration.json` is the current script.
- Two native Multiple Choice pauses at 30.7 and 68.7 seconds, following complete
  explanations of current creating a field and increased current strengthening it.
- Upper-right question panel, at most 300×290 pixels on desktop; content scrolls
  separately from the native Check, Try again and Continue buttons. Correct
  answers unlock Continue; incorrect answers require retry.
- Captions, question count and runtime metadata match this first case. The final
  summary remains on the laboratory board; no automatic H5P score/submission
  screen covers it. Stopping net electron flow removes
  the wire's field; this is explained verbally, while the approved first-case
  picture ends with current flowing. Random electron motion and Earth's field remain.
- Movie: `output/parts/01_compass_current/opening_and_compass_narrated_720p.mp4`.
  Importable package: `output/share/electromagnetism.h5p`. Local preview:
  `python scripts/serve_lesson.py`, then `http://127.0.0.1:8765/`.

The website entry points are `/` for the bilingual first-case revision and `/coils/`
for the bilingual coil lesson. GitHub Pages uses `https://nimisha-raina.github.io/modlab/`.
Updates require the publishing step in [PUBLISHING.md](PUBLISHING.md); pushing
source alone does not deploy the website. The publisher uses the active Python
environment and Node.js directly so it also runs on Windows. The Case 1 Blender
draft has not been repacked with its final soundtrack; audio is mixed into its
movie. See the fixed-timeline workflow in [DEVELOPMENT.md](DEVELOPMENT.md).

The tutor scene is `output/parts/01_compass_current/opening_and_compass_tutor.blend`.
It keeps a ten-second apparatus overview, an eight-second spoken zoom, five
seconds explaining ion vibration and random electron motion, and a shorter
seven-second overview transition. Switch closure is at second 23, compass
placement starts at 48 and the final summary starts at 72. The closing narration
opens with "To summarize what we have learned"; the stationary board hold extends
from second 74 to 86 so the recap fits at natural speaking speed. Experiment
events and both quiz pauses retain their timing. Word-boundary metadata
is aligned to prepared audio for the apparatus cues. Audio preparation preserves
150 ms of sentence-tail silence and uses 20 ms/100 ms raised-cosine fades to
remove abrupt joins. Working speech is in `audio_tutor/`; included recordings,
timing and provenance are in `assets/tutor-narration/`. The earlier 76-second
Thoma recordings remain in `assets/first-case-narration/` as reference material.

## Original reference assets

The bundled `assets/scene/` and `assets/narration/` are the original reference
release. Their timing and verification reports apply to that release only.

- Procedural school laboratory, copper circuit, battery and animated knife switch.
- Magnified copper teaching model with vibrating ions and mobile electrons.
- Negative-to-positive electron drift; conventional current in the opposite
  direction. Ion spacing remains fixed in the laboratory reference frame.
- Three concentric magnetic field guides, introduced after current begins.
- Continuous camera zoom and pullback, with one physical electron marker radius.
- Ten male Indian-English narration sections, English captions and a completed
  1280×720 H.264/AAC video: 1,970 frames at 24 fps, approximately 82.08 seconds.
- H5P Interactive Video 1.28.37 and Multiple Choice 1.16.27, with questions at
  approximately 39.158, 48.242 and 81.783 seconds. Pauses follow complete spoken
  explanations. Incorrect answers allow retry; correct answers expose Continue.
- A portable Blender scene with packed audio, source recordings and verification
  reports. Voice-model access is optional unless the spoken text changes.

## Reviewed base Blender draft

The following base-scene sections describe `opening_and_compass.blend` and its
76-second review. The tutor revision retimes that source as described above;
the microscopic flow, compass physics and apparatus geometry are retained.

- Ions and electrons appear together after the close-up is reached, and disappear
  together when the cutaway begins closing. No electron dots appear in overview.
- The large lesson title, baked caption panel and decorative footer are removed.
  Remaining apparatus backplates fit their text with a small margin. Captions
  remain available as exported sidecar text for later accessible presentation.
- Close-up field guides start appearing with switch closure. The gentle camera
  turn also starts earlier, making the circles readable during the first spoken
  field explanation. Camera poses and the continuous zoom/pullback are retained.
- During pullback, the original three circles stay visible alongside local guides:
  two on each long side and one on each short side. Arrows follow conventional
  current's right-hand rule. These are local contributions, not a computed map
  of the entire circuit's resultant field.
- Build with `run.py`, then run `scripts/verify_scene.py`. Review the generated
  `output/electromagnetism_intro.blend` before replacing any reference media.

The packed narration is a temporary reference track while the Blender teaching
sequence is developed. Sections 6 and 8 need revised wording: the field is now
already visible before section 6, and there are no overview electron dots in
section 8. Finalize the extended sequence, revise affected speech and timing,
then render and rebuild the H5P interactions. Do not treat the old reference
video or its verification report as validation of the revised animation.
The revised opening also requires remapping spoken sections and captions to
the new 11-second close-up arrival, 14-second closure and 22-second pullback.

## Compass and current extension

Part 1 is an independent 34-second silent Blender section with physical board
headings, compass placement and a series ammeter reading 0.50 A then 1.00 A. The
switch stays closed throughout this continuation; it restores 0.50 A at the end
for the next section. The needle follows the combined wire and Earth
fields; doubling current increases its deflection without artificially doubling
the angle. A degree reading and marked arc make the 25°/43° comparison visible.
There are six guide locations; three baseline circles stay at the magnified
location and one at each other location (eight drawn circles, sixteen at 2I).

See [PART_01.md](PART_01.md) for the timeline, source map, build commands and
review outputs. Build with `scripts/build_current_demo.py` and validate with
`scripts/verify_current_demo.py`. This section reuses the laboratory and circuit
modules. Its connected first-case movie now has narration and H5P integration. The separate
coil/reversal case is described below. Iron core, clips and applications are included in the extended Case 2 visual sequence.

`scripts/build_compass_sequence.py` creates a connected silent visual assembly
in `output/parts/01_compass_current/opening_and_compass.blend`. The opening retains
its zoom, ions/electrons, switching and field reveal, and gains the same series
ammeter. Its source timeline ends at 42 seconds with current flowing, then the
compass is placed immediately. The assembly lasts 76 seconds, including the
summary-board ending. Validate with
`scripts/verify_compass_sequence.py` and render with
`scripts/render_current_demo.py -- --combined`. The current first-case narration
replaces the former switch-off finale; do not reuse the old reference audio unchanged.

## First-case revisions and separate coil case

The connected opening shows the physical experiment board and entire circuit
together from a farther camera for three seconds, then approaches copper over
eight seconds. Ions/electrons appear at second 11. The switch closes at second
14; visible electron flow lasts eight seconds, with movement unchanged.
Particles disappear as pullback begins at second 22.
The opaque copper surface returns by second 23; the half-shell and cutaway rims
are hidden then. The ammeter covers a series gap in the left-side copper conductor. Its short
connections and terminals sit behind the housing, concealed from the front view. The round
black analogue meter is mounted along this branch, with a white
centre-zero −1 to +1 A scale, red needle and compact on-face numerical reading.
The model uses geometry rather than a copied reference photograph. The pointer
follows zero, 0.50 A, 1.00 A and −0.50 A in the corresponding cases.

Case 1 is frozen: `scripts/freeze_case_one.py` preserves its movie, editable tutor
scene and narration script under `output/parts/frozen_case_01/`, with SHA-256
checksums in `manifest.json`. The script refuses to overwrite a different frozen
snapshot. Case 2 builders do not regenerate Case 1 or change its website media.

### Historical Case 2 review

The following describes the preserved earlier checkpoint; use
[PART_02_FIXED_VIEW.md](PART_02_FIXED_VIEW.md) for the current implementation.

Part 2 was a separate 136-second silent visual review, starting with a completed
ten-turn coil and the switch OFF. White conventional-current arrows follow every
visible branch and the winding. Two concentric local-field circles appear at each
shown location. The local fields become a closed solenoid pattern while the camera
orbits about 40 degrees right and returns to the front. Smaller equidistant
compasses have equal live deflection readings. Direct battery reversal changes the
poles, current arrows, field arrows and needles without a board cutaway.

The extended sequence changes ten turns to twenty at the same axial length,
with both smaller diameter and smaller gaps, then inserts a soft-iron nail,
explains magnetic-region alignment on the board, attracts and releases six clips,
and ends with the requested summary followed by highlighted application pictures.
Every apparatus change takes place with the switch OFF. Current magnitude remains
0.50 A during the coil/core comparisons, assuming the regulated supply.
The core-strength gain, field-guide density and clip trajectories are illustrative.
The microphone picture is labelled moving coil + permanent magnet; it is an
application of electromagnetism, not the same lifting-electromagnet mechanism.

Build with `scripts/build_coil_demo.py`, validate with `scripts/verify_coil_demo.py`,
and render efficiently with `scripts/render_coil_review.py`, followed by its
`--encode` mode in the media environment. See [PART_02.md](PART_02.md) for the
complete timeline, output files, physics assumptions and cache invalidation.
Case 2 narration/H5P are not part of this silent visual review. Case 1 media,
narration and website are unchanged.
The latest revision labels magnetic field inside and outside the coil, distributes
stronger-field guides across several depth planes, moves the compasses farther
outward, and views nail insertion from the right. The region model
has a fixed nail outline plus electron-flow and internal-field arrows. The clips
begin below the nail instead of sliding in; release lasts 2.5 seconds. Final board
framing reduces the upper wall margin. All three
application pictures and component highlights remain visible together for the
whole 11-second applications stage (125–136 seconds). The duration follows the
sequence rather than an imposed finish deadline. All 22 Python tests, saved-scene
checks and full media decoding pass (816 frames, 136 seconds, 640×360 at 6 fps,
silent). The efficient renderer produced 460 distinct visual states. The editable
source retains 24 fps. The approved review copy has SHA-256
`e1aea7568c4925c5cf7035e94d31a3446c3d1b8ab5b4dc02bcaffab1f334fd89`.
See PART_02.md for validation.

Visible microscopic drift is faster (2.6 display units per second) and the
drawn random displacement is reduced while current flows. This is a readability
convention, not a claim that real thermal motion decreases. Electron radii and
ion lattice positions are unchanged. Review particle motion at 12 or 24 fps;
low frame rates can alias the repeated markers. Focused interval exports and
matching media checks are documented in [PART_01.md](PART_01.md).

The current apparatus review uses a deeper black panel-meter housing, separated
white scale and concealed rear terminals. Build the standalone compass scene
and run `scripts/render_apparatus_review.py` on it for a full-circuit still and
meter detail. The reviewed base first case lasts 76 seconds: the established demonstration
plus a two-second return to the board and eight-second summary hold. The summary
replaces the prior heading as this return begins at 66 seconds. Board headings
omit case numbers. The component label reads "Resistor". Explicit dial triangles,
separated face/ink/pointer layers and a larger camera near plane prevent the
black bezel from competing with the white dial's depth. Four points
cover electron drift, current and magnetic field, compass detection and stronger
field with more current. The enlarged dial reading is checked at 720p in the
fixed comparison view. `scripts/render_complete_preview.py` renders the full
12-fps 720p visual review; run its `--encode` stage in the media environment and
validate with `scripts/verify_compass_preview.py --combined --review-720p`.
The revised complete review movie passed this media check: 912 frames, 76.0 seconds,
1280×720, 12 fps and regular timestamps. This visual review is silent; the
current narrated movie copies its video stream and adds the final soundtrack.
The camera, dial, persistent-guide and deflection-indicator
revision is included in this movie. An encoded-image check of the dial interior
in 483 visible frames detected no large black patches; keyframes were also
inspected. All 17 Python tests, the main scene check and connected-scene checks
passed. The render report records 603 rendered frames and 309 reused stills.
Coil scene caches require rebuilding to receive this apparatus revision.

Previously generated preview movies are caches of their corresponding build.
Rebuilding a `.blend` does not update a movie; render the revised source before
using a previous preview as evidence of these changes.

## Editing map

| Change | Start here | Follow-up |
| --- | --- | --- |
| Questions and feedback | `student-lesson/content/questions.json` | Build and test H5P |
| Question panel | `student-lesson/dist/h5p-theme.css`, `question-layout.js` | Test all dialogs on desktop and phone |
| Page appearance | `student-lesson/dist/index.html`, `styles.css` | Browser preview |
| First-case speech and captions | `docs/first-case-narration.json` | Generate affected clips, prepare the fixed timeline and rebuild H5P |
| Original reference speech | `docs/narration.json` | Use the original retiming and rendering workflow |
| Colours or marker sizes | `src/electromagnetism/config.py` | Build and inspect rendered frames |
| Camera movement | `src/electromagnetism/camera_path.py` | Verify scene and review transitions |
| Laboratory, circuit or particles | Matching module in `src/electromagnetism/` | Build, verify and inspect frames |
| Switching or duration | `config.py`, motion keys and narration source intervals | Keep storyboard, captions and timing consistent |

H5P content under `student-lesson/dist/h5p/` is generated. Edit the readable JSON
inputs, not that package or official vendor libraries. The builder and progress
labels derive the question count from these inputs. The current first-case
checks require exactly two questions, each after its complete spoken explanation.

## First maintainer check

1. Build and preview the website from the included video using the root README.
2. Watch the lesson, answer incorrectly, retry and continue through all questions.
3. Run `python3 scripts/restore_assets.py`, then rebuild the Blender scene.
4. Run the Python, Blender and H5P checks in the development guide.
5. Choose the deployment location and original-work licence with the repository
   owner before distributing modified versions.

On Windows, follow [Windows preview and checks](DEVELOPMENT.md#windows-preview-and-checks).
`pnpm build` now selects `PYTHON`, the project media environment, or an available
system Python 3 interpreter. Blender 5.2.0 LTS has also passed the scene build and
verification on Windows. Reuse the included video and narration for initial
review; a full render or voice generation is needed only for relevant content
changes. The included transcript report can be reused for unchanged recordings;
the video alignment check runs without downloading a recognition or voice model.

## Scope and known limits

This is a teaching illustration, not a microscopic physics simulation. Particle
scales, speeds and field-guide sizes are exaggerated. A zoom changes magnification,
not the reference frame. Read the science notes before extending to relativity.

The website stores no student identity or persistent scores. There is no backend,
teacher dashboard or gradebook integration. Those require additional design work.

Automated checks cover animation invariants, soundtrack timing and native H5P
behaviour. Rendering quality, pronunciation and small-screen layout need review
after changes. Saved reference reports describe the included media and should be
regenerated when the media changes.

The original bundled transcript report predates recording hashes for its first eight
entries. It is reference evidence, not a fresh speech-recognition check of
those clips. The video verifier separately compares all ten prepared WAV clips
with the decoded original soundtrack. For the earlier 76-second first case,
`assets/first-case-narration/` includes thirteen recordings, measured timing,
recording hashes, recognition results and decoded-video alignment checks.
Recognition may omit repeated words or render spoken numbers as digits;
it does not certify pronunciation. All thirteen prepared clips match the final
decoded soundtrack at their intended start times. The current tutor revision has
fourteen recordings and fresh transcript/alignment reports in
`assets/tutor-narration/`; its fades produce zero-valued PCM boundaries without
clipping. Both current question pauses fall in silence after their explanations.

## Deployment and ownership

For GitHub Pages, see [PUBLISHING.md](PUBLISHING.md). The `gh-pages` branch holds
the deployed website; `main` retains the editable source. Publish updates with
`python3 scripts/publish_github_pages.py` after committing source changes.

Build `student-lesson/` and publish its entire `dist/` directory to a static HTTPS
host with correct content types and MP4 byte-range support. No server secrets are
needed. The repository includes no deployment account configuration.

After checking the final public address on a phone, generate its QR code:

```sh
python3 -m pip install -r requirements-qr.txt
python3 scripts/create_lesson_qr.py https://your-public-lesson.example
```

Files are written to `output/share/`. Changing the address requires a new printed
QR code unless a stable redirect is retained.
