# Maintainer handoff

## Included lesson

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

## Editing map

| Change | Start here | Follow-up |
| --- | --- | --- |
| Questions and feedback | `student-lesson/content/questions.json` | Build and test H5P |
| Question panel | `student-lesson/dist/h5p-theme.css`, `question-layout.js` | Test all dialogs on desktop and phone |
| Page appearance | `student-lesson/dist/index.html`, `styles.css` | Browser preview |
| Spoken explanation | `docs/narration.json` | Regenerate affected audio, prepare timing, rebuild and render |
| Caption text | `src/electromagnetism/lesson_text.py` | Rebuild, render, synchronize and rebuild H5P |
| Colours or marker sizes | `src/electromagnetism/config.py` | Build and inspect rendered frames |
| Camera movement | `src/electromagnetism/camera_path.py` | Verify scene and review transitions |
| Laboratory, circuit or particles | Matching module in `src/electromagnetism/` | Build, verify and inspect frames |
| Switching or duration | `config.py`, motion keys and narration source intervals | Keep storyboard, captions and timing consistent |

H5P content under `student-lesson/dist/h5p/` is generated. Edit the readable JSON
inputs, not that package or official vendor libraries. The builder currently
expects three questions; adding questions requires updating its count checks
and the page's labels.

## First maintainer check

1. Build and preview the website from the included video using the root README.
2. Watch the lesson, answer incorrectly, retry and continue through all questions.
3. Run `python3 scripts/restore_assets.py`, then rebuild the Blender scene.
4. Run the Python, Blender and H5P checks in the development guide.
5. Choose the deployment location and original-work licence with the repository
   owner before distributing modified versions.

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

## Deployment and ownership

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
