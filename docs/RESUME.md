# Approved project checkpoint

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
- Importable package: `output/share/electromagnetism.h5p`. The local webpage
  uses this first case. The final summary remains on the lab board.
- Original frozen movie SHA-256:
  `cf9ac5f4a57678eada724182df952b438929ad5ffe38a2cc0a587e377206f0b8`.
- Original frozen scene SHA-256:
  `f177ebd25f4bd62ff1ee84da2ef3894e1af788de11180d003096695fc0a8b4fb`.

## Case 2: approved visual draft

- Movie: `output/parts/02_coil_reversal/coil_reversal_field_revision_6fps.mp4`,
  identical to `coil_reversal_draft_6fps.mp4`.
- Editable scene: `output/parts/02_coil_reversal/coil_reversal.blend`.
- 136 seconds, 640×360, 6-fps silent review; editable animation is 24 fps.
- Begin with straight copper and switch OFF. Approach the winding area; ten
  turns form in five seconds at about half-screen width.
- Switch ON, show upper/lower local contributions, then a closed magnetic field
  resembling a bar magnet's. Show N/S, smaller compasses and deflection readings.
- Disconnect, turn the battery, reconnect; poles, needles and larger gold/blue
  direction arrows reverse. Inside and outside magnetic fields are labelled.
- Switch OFF, change ten turns to twenty at the same coil length with smaller
  diameter and gaps. Switch ON at the same 0.50 A current magnitude.
- Move compasses outward; view nail insertion from the right with battery and
  switch state in frame. Switch ON for stronger field and compass response.
- Fixed regions inside a nail outline retain their positions while magnetic
  arrows align. Electron-flow/internal-field arrows explain this winding's
  directions. Stronger-field guide families are evenly spread.
- Switch OFF, introduce six iron clips, switch ON to attract, then OFF to release.
  The fall lasts 1.2 seconds. The final board sits higher in the picture.
- Summary omits the separate "current creates a magnetic field" point.
- End with crane, dynamic microphone and MRI cutaways together, with all magnetic
  components highlighted continuously for 11 seconds, from 125 to 136.
- Movie SHA-256:
  `fc4357a5ea3e7bd17819d4d7d6ffb0db5f64643a48bfc92289f8459051f89ca1`.
- Case 2 narration/H5P have not been added. This is not the final high-frame-rate
  encode. Ask what to work on next before adding content.

## Scientific assumptions

Compasses follow the complete circuit plus one common Earth field at their actual
animated positions. Reversal need not rotate them exactly 180 degrees. Internal
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
scene checks. Case 2 decoded as 816 frames at 6 fps (136 seconds, silent). The
public archive contains 342 checksum-verified files, totaling 344,506,306 bytes.
The full local snapshot additionally preserves original render frames and logs.
