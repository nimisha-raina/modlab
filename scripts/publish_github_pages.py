"""Build, test and publish the student website to the gh-pages branch.

Run from a clean source checkout with GitHub write access and Node.js installed.
The repository owner must enable GitHub Pages once; see docs/PUBLISHING.md.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "student-lesson"


def run(*args, cwd=ROOT, capture=False, env=None):
    result = subprocess.run(args, cwd=cwd, check=True, text=True, env=env,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def publish(remote):
    if run("git", "status", "--porcelain", capture=True):
        raise SystemExit("Commit or set aside source changes before publishing.")
    source_revision = run("git", "rev-parse", "HEAD", capture=True)
    remote_url = run("git", "remote", "get-url", remote, capture=True)
    # Use the active Python and Node directly; Windows may map python3 to a
    # store shortcut and cannot execute pnpm.cmd through subprocess uniformly.
    run(sys.executable, "scripts/build_h5p.py", cwd=SITE)
    run(sys.executable, "scripts/build_coil_h5p.py", cwd=SITE)
    run(sys.executable, "scripts/build_case_one_h5p.py", cwd=SITE)
    run("node", "scripts/test_lessons.cjs", cwd=SITE)
    dist = SITE / "dist"
    for name in ["index.html", "captions.js", "vendor/h5p-player/main.bundle.js",
                 "h5p/electromagnetism/content/content.json",
                 "h5p/electromagnetism/content/videos/electromagnetism.mp4",
                 "coils/index.html","coils/config.js","case-one-config.js",
                 "h5p/case-one-english/content/videos/lesson.mp4",
                 "h5p/case-one-hinglish/content/videos/lesson.mp4",
                 "h5p/coil-english/content/videos/coil.mp4",
                 "h5p/coil-hinglish/content/videos/coil.mp4"]:
        if not (dist / name).is_file():
            raise SystemExit(f"Missing website asset: {name}")
    if any(p.is_symlink() for p in dist.rglob("*")):
        raise SystemExit("Publish regular files, not links to local dependencies.")
    release={"source_revision":source_revision,"case_one":{},"case_two":{}}
    for case,prefix,filename in (('case_one','case-one','lesson.mp4'),('case_two','coil','coil.mp4')):
        for language in ('english','hinglish'):
            media=dist/f'h5p/{prefix}-{language}/content/videos/{filename}'
            with media.open('rb') as stream:
                checksum=hashlib.file_digest(stream,'sha256').hexdigest()
            release[case][language]={"sha256":checksum,"bytes":media.stat().st_size}
    (dist/'release.json').write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8')

    existing = run("git", "ls-remote", "--heads", remote, "gh-pages", capture=True)
    (ROOT / "output").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pages-", dir=ROOT / "output") as folder:
        checkout = Path(folder)
        if existing:
            run("git", "clone", "--quiet", "--single-branch", "--branch", "gh-pages",
                remote_url, str(checkout))
            # This branch contains only generated website files. Retain its Git
            # history while replacing the previous deployment's tracked files.
            run("git", "rm", "-r", "--quiet", "--ignore-unmatch", ".", cwd=checkout)
        else:
            run("git", "init", "--quiet", "--initial-branch=gh-pages", cwd=checkout)
            run("git", "remote", "add", "origin", remote_url, cwd=checkout)
        shutil.copytree(dist, checkout, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".DS_Store"))
        shutil.copy2(SITE / "THIRD_PARTY_NOTICES.md", checkout)
        shutil.copy2(SITE / "vendor/h5p-libraries.lock.json", checkout / "vendor")
        (checkout / ".nojekyll").touch()
        (checkout / ".gitattributes").write_text("* -text\n")
        run("git", "add", ".", cwd=checkout)
        if not run("git", "status", "--porcelain", cwd=checkout, capture=True):
            print("The published website files are already current.")
            return
        identity = os.environ.copy()
        identity.update({"GIT_AUTHOR_NAME": "Modlab Project",
                         "GIT_AUTHOR_EMAIL": "project@modlab.invalid",
                         "GIT_COMMITTER_NAME": "Modlab Project",
                         "GIT_COMMITTER_EMAIL": "project@modlab.invalid"})
        run("git", "-c", "commit.gpgSign=false", "commit", "--quiet",
            "-m", "Publish interactive electromagnetism lesson",
            "-m", f"Source revision: {source_revision}", cwd=checkout, env=identity)
        # A concurrent publication is rejected instead of overwriting its history.
        run("git", "push", "origin", "HEAD:gh-pages", cwd=checkout)
    print("Website uploaded to gh-pages. Check GitHub Pages for deployment status.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", default="origin", help="Existing Git remote to publish to")
    publish(parser.parse_args().remote)
