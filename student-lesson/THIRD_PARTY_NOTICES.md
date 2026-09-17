# Third-party notices

## Narration

The current fourteen-section tutor narration uses Microsoft's Edge speech
service, male Indian-English voice `en-IN-PrabhatNeural`. Authoring uses the
`edge-tts` 7.2.8 client (LGPL-3.0): https://github.com/rany2/edge-tts . The client
is not shipped to student browsers. Its full LGPLv3/MIT license notice is retained
in `assets/tutor-narration/CLIENT-LICENSE` in the parent project. Its license applies to the client, not to
Microsoft's voice model. Recorded output is not labelled as Apache-licensed
model output. Only the public lesson text is sent during authoring; student
playback uses the embedded soundtrack and does not call a speech service.

The earlier male Indian-English narration clips are generated with AI4Bharat's
`ai4bharat/indic-parler-tts` model, using its named English speaker Thoma.
The model is licensed under Apache 2.0. The lesson script is original.
The earlier 76-second first case contains thirteen sections generated through the official
public demonstration during authoring. The original reference recordings in
`assets/narration/` used the public demonstration for sections 1–8 and local
generation for sections 9–10, from model revision
`7b527af5ee8ed1f9a28d80b19703ed9bb8ba10ca`.
No student information is sent to the voice service. The completed audio is
embedded in the video; student playback does not call a voice service or need
a Hugging Face account. Model weights and account credentials are not deployed.

- Model and license: https://huggingface.co/ai4bharat/indic-parler-tts
- Official demonstration: https://huggingface.co/spaces/ai4bharat/indic-parler-tts


The lesson uses the official H5P libraries without changing their source.

- H5P Interactive Video and related content libraries: H5P Group / Joubel,
  obtained from https://hub-api.h5p.org/v1/content-types/H5P.InteractiveVideo .
  The source archive SHA-256 and exact component versions are recorded in
  `vendor/h5p-libraries.lock.json`. Each library retains its `library.json`,
  copyright comments, bundled license notices, and fonts.
- H5P standalone player 3.8.2: https://github.com/tunapanda/h5p-standalone ,
  MIT license. The package embeds H5P core and retains its upstream notices.
  Its LICENSE is copied beside the deployed player. The pnpm lockfile records
  the exact package integrity.
- Font Awesome 4.5: bundled license information is retained in its library.
  H5P's icon fonts and components retain the notices distributed upstream.
- jsdom 26.1.0 is a development-only dependency used to test the official H5P
  question code. It is not shipped to student browsers.

The lesson's CSS adapts the appearance of H5P through its supported `customCss`
option. The question and video logic remain the original H5P implementation.
