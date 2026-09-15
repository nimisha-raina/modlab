"""Build the genuine H5P lesson from readable questions and official libraries.

Run from student-lesson after `pnpm install`: python3 scripts/build_h5p.py
The Blender video is copied into dist/assets before running this script.
"""

import copy
import html
import json
from pathlib import Path
import shutil
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LIBRARIES = ROOT / "vendor" / "h5p-libraries"
PACKAGE = DIST / "h5p" / "electromagnetism"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def defaults(fields):
    """Use the upstream H5P semantics for labels and behavioural defaults."""
    values = {}
    for field in fields:
        if "default" in field:
            values[field["name"]] = copy.deepcopy(field["default"])
        elif field["type"] == "group":
            value = defaults(field["fields"])
            if value:
                values[field["name"]] = value
    return values


def question_interaction(question, index, time):
    params = defaults(read(LIBRARIES / "H5P.MultiChoice-1.16" / "semantics.json"))
    params["question"] = f'<p>{html.escape(question["question"])}</p>'
    if question.get("context"):
        params["question"] += f'<p class="lesson-question-context">{html.escape(question["context"])}</p>'
    params["answers"] = [
        {"text": f"<p>{html.escape(answer)}</p>", "correct": i == question["correct"], "tipsAndFeedback": {}}
        for i, answer in enumerate(question["answers"])
    ]
    # This group is flattened by H5P's RangeList authoring widget.
    params["overallFeedback"] = [
        {"from": 0, "to": 99, "feedback": question["hint"]},
        {"from": 100, "to": 100, "feedback": question["success"]},
    ]
    params["behaviour"].update({"type": "single", "randomAnswers": False,
        "enableSolutionsButton": False, "enableRetry": True, "showScorePoints": False})
    params["UI"].update({"checkAnswerButton": "Check answer", "tryAgainButton": "Try again"})
    title = f"Question {index + 1} of 3"
    return {
        "duration": {"from": time, "to": time},
        "pause": True,
        # Required H5P button interactions automatically open the native dialog.
        # This gives the same in-player popup and native close transition on phones.
        "displayType": "button", "buttonOnMobile": False,
        "label": f"<p>{title}</p>", "x": 77, "y": 22,
        "width": 22, "height": 15, "libraryTitle": title,
        "action": {"library": "H5P.MultiChoice 1.16", "params": params,
            "subContentId": str(uuid.uuid5(uuid.NAMESPACE_URL, "electromagnetism/" + question["id"])),
            "metadata": {"title": title, "license": "U", "contentType": "Multiple Choice"}},
        "adaptivity": {"requireCompletion": True},
    }


def main():
    standalone = ROOT / "node_modules" / "h5p-standalone"
    if not (standalone / "dist" / "main.bundle.js").is_file():
        raise SystemExit("Install the pinned dependencies with pnpm install first.")
    shutil.copytree(standalone / "dist", DIST / "vendor" / "h5p-player", dirs_exist_ok=True)
    shutil.copy2(standalone / "LICENSE", DIST / "vendor" / "h5p-player" / "LICENSE")
    PACKAGE.mkdir(parents=True, exist_ok=True)
    dependencies = []
    for library in sorted(LIBRARIES.iterdir()):
        meta = read(library / "library.json")
        dependencies.append({key: meta[key] for key in ("machineName", "majorVersion", "minorVersion")})
        shutil.copytree(library, PACKAGE / library.name, dirs_exist_ok=True)

    questions = read(ROOT / "content" / "questions.json")
    captions = read(ROOT / "content/captions.json")
    timing_path = ROOT / "content/narration-timing.json"
    narrated = timing_path.exists()
    timing = read(timing_path) if narrated else {
        "duration": captions[-1][1],
        "segments": [{"target_end":caption[1]} for caption in captions],
    }
    duration = timing["duration"]
    times = [round(timing["segments"][q["after_section"]-1]["target_end"]-.3,3) for q in questions]
    assert len(questions) == 3
    assert all(0 <= q["correct"] < len(q["answers"]) for q in questions)
    assert all(0 < time < duration for time in times)
    (DIST / "captions.js").write_text("window.LESSON_CAPTIONS = " + json.dumps(
        captions) + ";\n" +
        "window.LESSON_METADATA = " + json.dumps({"duration":duration,"questions":len(questions),"narrated":narrated}) + ";\n")
    params = defaults(read(LIBRARIES / "H5P.InteractiveVideo-1.28" / "semantics.json"))
    params["interactiveVideo"] = {
        "video": {"files": [{"path": "videos/electromagnetism.mp4", "mime": "video/mp4",
            "copyright": {"license": "U"}}], "startScreenOptions": {
            "title": "Electricity makes magnetism", "hideStartTitle": True,
            "shortStartDescription": "", "poster": {"path": "images/poster.jpg", "mime": "image/jpeg",
                "width": 1280, "height": 720, "copyright": {"license": "U"}}}},
        "assets": {"interactions": [question_interaction(q, i, times[i]) for i, q in enumerate(questions)],
            "bookmarks": [], "endscreens": [{"time": duration, "label": "Your discoveries"}]},
        "summary": {"task": {"library": "H5P.Summary 1.10", "params": {"summaries": []}}, "displayAt": 0},
    }
    params["override"].update({"autoplay": False, "loop": False, "hasNoAutoPause": False,
        "showSolutionButton": "off", "retryButton": "on", "showRewind10": True,
        "preventSkippingMode": "forward", "deactivateSound": not narrated})
    params["l10n"].update({"defaultAdaptivitySeekLabel": "Continue video",
        "requiresCompletionWarning": "Give this question another try before continuing.",
        "endcardTitle": "Your discoveries", "endcardInformationOnSubmitButtonDisabled": "You explored @answered questions.",
        "endscreen": "View your answers"})
    write(PACKAGE / "content" / "content.json", params)
    write(PACKAGE / "h5p.json", {"title": "Electricity makes magnetism — Class 8",
        "language": "en", "mainLibrary": "H5P.InteractiveVideo", "embedTypes": ["iframe"],
        "license": "U", "preloadedDependencies": dependencies})
    for source, target in [(DIST / "assets/electromagnetism.mp4", PACKAGE / "content/videos/electromagnetism.mp4"),
                           (DIST / "assets/poster.jpg", PACKAGE / "content/images/poster.jpg")]:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # A portable H5P file can be imported into a school H5P authoring platform.
    destination = ROOT.parent / "output/share/electromagnetism.h5p"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(PACKAGE))
    print(f"Built H5P Interactive Video: 3 questions; {len(dependencies)} official runtime libraries.")


if __name__ == "__main__":
    main()
