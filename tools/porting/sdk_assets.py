#!/usr/bin/env python3
"""Restore the SDK's separately packaged build dependencies from GitHub Releases."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "tools/porting/assets"


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_id(path, mode):
    if mode == "120000":
        data = os.readlink(path).encode()
        return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    size = path.stat().st_size
    digest = hashlib.sha1(f"blob {size}\0".encode())
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe archive path: {name}")
    return str(path)


def matches(path, mode, oid):
    if mode == "120000":
        if not path.is_symlink():
            return False
    else:
        if path.is_symlink() or not path.is_file():
            return False
        if bool(path.stat().st_mode & 0o111) != (mode == "100755"):
            return False
    return git_blob_id(path, mode) == oid


def load_files():
    process = subprocess.Popen(["zstd", "-dc", str(ASSETS / "files.tsv.zst")],
                               stdout=subprocess.PIPE, text=True)
    files = {}
    try:
        with process.stdout:
            for line in process.stdout:
                mode, oid, size, encoded = line.rstrip("\n").split("\t", 3)
                name = safe_name(json.loads(encoded))
                files[name] = (mode, oid, int(size))
        if process.wait():
            raise RuntimeError("Cannot read SDK dependency file inventory")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
    return files


def fetch():
    if sys.version_info < (3, 12):
        raise SystemExit("Python 3.12+ is required for safe archive extraction")
    for executable in ("gh", "zstd"):
        if not shutil.which(executable):
            raise SystemExit(f"Install {executable} before restoring SDK dependencies")
    manifest = json.loads((ASSETS / "manifest.json").read_text())
    files = load_files()
    cache = ROOT / ".git/sdk-assets"
    cache.mkdir(parents=True, exist_ok=True)
    missing_bytes, present = 0, 0
    for name, (mode, oid, size) in files.items():
        target = ROOT / name
        if target.exists() or target.is_symlink():
            if not matches(target, mode, oid):
                raise SystemExit(f"Refusing to replace an existing different file: {name}")
            present += 1
        else:
            missing_bytes += size
    if present == len(files):
        print(f"SDK dependencies already ready: {present} files verified")
        return
    needed = missing_bytes + sum(item["bytes"] for item in manifest["archives"]
                                 if not (cache / safe_name(item["name"])).exists())
    if shutil.disk_usage(ROOT).free < needed:
        raise SystemExit(f"Need approximately {needed / 2**30:.1f} GiB free for download and extraction")
    archives = []
    for item in manifest["archives"]:
        filename = safe_name(item["name"])
        if "/" in filename:
            raise ValueError("Archive asset names must be plain filenames")
        path = cache / filename
        if not path.exists():
            subprocess.run(["gh", "release", "download", manifest["release"],
                            "--repo", manifest["repository"], "--pattern", filename,
                            "--dir", str(cache)], check=True)
        if path.stat().st_size != item["bytes"] or file_sha256(path) != item["sha256"]:
            raise SystemExit(f"Dependency archive checksum failed: {path}")
        archives.append(path)
        print(f"Verified {filename}", flush=True)
    source = subprocess.Popen(["cat", *map(str, archives)], stdout=subprocess.PIPE)
    decoder = subprocess.Popen(["zstd", "-dc"], stdin=source.stdout, stdout=subprocess.PIPE)
    source.stdout.close()
    count = 0
    try:
        with tarfile.open(fileobj=decoder.stdout, mode="r|") as archive:
            for member in archive:
                name = safe_name(member.name)
                if member.isdir():
                    continue
                if name not in files:
                    raise ValueError(f"Unexpected dependency file: {name}")
                mode, oid, size = files[name]
                if member.issym() != (mode == "120000") or member.islnk():
                    raise ValueError(f"Unexpected archive member type: {name}")
                if member.isfile() and member.size != size:
                    raise ValueError(f"Unexpected dependency size: {name}")
                target = ROOT / name
                if not target.exists() and not target.is_symlink():
                    archive.extract(member, path=ROOT, filter="data")
                if not matches(target, mode, oid):
                    raise ValueError(f"Restored dependency content mismatch: {name}")
                count += 1
                if count % 10000 == 0:
                    print(f"Restored {count}/{len(files)} dependency files", flush=True)
        if decoder.wait() or source.wait():
            raise RuntimeError("Dependency archive decompression failed")
        if count != len(files):
            raise ValueError(f"Dependency coverage mismatch: {count} != {len(files)}")
    finally:
        decoder.stdout.close()
        for process in (decoder, source):
            if process.poll() is None:
                process.kill()
                process.wait()
    print(f"SDK dependencies ready: {count} files verified against their original Git blob IDs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["fetch"])
    parser.parse_args()
    fetch()
