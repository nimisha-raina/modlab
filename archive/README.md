# Saved media and scene archive

`generated/` mirrors `output/` for finalized media, editable scenes, speech inputs,
H5P, historical revisions, validation metadata and review pictures.
`manifest.json` records stored SHA-256 values, original working-file hashes and
byte sizes. Movies and audio retain their bytes. Blender copies pack assets and
use relative resource paths. Portable text metadata omits local account paths.

Verify with `python scripts/archive_project.py verify`. In a fresh checkout,
run `python scripts/archive_project.py restore` to copy missing files into
`output/`. Existing files remain intact, including exact original frozen masters.
The public frozen manifest matches the packed scene and records original hashes.

The three reproducible frame-cache folders remain with all original working
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
