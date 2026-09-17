# Class 8 interactive electromagnetism lesson

This webpage runs **genuine H5P Interactive Video 1.28.37** with H5P Multiple Choice
1.16.27. H5P supplies playback, timed questions, answer checking, hints, retries,
and continuation. The open-source `h5p-standalone` player supplies H5P's runtime
without requiring a school account or a separate learning management system.

## How the questions work

After narration sections 5 and 12, at 30.7 and 68.7 seconds, H5P pauses the video and automatically opens its
native question dialog. A correct answer unlocks **Continue video**. The scene
stays behind the dialog. The local theme gives the box a compact size and a
180 ms fade and movement transition; reduced-motion preferences disable it.
The original H5P buttons sit in a separate, non-scrolling footer. Question text,
choices and feedback scroll within the panel when necessary. This keeps Check,
Try again and Continue reachable without resizing the page. H5P retains all
answer checking and button handlers.

The page does not collect names, submit results, or persist scores. Progress lives
in the open page and resets on reload. The lesson provides the realistic
laboratory video with English captions and male Indian-English narration.
All fourteen voice sections are embedded in the 86-second first-case video.
Timed yellow pointers identify each apparatus component as it is named.
The camera approaches copper during the spoken atomic-level introduction.
Questions follow complete sentences, so pausing, seeking and resuming keep
the animation and narration synchronized.
The current-strength question holds wire and distance fixed.
The lesson finishes on the laboratory summary board, with replay available below
the video. No automatic score/submission screen covers the ending.

## Files to edit

- `content/questions.json`: narration section numbers, choices, correct answers, and feedback.
- `content/narration-timing.json`: measured narration timing exported from Blender preparation.
- `content/captions.json`: captions with their final video times.
- `scripts/build_h5p.py`: creates native H5P content and the downloadable package.
- `dist/index.html` and `dist/styles.css`: the page surrounding the player.
- `dist/h5p-theme.css`: styling inside the H5P video frame.
- `dist/question-layout.js`: places H5P's native buttons in the stable footer.
- `dist/lesson.js`: connects native H5P progress to captions and replay.
- `dist/captions.js`: generated captions and video metadata.
- `dist/assets/`: the laboratory video and its poster.
- `vendor/h5p-libraries/`: unchanged official H5P runtime libraries.
- `vendor/h5p-libraries.lock.json`: exact upstream versions and source-bundle hash.
- `tests/h5p.test.cjs`: checks dependencies and genuine H5P scoring and retries.

## Build and preview

The site uses Python 3 for content generation and Node.js/pnpm for its pinned
player dependency and tests. From this folder:

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm test
```

The build copies the runtime into `dist/vendor/` and writes the H5P lesson under
`dist/h5p/electromagnetism/`. It also writes
`../output/share/electromagnetism.h5p`. A school H5P platform can import this
package with the matching content libraries installed. Official editor libraries
can be installed through that platform's H5P content hub when needed.

From the parent Blender project, run `python3 scripts/serve_lesson.py`, then open
`http://127.0.0.1:8765/`. This preview server supports video seeking. Stop it with
Ctrl+C. The deployed player serves all its files from the same site; it does not
rely on a third-party video host or a runtime CDN.

For the current first case, run `scripts/prepare_first_case_narration.py` from
the parent project using its media environment, then rebuild this site. It
mixes measured speech into the approved movie without changing video or speech
speed and copies matching timing, captions and a fresh poster. Its source is
`docs/first-case-narration.json`; cached clips live under
`output/parts/01_compass_current/audio_tutor/`. Included authoring recordings are
under `assets/tutor-narration/`. The older `sync_student_lesson.py`
belongs to the original reference render workflow.
Do not hand-edit the generated `content.json` or vendor libraries.

## Publishing

GitHub Pages serves the built lesson from the `gh-pages` branch. Follow
[the publishing guide](../docs/PUBLISHING.md) for the owner's one-time setting
and the update command, `python3 scripts/publish_github_pages.py`.

Publish the complete built `dist/` directory to a static HTTPS host with correct
content types and MP4 byte-range support. Relative asset URLs support deployment
below a repository subpath as well as at a domain root. The repository includes
no account-specific hosting configuration. Check playback and both questions
at the final address before distributing the link or QR code.

The root `docs/HANDOFF.md` describes QR generation and maintainer responsibilities.
See `THIRD_PARTY_NOTICES.md` for provenance and licensing.
