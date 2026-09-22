# Project checkpoint

## Current bilingual Case 1

[PART_01_BILINGUAL.md](PART_01_BILINGUAL.md) describes the revised first case:
English 144.417 seconds (polished Prabhat) and हिंदी 187.833 seconds (Swara), fully Hindi
labels, board prose and captions, travelling current arrows, before/now readings, a 60° close-up, richer particle narration and two native H5P pauses.
The root webpage starts with language selection. Its original 86-second version
below remains frozen. Case 2 retains its existing bilingual media and behaviour.

## Current bilingual Case 2

The English/हिंदी presentation revision has been rendered and verified. Read
[PART_02_POLISH.md](PART_02_POLISH.md) first for the current localized graphics,
Prabhat English and Swara Hindi voices, build commands and release status.
English lasts 239.167 seconds; हिंदी lasts 289 seconds. Both have four native
H5P questions. [PART_02_BILINGUAL.md](PART_02_BILINGUAL.md) documents the
preserved previous shared-picture release.

## Previous fixed-view revision (retained)

The previous narrated Case 2 is described in [PART_02_FIXED_VIEW.md](PART_02_FIXED_VIEW.md).
It uses one fixed camera, unchanged coil diameter for the 10/20-turn comparison,
yellow conventional-current arrows, turquoise field arrows and visible compass
measurements. H5P was deferred in that revision. The older checkpoint below is retained
as history; it is not the current camera or diameter specification.

- Previous movie: `output/parts/02_coil_reversal/coil_fixed_view_narrated_720p.mp4`.
- Editable scene: `output/parts/02_coil_reversal/coil_fixed_view_narrated.blend`.
- Duration: 231.5 seconds; 1280 x 720, 6-fps narrated review; scene remains 24 fps.
- The clips attach at exposed nail ends, with matching board headings.
- Portable packed copies are in `archive/generated/parts/02_coil_reversal/`.
- Case 1 is unchanged. The earlier fixed-view review is also preserved as v1.


Read [HANDOFF.md](HANDOFF.md) for detailed implementation and setup.
[CONTINUE.md](CONTINUE.md) contains the continuation prompt.
[archive/README.md](../archive/README.md) explains saved media and restoration.

## Case 1: frozen

- Movie: `output/parts/frozen_case_01/opening_and_compass_narrated_720p.mp4`.
- Editable scene: `output/parts/frozen_case_01/opening_and_compass_tutor.blend`.
- 86 seconds, 1280×720, 12 fps; 14 male Indian-English tutor narration sections.
- Apparatus pointers follow the spoken tour; microscopic flow lasts eight seconds.
- Two genuine H5P questions pause at 30.7 and 68.7 seconds. Compact panels retain
  reachable native Check, Try again and Continue controls.
- Original importable package: `output/share/electromagnetism.h5p`. The final
  summary remains on the lab board; the root page now uses the bilingual revision.
- Original frozen movie SHA-256:
  `cf9ac5f4a57678eada724182df952b438929ad5ffe38a2cc0a587e377206f0b8`.
- Original frozen scene SHA-256:
  `f177ebd25f4bd62ff1ee84da2ef3894e1af788de11180d003096695fc0a8b4fb`.

## Historical Case 2: approved silent visual draft

- Movie: `output/parts/02_coil_reversal/coil_reversal_preformed_coil_6fps.mp4`,
  identical to the latest `coil_reversal_draft_6fps.mp4` after encoding.
- Editable scene: `output/parts/02_coil_reversal/coil_reversal.blend`.
- Movie SHA-256:
  `e1aea7568c4925c5cf7035e94d31a3446c3d1b8ab5b4dc02bcaffab1f334fd89`.
- Editable-scene SHA-256:
  `23a0ed8e6c3513abbcb3111228b299ced957910f2532eafcc2c91896394193ae`.
- 136 seconds, 640×360, 6-fps silent review; editable animation is 24 fps.
- Begin with the ten-turn coil already formed and the switch OFF. White arrows
  show conventional current from positive to negative after switch-on.
- Every displayed wire-field location uses two concentric circles: paired guides
  surround the coil turns and all six representative circuit branches.
- Local circles crossfade to closed guides in several depth planes. The camera
  orbits about 40 degrees right, pauses, then returns to the front.
- Two equidistant smaller compasses show equal deflections: about 24 degrees for
  ten turns, 34 for twenty turns and 49 with the soft-iron core.
- Disconnect and turn the battery directly, without a board cutaway; poles,
  needles, current arrows and field arrows reverse.
- Switch OFF, change ten turns to twenty at the same coil length with smaller
  diameter and gaps. Switch ON at the same 0.50 A current magnitude.
- Move compasses farther outward and view nail insertion from the right. The
  illustrative core gain and 28 evenly spread guides make strengthening clear.
- Fixed regions inside a nail outline retain their positions while magnetic
  arrows align. Electron-flow/internal-field arrows explain this winding's
  directions. Stronger-field guide families are evenly spread.
- Six iron clips already rest below the nail. Switch ON to attract, then OFF to
  release them over 2.5 seconds. A wide view retains the whole circuit.
- Summary omits the separate "current creates a magnetic field" point.
- End with crane, dynamic microphone and MRI cutaways together, with all magnetic
  components highlighted continuously for 11 seconds, from 125 to 136.
- The previous approved movie and scene are preserved as
  `coil_reversal_before_preformed_coil_revision_6fps.mp4` and `.blend`.
- Case 2 narration/H5P have not been added. This is not the final high-frame-rate
  encode. Ask what to work on next before adding content.

## Scientific assumptions for the historical silent draft

The paired end compasses use an ideal symmetric-solenoid reading: the averaged
axial coil contribution plus one common Earth field at equal distances. Other
field calculations retain the complete circuit. Reversal need not rotate the
needles exactly 180 degrees. Internal
field runs S→N, external return runs N→S. Magnetic regions align with the internal
field, not directly with electron drift. Turn count and diameter both change in
this comparison. Core gain, drawn line counts and clip motion are illustrative;
low-remanence soft iron and regulated current are assumed. A dynamic microphone
uses induction with a moving coil and permanent magnet. See SCIENCE.md/PART_02.md.

## Restore and validate

```sh
python scripts/archive_project.py verify
python scripts/archive_project.py restore
python -m unittest discover -s tests -v
python scripts/freeze_case_one.py
python scripts/verify_compass_preview.py --coil --draft-fps 6
```

Restore copies missing files without overwriting different existing work.
Public packed scenes retain geometry/animation but have different packaging
checksums. Their frozen manifest matches those copies and records original hashes.
Original local masters and all render caches remain in private `backups/` snapshots.
Use the media environment, installed Blender and Node.js for documented checks.
No render, speech synthesis or voice-model download is needed merely to resume.

## Publishing and credentials

Backing up `main` does not publish GitHub Pages. The public site may still show
the earlier reference; inspect deployment before claiming it is current.
Keep passwords, tokens, local account paths and private snapshots off GitHub.
Authentication stays in Git Credential Manager. Preserve third-party licences.

Some bundled Windows Git installations store HTTPS helpers under `mingw64/bin`,
while `git --exec-path` points at `mingw64/libexec/git-core`. For a command session,
set `GIT_EXEC_PATH` to the installation's `mingw64/bin` when helpers are missing.

## Checkpoint validation

The checkpoint passed 22 Python tests and both native H5P tests. All 14 Case 1
narration sections passed the audio/video alignment check. Original frozen Case 1
hashes remain unchanged. Both portable Blender scenes reopened and passed their
scene checks. Case 2 decoded as 816 frames at 6 fps (136 seconds, silent). Its
render cache contains 460 distinct visual states. The public archive contains
357 checksum-verified files totaling 363,994,170 bytes. The full local snapshot
additionally preserves original render frames and logs.
