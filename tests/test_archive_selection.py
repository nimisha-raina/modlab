"""A selected release update must preserve previously archived media."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("archive_project",Path(__file__).resolve().parents[1]/"scripts/archive_project.py")
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class ArchiveSelectionTests(unittest.TestCase):
    def test_selected_update_preserves_existing_release_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root/"archive/generated"
            generated.mkdir(parents=True)
            (root/"output").mkdir()
            old = generated/"case-one.mp4"
            old.write_bytes(b"frozen original media")
            entry = dict(path=old.name,original_sha256=archive.digest(old),sha256=archive.digest(old),bytes=old.stat().st_size)
            (root/"archive/manifest.json").write_text(json.dumps(dict(files=[entry])))
            # A local working revision of an unselected case must not leak in.
            (root/"output/case-one.mp4").write_bytes(b"unselected local edit")
            (root/"output/case-two.mp4").write_bytes(b"new case two")
            with patch.multiple(archive,ROOT=root,ARCHIVE=root/"archive",GENERATED=generated):
                archive.prepare(["case-two.mp4"])
            preparation = json.loads((root/"archive/preparation.json").read_text())
            self.assertEqual(old.read_bytes(),b"frozen original media")
            self.assertEqual({e["path"] for e in preparation["files"]},{"case-one.mp4","case-two.mp4"})
            self.assertEqual((generated/"case-two.mp4").read_bytes(),b"new case two")

    def test_selection_cannot_escape_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.multiple(archive,ROOT=root,ARCHIVE=root/"archive",GENERATED=root/"archive/generated"):
                with self.assertRaises(ValueError):
                    archive.prepare(["../outside.mp4"])
