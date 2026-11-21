import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[1] / "non_chroot.py"
SPEC = importlib.util.spec_from_file_location("non_chroot", MODULE)
port = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(port)


class ExportSafetyTest(unittest.TestCase):
    def test_binary_modes_and_object_index_isolation(self):
        with tempfile.TemporaryDirectory(prefix="x7-native-test-") as temporary:
            root = Path(temporary)
            repo = root / "repository"
            repo.mkdir()
            git = port.Git(repo)
            git.environment.update({
                "GIT_AUTHOR_NAME": "Port export test",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "Port export test",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            })
            git.run("init", "--quiet")
            blob, executable = repo / "firmware.bin", repo / "launcher.sh"
            blob.write_bytes(b"\0\xfffactory\0")
            executable.write_text("#!/bin/sh\nexit 0\n")
            git.run("add", ".")
            git.run("commit", "--quiet", "-m", "fixture baseline")
            before = git.text("rev-parse", "HEAD")
            blob.write_bytes(b"\0\xffported-firmware\0\x80")
            executable.chmod(0o755)
            git.run("add", ".")
            git.run("commit", "--quiet", "-m", "fixture binary and mode changes")
            after = git.text("rev-parse", "HEAD")
            original_index = hashlib.sha256((repo / ".git/index").read_bytes()).digest()
            original_objects = {p.relative_to(repo / ".git/objects")
                                for p in (repo / ".git/objects").rglob("*") if p.is_file()}
            with git.isolated():
                patch = root / "roundtrip.patch"
                port.save(patch, git.patch(before, after))
                git.run("read-tree", before)
                git.run("apply", "--cached", patch)
                self.assertEqual(git.text("write-tree"), git.text("rev-parse", after + "^{tree}"))
                self.assertTrue(git.run("ls-files", "--stage", "launcher.sh").startswith(b"100755 "))
                git.run("apply", "--cached", "--reverse", patch)
                self.assertEqual(git.text("write-tree"), git.text("rev-parse", before + "^{tree}"))
                git.replace_bytes("curated.xml", b"<resources/>\n")
                synthetic = git.text("write-tree")
                self.assertEqual(git.run("show", synthetic + ":curated.xml"), b"<resources/>\n")
            self.assertEqual(hashlib.sha256((repo / ".git/index").read_bytes()).digest(), original_index)
            self.assertEqual(git.text("rev-parse", "HEAD"), after)
            self.assertEqual(blob.read_bytes(), b"\0\xffported-firmware\0\x80")
            self.assertFalse((repo / "curated.xml").exists())
            self.assertEqual(original_objects, {p.relative_to(repo / ".git/objects")
                             for p in (repo / ".git/objects").rglob("*") if p.is_file()})

    def test_regeneration_never_overwrites_edits_or_follows_symlinks(self):
        with tempfile.TemporaryDirectory(prefix="x7-native-save-") as temporary:
            root = Path(temporary)
            output = root / "patch"
            port.save(output, b"original")
            port.save(output, b"original")
            with self.assertRaises(FileExistsError):
                port.save(output, b"replacement")
            self.assertEqual(output.read_bytes(), b"original")
            link = root / "symlink"
            link.symlink_to(root / "missing-target")
            with self.assertRaises(FileExistsError):
                port.save(link, b"unexpected")
            self.assertFalse((root / "missing-target").exists())


if __name__ == "__main__":
    unittest.main()
