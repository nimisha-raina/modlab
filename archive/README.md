# Saved media and scene archive

Current Case 1 revision: `generated/parts/01_compass_current/bilingual/`, with
English/Hindi movies, independently timed packed scenes, male English and
female Hindi narration, Hindi
lettering and verification. Both importable H5P packages are under `generated/share/`.
The frozen 86-second first case and all earlier Case 2 checkpoints remain preserved.

`generated/` mirrors `output/` for finalized media, editable scenes, speech inputs,
H5P, historical revisions, validation metadata and review pictures.
`manifest.json` records stored SHA-256 values, original working-file hashes and
byte sizes. Movies and audio retain their bytes. Blender copies pack assets and
use relative resource paths. Portable text metadata omits local account paths.
Packing also clears the separate source paths stored inside packed image tiles;
the embedded image bytes remain unchanged.
Git attributes preserve archived bytes, including metadata line endings, so
checksum verification works on both Windows and Linux checkouts.

Verify with `python scripts/archive_project.py verify`. In a fresh checkout,
run `python scripts/archive_project.py restore` to copy missing files into
`output/`. Existing files remain intact, including exact original frozen masters.
The public frozen manifest matches the packed scene and records original hashes.
Re-archiving an unchanged restored copy preserves its original source checksum.

The reproducible frame-cache folders remain with all original working
output in a private snapshot created by `python scripts/archive_project.py snapshot`.
Its ZIP includes a per-file manifest and is checked by CRC and SHA-256.
Dependencies, model caches and credentials are excluded; pinned requirements and
the website lockfile preserve installation instructions.

```sh
python scripts/archive_project.py prepare
blender --background --python-exit-code 1 --python scripts/pack_archive_scenes.py
python scripts/archive_project.py finalize
python scripts/archive_project.py snapshot
```

Preserve `student-lesson/THIRD_PARTY_NOTICES.md`, licences in vendored H5P libraries
and `assets/tutor-narration/CLIENT-LICENSE`. Application-picture provenance and
scientific sources are in `assets/lesson-applications/README.md`.
Archiving does not deploy GitHub Pages.

To add selected Case 2 outputs while preserving older archived releases, use
`python scripts/archive_project.py prepare --paths parts/02_coil_reversal/audio_fixed parts/02_coil_reversal/coil_fixed_view_source.blend parts/02_coil_reversal/coil_fixed_view_narrated.blend parts/02_coil_reversal/coil_fixed_view_narrated_720p.mp4`,
then run the packing and finalize steps above. Only changed selected Blender
scenes are repacked. `fixed_view_frames/` is a reproducible cache and is excluded
from the public archive.

For the current English/Hinglish lesson, select
`parts/02_coil_reversal/bilingual share/coil-english.h5p share/coil-hinglish.h5p`
instead. Its `bilingual_frames/` cache is also excluded. The source storyboard,
visual master, both packed language scenes, soundtracks, videos, question timing
and validation reports are included. See `docs/PART_02_BILINGUAL.md`.
