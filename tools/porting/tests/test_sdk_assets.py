import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "sdk_assets", Path(__file__).resolve().parents[1] / "sdk_assets.py")
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)


class ArchivePathTest(unittest.TestCase):
    def test_escaping_archive_names_are_rejected(self):
        for name in ("/absolute", "../escape", "prebuilts/../escape"):
            with self.assertRaises(ValueError):
                assets.safe_name(name)


@unittest.skipUnless(shutil.which("zstd") and sys.version_info >= (3, 12),
                     "archive restore requires zstd and Python 3.12+")
class DependencyRestoreTest(unittest.TestCase):
    def fixture(self, root):
        folder = root / "tools/porting/assets"
        cache = root / ".git/sdk-assets"
        folder.mkdir(parents=True)
        cache.mkdir(parents=True)
        data, name, link = b"#!/bin/sh\nexit 0\n", "prebuilts/test/bin/tool", "prebuilts/test/bin/alias"
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as archive:
            regular = tarfile.TarInfo(name)
            regular.mode, regular.size = 0o755, len(data)
            archive.addfile(regular, io.BytesIO(data))
            alias = tarfile.TarInfo(link)
            alias.type, alias.linkname = tarfile.SYMTYPE, "tool"
            archive.addfile(alias)
        compressed = subprocess.check_output(["zstd", "-q", "-c"], input=buffer.getvalue())
        filename = "deps.part000"
        (cache / filename).write_bytes(compressed)
        def oid(value):
            return hashlib.sha1(f"blob {len(value)}\0".encode() + value).hexdigest()
        rows = (f'100755\t{oid(data)}\t{len(data)}\t{json.dumps(name)}\n'
                f'120000\t{oid(b"tool")}\t4\t{json.dumps(link)}\n')
        (folder / "files.tsv.zst").write_bytes(
            subprocess.check_output(["zstd", "-q", "-c"], input=rows.encode()))
        (folder / "manifest.json").write_text(json.dumps({
            "logical_bytes": len(data) + 4, "repository": "fixture/private", "release": "fixture",
            "archives": [{"name": filename, "bytes": len(compressed),
                          "sha256": hashlib.sha256(compressed).hexdigest()}]}))
        return folder, name, link, data

    def test_verified_archive_restores_binary_mode_and_symlink_without_network(self):
        with tempfile.TemporaryDirectory(prefix="y02-assets-test-") as temporary:
            root = Path(temporary)
            folder, name, link, data = self.fixture(root)
            with patch.object(assets, "ROOT", root), patch.object(assets, "ASSETS", folder), \
                    patch.object(assets.shutil, "which", return_value="installed"):
                assets.fetch()
                # An already restored SDK needs no additional disk allocation.
                with patch.object(assets.shutil, "disk_usage", side_effect=AssertionError("unneeded space check")):
                    assets.fetch()
            self.assertEqual((root / name).read_bytes(), data)
            self.assertTrue((root / name).stat().st_mode & 0o111)
            self.assertTrue((root / link).is_symlink())
            self.assertEqual((root / link).readlink(), Path("tool"))

    def test_existing_modified_dependency_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="y02-assets-preserve-") as temporary:
            root = Path(temporary)
            folder, name, _, _ = self.fixture(root)
            target = root / name
            target.parent.mkdir(parents=True)
            target.write_bytes(b"user modification")
            with patch.object(assets, "ROOT", root), patch.object(assets, "ASSETS", folder), \
                    patch.object(assets.shutil, "which", return_value="installed"):
                with self.assertRaises(SystemExit):
                    assets.fetch()
            self.assertEqual(target.read_bytes(), b"user modification")

    def test_missing_executable_permission_is_not_reported_ready(self):
        with tempfile.TemporaryDirectory(prefix="y02-assets-mode-") as temporary:
            root = Path(temporary)
            folder, name, _, data = self.fixture(root)
            target = root / name
            target.parent.mkdir(parents=True)
            target.write_bytes(data)
            target.chmod(0o644)
            with patch.object(assets, "ROOT", root), patch.object(assets, "ASSETS", folder), \
                    patch.object(assets.shutil, "which", return_value="installed"):
                with self.assertRaises(SystemExit):
                    assets.fetch()
            self.assertFalse(target.stat().st_mode & 0o111)


if __name__ == "__main__":
    unittest.main()
