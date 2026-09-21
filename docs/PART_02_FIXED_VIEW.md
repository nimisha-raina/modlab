# Case 2: fixed-view narrated lesson

This previous review is retained. The current workflow is in
[PART_02_BILINGUAL.md](PART_02_BILINGUAL.md).

This revision keeps the physical laboratory board and complete circuit in one
slightly elevated front view. The camera never moves. The earlier 136-second
silent orbit review and frozen Case 1 are retained separately.

## Teaching sequence

1. Ten-turn coil already connected; switch OFF. Identify the apparatus.
2. Close the switch. Yellow arrows follow conventional current along the copper
   wire, from positive to negative, opposite to electron drift.
3. Two concentric local field circles surround each illustrated wire location.
   Each circle is perpendicular to that wire's tangent. The local contributions
   fade into the complete solenoid field; lines do not physically merge.
4. Turquoise arrows show the field returning from N to S outside and S to N
   inside. Fixed, symmetric compasses have red north tips, reference arcs and
   integer-degree readings.
5. Open the switch, reverse the cell connections and close the switch. Current,
   field direction, poles and compass deflection reverse.
6. Open the switch; compare 10 turns with 20 turns at the **same length and
   diameter**. Smaller gaps accommodate more wire. Switch on at the same 0.50 A
   current magnitude, showing greater compass deflection.
7. Open the switch, insert soft iron, then switch on. A third, stronger field
   drawing and greater compass deflection show the core's effect.
8. The board shows fixed magnetic regions inside a nail outline. Their magnetic
   directions align with the coil's field; the region boundaries do not move.
9. Paper clips rest below the two exposed ends of the nail, beyond the winding
   so their attachment remains visible. Closing the switch lifts them vertically;
   opening it releases them in a slowed teaching demonstration. The board labels
   the OFF, attraction and release stages as they happen.
10. Summarize poles, reversal, more turns, soft iron and controlled attraction.
11. Show crane, dynamic microphone and MRI pictures together for **11 seconds**,
    with their magnetic components highlighted throughout.

The 10-turn, 20-turn and iron-core drawings contain 10, 20 and 30 closed traces,
respectively, evenly distributed across five orientations around the axis.
The drawing density is qualitative. It is not a numerical measurement of flux
or an assertion that an iron core always increases strength by a fixed factor.

## Files and timing

- Script: `docs/coil-narration.json`.
- Working speech, provenance and measured timings:
  `output/parts/02_coil_reversal/audio_fixed/`.
- Editable storyboard: `coil_fixed_view_source.blend`, 136 source seconds.
- Editable narrated scene: `coil_fixed_view_narrated.blend`, 24 fps, with packed
  narration. Both scene files are under `output/parts/02_coil_reversal/`.
- Movie: `coil_fixed_view_narrated_720p.mp4`, 1280 x 720, 6 fps for review; the editable scene remains 24 fps.
- Measured narrated duration: **231.5 seconds**. Speech is not accelerated.
  Source seconds in the storyboard map piecewise to measured narration windows.
  The actual mapping is in `audio_fixed/narration-timing.json`.

The voice is the male Indian-English tutor `en-IN-PrabhatNeural`. Existing speech
clips are reused by content hash. Only changes to spoken content require a
speech-service request; no local voice-model download is needed. Preparation
normalizes loudness, preserves natural sentence endings, and adds short cosine
fades to reduce abrupt audio joins. The final applications line fits within the
agreed 11-second display at natural speed.

## Rebuild after relevant changes

Use the existing media Python environment and Blender:

```sh
python scripts/generate_tutor_narration.py --script docs/coil-narration.json
python scripts/prepare_coil_narration.py
python -m unittest discover -s tests
blender --background --python-exit-code 1 --python scripts/build_coil_fixed_view.py
blender --background output/parts/02_coil_reversal/coil_fixed_view_narrated.blend --python-exit-code 1 --python scripts/verify_coil_fixed_view.py
blender --background output/parts/02_coil_reversal/coil_fixed_view_narrated.blend --python-exit-code 1 --python scripts/render_coil_fixed_view.py -- --stills 0 8 24 61 70 88 108 119 130
blender --background output/parts/02_coil_reversal/coil_fixed_view_narrated.blend --python-exit-code 1 --python scripts/render_coil_fixed_view.py
python scripts/render_coil_fixed_view.py --encode
python scripts/verify_narrated_video.py --timing output/parts/02_coil_reversal/audio_fixed/video-timing.json --video output/parts/02_coil_reversal/coil_fixed_view_narrated_720p.mp4 --no-questions
```

The renderer defaults to a 6-fps review on modest graphics hardware; add
`-- --fps 12` to render a higher-frame-rate export. The renderer reuses identical scene states from `fixed_view_frames/`. The
fingerprint includes the saved source checksum, visible transforms, winding
shape keys, field opacity and compass-arc length. Changing the saved scene
invalidates older cached renders. Keep source and narrated scenes separate to
avoid applying the speech timing twice. Retiming includes object, curve,
shape-key and material-node actions exactly once.

The earlier fixed-view review is preserved as `coil_fixed_view_review_v1.blend`
and `coil_fixed_view_review_v1_720p.mp4`. The clip-visibility revision can use
`--reuse-prefix` with its saved render map: every frame before source second 99
must match the earlier scene-state fingerprint before its image is reused.
The revised ending is rendered normally. This option is specific to that
revision, not a general way to reuse frames after arbitrary scene changes.

## Validation of the saved review

The clip-visibility revision passes 26 Python tests, both existing H5P checks,
and the Blender scene verifier. All 1,389 movie frames decode with increasing
timestamps. All 18 narration sections match the prepared recordings at their
scheduled times. The render report and scene verifier identify the same input
scene checksum. Reports are saved alongside the movie and in `audio_fixed/`.

Movie SHA-256:
`264c3c618578116bec51405679bf1f8bc024c9adba1383ffa56c47011d99f673`.

## Future H5P authoring

H5P is deliberately deferred for this chapter. Suggested short prediction
questions, placed before the relevant switch-on or reversal demonstration:

- At the same current and coil size, what happens when 10 turns become 20?
- What happens when soft iron is inserted?
- What happens to the clips when the switch opens?
- What happens to the poles when current reverses?

Reuse genuine H5P Interactive Video interactions, compact question panels and
visible Continue controls from Case 1 when that stage is requested.
