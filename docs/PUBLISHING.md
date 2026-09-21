# Publish the student lesson with GitHub Pages

The `main` branch contains the editable project. The `gh-pages` branch contains
the complete built website, including its video, captions and H5P runtime.
Students need no account. Playback makes no requests to the voice-generation
service or a separate video host.

## One-time repository setting

A repository owner, administrator or maintainer must configure GitHub Pages:

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select **gh-pages** and **/(root)**, then click **Save**.
4. Wait for the **pages build and deployment** run to finish in **Actions**.
5. Use **Visit site** on the Pages settings screen to open the final address.

The default project address is `https://<repository-owner>.github.io/<repository>/`.
A custom domain can be configured separately by the owner. See
[GitHub's publishing-source guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

The site uses a `.nojekyll` marker so GitHub serves the existing files directly.
No custom workflow, additional deployment token or server-side application is
required. The repository's Actions policies must allow GitHub's Pages deployment.

## Publish an update

Install the pinned website dependencies once using
`pnpm install --frozen-lockfile` inside `student-lesson/`. Commit the approved
source and media changes, then run this from the repository root:

```sh
python scripts/publish_github_pages.py
```

The script requires Python 3, Node.js, Git, installed website dependencies and
working GitHub credentials. Run it with the project's Python environment.
It builds and
tests H5P, copies the website into a temporary checkout, preserves deployment
history and pushes a new `gh-pages` commit with a neutral project identity.
It does not force-push. If another publication happens concurrently, update
your source as needed and rerun the script.

Changes pushed only to `main` do not update the public lesson. Run the publishing
script after the changed source, video and timing have been approved. A change to
questions or layout needs no Blender render; a changed animation needs the full
render and synchronization workflow in [DEVELOPMENT.md](DEVELOPMENT.md).

After publishing, wait for GitHub Pages to deploy and check the final address:

- The video and audio play, pause, seek and resume together.
- Case 1’s two questions support incorrect answers, retry and Continue.
- At `coils/`, both English and Hinglish choices load their own narration and
  four native questions; all four support retry and Continue.
- The question footer remains visible on a small phone screen.

## Student link and QR code

The current public lesson is [available here](https://nimisha-raina.github.io/modlab/).
Its QR files are included under `student-lesson/dist/share/` and published at
`share/lesson-qr.png` and `share/lesson-qr.svg` beneath the lesson address.

Once the final address is live and verified, generate a QR code for that address:

```sh
python3 -m pip install -r requirements-qr.txt
python3 scripts/create_lesson_qr.py https://your-public-lesson.example
```

The files appear in `output/share/`. A QR code encodes its original address;
switching hosts requires distributing the new code unless a redirect is kept.
