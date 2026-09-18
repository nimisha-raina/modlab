"""Archive and restore release materials; preserve complete private snapshots."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/"archive"
GENERATED = ARCHIVE/"generated"
CACHES = {"complete_review_frames","tutor_review_frames","extended_review_frames"}
EXTENSIONS = {".blend",".mp4",".mp3",".wav",".h5p",".srt",".vtt",".json",".jsonl",".png",".jpg",".svg"}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def write_text_lf(path,text):
    """Write generated text with LF endings, replacing locked-in-place files safely."""
    temporary = path.with_name(path.name+".tmp")
    temporary.write_bytes(text.encode("utf-8"))
    os.replace(temporary,path)


def archived_file(relative):
    path = (GENERATED/relative).resolve()
    if not path.is_relative_to(GENERATED.resolve()):
        raise ValueError("Archive path escapes the media directory")
    return path


def portable(value):
    if isinstance(value,dict):
        return {portable(k):portable(v) for k,v in value.items()}
    if isinstance(value,list):
        return [portable(v) for v in value]
    if isinstance(value,str):
        for prefix in (str(ROOT)+"\\",ROOT.as_posix()+"/"):
            value = value.replace(prefix,"")
        if re.search(r"[A-Za-z]:[\\/]Users[\\/]",value):
            return "external-runtime/"+re.split(r"[\\/]",value)[-1]
    return value


def prepare():
    GENERATED.mkdir(parents=True,exist_ok=True)
    files,jobs = [],[]
    for source in sorted((ROOT/"output").rglob("*")):
        if not source.is_file() or source.suffix.lower() not in EXTENSIONS:
            continue
        if any(part in CACHES for part in source.parts):
            continue
        relative = source.relative_to(ROOT/"output")
        target = GENERATED/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        original = digest(source)
        if source.suffix==".json":
            write_text_lf(target,json.dumps(portable(json.loads(source.read_text(encoding="utf-8"))),indent=2)+"\n")
        elif source.suffix==".jsonl":
            write_text_lf(target,"\n".join(json.dumps(portable(json.loads(line))) for line in source.read_text(encoding="utf-8").splitlines() if line.strip())+"\n")
        else:
            shutil.copy2(source,target)
        entry = {"path":relative.as_posix(),"original_sha256":original}
        files.append(entry)
        if source.suffix==".blend":
            jobs.append(entry)
    write_text_lf(ARCHIVE/"preparation.json",json.dumps({"files":files,"blender_jobs":jobs},indent=2)+"\n")
    print(f"ARCHIVE_PREPARED: {len(files)} files; {len(jobs)} Blender scenes.")


def finalize():
    preparation = json.loads((ARCHIVE/"preparation.json").read_text(encoding="utf-8"))
    frozen = GENERATED/"parts/frozen_case_01/manifest.json"
    data = json.loads(frozen.read_text(encoding="utf-8"))
    data.setdefault("original_files_sha256",data["files_sha256"].copy())
    data["files_sha256"] = {name:digest(frozen.parent/name) for name in data["files_sha256"]}
    data["packaging"] = "Portable packed scenes; approved geometry and animation unchanged. Exact original scenes remain in the private local snapshot."
    write_text_lf(frozen,json.dumps(data,indent=2)+"\n")
    for entry in preparation["files"]:
        file = GENERATED/entry["path"]
        entry["sha256"],entry["bytes"] = digest(file),file.stat().st_size
        if file.stat().st_size >= 100*1024*1024:
            raise ValueError("File exceeds GitHub per-file limit: "+entry["path"])
    result = {"schema":1,"date_utc":datetime.now(timezone.utc).isoformat(),
              "files":preparation["files"],"excluded_frame_caches":sorted(CACHES),
              "case_1":"Frozen 86-second narrated lesson with two H5P pauses.",
              "case_2":"Approved 136-second silent draft; three applications highlighted together for 11 seconds."}
    write_text_lf(ARCHIVE/"manifest.json",json.dumps(result,indent=2)+"\n")
    verify()


def verify():
    manifest = json.loads((ARCHIVE/"manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = archived_file(entry["path"])
        assert path.is_file() and path.stat().st_size==entry["bytes"],entry["path"]
        assert digest(path)==entry["sha256"],entry["path"]
    print(f"ARCHIVE_VERIFIED: {len(manifest['files'])} files, {sum(e['bytes'] for e in manifest['files'])} bytes.")


def restore():
    verify()
    for entry in json.loads((ARCHIVE/"manifest.json").read_text(encoding="utf-8"))["files"]:
        source = archived_file(entry["path"])
        target = (ROOT/"output"/entry["path"]).resolve()
        if not target.is_relative_to((ROOT/"output").resolve()):
            raise ValueError("Restore path escapes the output directory")
        if target.exists():
            if digest(target)!=entry["sha256"]:
                print("PRESERVED_EXISTING: "+entry["path"])
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    print("RESTORED: missing output files; existing work preserved.")


def snapshot():
    directory = ROOT/"backups"
    directory.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = directory/f"modlab-local-snapshot-{stamp}.zip"
    excluded = {".git",".cache","node_modules","backups","__pycache__",".openai",".sites-runtime",".codex",".agents"}
    entries = []
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
        sources = []
        for directory_name, directories, filenames in os.walk(ROOT):
            directories[:] = sorted(d for d in directories if d not in excluded and not d.startswith(".venv"))
            sources.extend(Path(directory_name)/name for name in sorted(filenames))
        for source in sources:
            relative = source.relative_to(ROOT)
            if any(p in excluded or p.startswith(".venv") for p in relative.parts):
                continue
            if not source.is_file() or source.name==".env" or source.name.startswith(".env.") and source.name!=".env.example":
                continue
            archive.write(source,relative.as_posix())
            entries.append({"path":relative.as_posix(),"sha256":digest(source),"bytes":source.stat().st_size})
        archive.writestr("SNAPSHOT-MANIFEST.json",json.dumps({"files":entries,"excluded":sorted(excluded)},indent=2)+"\n")
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for entry in entries:
            with archive.open(entry["path"]) as stream:
                assert hashlib.file_digest(stream,"sha256").hexdigest()==entry["sha256"],entry["path"]
    report = {"file":target.name,"sha256":digest(target),"files":len(entries),"bytes":target.stat().st_size,"verified":True}
    target.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("LOCAL_SNAPSHOT_VERIFIED: "+str(target.relative_to(ROOT)))
    print(json.dumps(report))


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","finalize","verify","restore","snapshot"))
    globals()[parser.parse_args().action]()
