#!/usr/bin/env python3
"""Export and verify the X7 Pro Android port without container integration."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SDK = ROOT / "android13_sdk/RK3562_Android13.0_SDK"
OUTPUT = ROOT / "patches/android13/non-chroot"
BASE = "2739aad12478b269998fbac4ea39f396f4695f9f"
SNAPSHOT = "1a2da0cd230e447abd85f1eaaa7e0b5e50fda036"
LATER = "2f8600284e4f869435f1b3689fb79ab9f55a8aee"
PRODUCT = "device/rockchip/rk3562/rk3562_x7pro_go/"
KCONFIG = "kernel-5.10/kernel/configs/x7pro.config"
OVERLAY = PRODUCT + "overlay/frameworks/base/core/res/res/values/config.xml"
MODULES = (
    ("host-build", "Host build scripts and repository guidance"),
    ("product", "X7 Pro product, FIT packaging and captured vendor assets"),
    ("rockchip-common", "Shared Rockchip init, permissions and recovery integration"),
    ("kernel-stable-abi", "Kernel version reconciliation, core and vendor module ABI"),
    ("kernel-board", "Board DTS and X7 Pro kernel configuration"),
    ("kernel-display-input", "Display, touch and sensor drivers"),
    ("kernel-camera", "Camera sensor drivers"),
    ("kernel-audio", "Audio codecs and amplifier"),
    ("kernel-usb-radio-power", "DWC3, Type-C, SDIO radio and battery support"),
    ("hal-connectivity", "BES2600 Wi-Fi and Bluetooth Android interfaces"),
    ("hal-media", "Rockchip audio, camera and TEE service integration"),
    ("framework-storage-adb", "Framework, storage, seccomp and USB ADB"),
    ("settings-camera", "Settings and Camera2 application fixes"),
)


def classify(path):
    if path in {"AGENTS.md", "build.sh", "javaenv.sh", "rkbin/.gitignore",
                "rkbin/tools/config.ini"}:
        return "host-build"
    if path.startswith(PRODUCT) or path == "device/rockchip/rk3562/AndroidProducts.mk":
        return "product"
    if path.startswith("device/rockchip/common/"):
        return "rockchip-common"
    if path.startswith("kernel-5.10/"):
        relative = path[len("kernel-5.10/"):]
        if relative in {"arch/arm64/boot/dts/rockchip/Makefile",
                        "arch/arm64/boot/dts/rockchip/rk3562-y02-v10.dts",
                        "kernel/configs/x7pro.config"}:
            return "kernel-board"
        if relative.startswith(("drivers/input/", "drivers/gpu/drm/panel/panel-simple.c",
                                "drivers/gpu/drm/rockchip/")):
            return "kernel-display-input"
        if relative.startswith("drivers/media/i2c/"):
            return "kernel-camera"
        if relative.startswith("sound/soc/codecs/"):
            return "kernel-audio"
        if relative.startswith(("drivers/usb/dwc3/", "drivers/usb/typec/",
                                "drivers/mmc/core/", "net/rfkill/")) or relative in {
                                    "drivers/power/supply/rk817_battery.c",
                                    "include/linux/mmc/host.h", "include/linux/mmc/mmc.h"}:
            return "kernel-usb-radio-power"
        return "kernel-stable-abi"
    if path.startswith(("frameworks/opt/net/wifi/", "hardware/bes/",
                        "hardware/interfaces/bluetooth/", "hardware/interfaces/wifi/")):
        return "hal-connectivity"
    if path.startswith(("hardware/rockchip/audio/", "hardware/rockchip/camera/",
                        "hardware/rockchip/optee/")):
        return "hal-media"
    if path.startswith(("frameworks/av/", "frameworks/base/", "system/core/",
                        "packages/modules/adb/", "vendor/rockchip/")):
        return "framework-storage-adb"
    if path.startswith(("packages/apps/Settings/", "packages/apps/Camera2/")):
        return "settings-camera"
    raise ValueError(f"Unclassified path (update the module map explicitly): {path}")


class Git:
    def __init__(self, sdk, executable=None):
        self.sdk = Path(sdk)
        self.executable = executable or shutil.which("git")
        if not self.executable:
            self.executable = str(ROOT / "tools/git-debian/usr/bin/git")
        self.environment = os.environ.copy()
        for key in ("GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                    "GIT_DIR", "GIT_WORK_TREE"):
            self.environment.pop(key, None)
        self.environment["LC_ALL"] = "C"

    def run(self, *args, data=None):
        result = subprocess.run(
            [self.executable, "-C", str(self.sdk), "-c", "core.autocrlf=false",
             "-c", "core.quotePath=false", *map(str, args)],
            input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.environment,
        )
        if result.returncode:
            raise RuntimeError(f"git {' '.join(map(str, args))}:\n"
                               + result.stderr.decode(errors="replace"))
        return result.stdout

    def text(self, *args):
        return self.run(*args).decode().strip()

    @contextmanager
    def isolated(self):
        original = self.environment.copy()
        object_dir = self.text("rev-parse", "--git-path", "objects")
        object_dir = (self.sdk / object_dir).resolve()
        with tempfile.TemporaryDirectory(prefix="x7-native-index-") as name:
            temporary = Path(name)
            (temporary / "objects").mkdir()
            self.environment["GIT_INDEX_FILE"] = str(temporary / "index")
            self.environment["GIT_OBJECT_DIRECTORY"] = str(temporary / "objects")
            self.environment["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(object_dir)
            try:
                yield
            finally:
                self.environment = original

    def changed(self, before, after):
        fields = self.run("diff", "--no-renames", "--name-status", "-z", before, after).split(b"\0")
        return [(fields[i].decode(), fields[i + 1].decode())
                for i in range(0, len(fields) - 1, 2)]

    def patch(self, before, after, paths=None):
        args = ["diff", "--binary", "--full-index", "--no-renames", "--no-ext-diff",
                "--no-textconv", "--no-color", "--src-prefix=a/", "--dst-prefix=b/",
                before, after]
        if paths is not None:
            args += ["--", *[f":(literal){path}" for path in paths]]
        return self.run(*args)

    def replace(self, revision, paths):
        for path in paths:
            record = self.run("ls-tree", "-z", revision, "--", path).rstrip(b"\0")
            meta, actual = record.split(b"\t", 1)
            mode, kind, oid = meta.split()
            if kind != b"blob" or actual.decode() != path:
                raise ValueError(f"Expected an exact blob: {revision}:{path}")
            self.run("update-index", "--add", "--cacheinfo", mode.decode(), oid.decode(), path)

    def replace_bytes(self, path, contents):
        oid = self.run("hash-object", "-w", "--stdin", data=contents).decode().strip()
        self.run("update-index", "--add", "--cacheinfo", "100644", oid, path)


def save(path, contents):
    """Regeneration is allowed only when an existing file is byte-identical."""
    if isinstance(contents, str):
        contents = contents.encode()
    if path.is_symlink():
        raise FileExistsError(f"Refusing to write through a symlink: {path}")
    if path.exists():
        if not path.is_file() or path.read_bytes() != contents:
            raise FileExistsError(f"Refusing to overwrite different content: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(contents)


def emit(git, output, name, before, after, paths=None, provenance=None):
    content = git.patch(before, after, paths)
    if not content:
        raise ValueError(f"Empty patch: {name}")
    save(output / name, content)
    changed = git.changed(before, after)
    if paths is not None:
        changed = [item for item in changed if item[1] in paths]
    return {"file": name, "sha256": hashlib.sha256(content).hexdigest(),
            "paths": [{"status": status, "path": path} for status, path in changed],
            "provenance": provenance or []}


def supplement(git, output):
    stages = []
    git.run("read-tree", SNAPSHOT)
    previous = git.text("write-tree")

    def stage(name, provenance):
        nonlocal previous
        target = git.text("write-tree")
        stages.append(emit(git, output, "supplement/" + name, previous, target,
                           provenance=provenance))
        previous = target

    hardware = "47e23b6e25d860c17d9fc90566ba15cc5716b489"
    git.replace(hardware, [
        "kernel-5.10/drivers/input/touchscreen/x7_sitronix_ts_main.c",
        "kernel-5.10/drivers/leds/Kconfig", "kernel-5.10/drivers/leds/Makefile",
        "kernel-5.10/drivers/leds/leds-x7pro-scan.c",
        "kernel-5.10/drivers/video/rockchip/rga3/rga_mm.c",
    ])
    config = git.run("show", f"{SNAPSHOT}:{KCONFIG}")
    anchor = b"CONFIG_VIDEO_SC035GS=y\n"
    if config.count(anchor) != 1:
        raise ValueError("Kernel config anchor changed")
    git.replace_bytes(KCONFIG, config.replace(anchor, anchor +
                      b"CONFIG_LEDS_CLASS_FLASH=y\nCONFIG_LEDS_X7PRO_SCAN=y\n"))
    stage("0001-touch-led-rga.patch", [hardware,
          "Keep only touch polling, scan LEDs, RGA DMA and their LED config flags; "
          "exclude namespace/cgroup additions and the legacy stock camera ioctl."])

    camera = "ba963249122d9a946c5d4e49f21da5f3f28342b3"
    git.replace(camera, [path for _, path in git.changed(camera + "^", camera)])
    stage("0002-camera-pipeline-flash.patch", [camera])

    python = "15a1742197edec269449cad454eba909b467d3fc"
    git.replace(python, ["build/make/tools/fileslist_util.py"])
    stage("0003-python3-fileslist.patch", [python])

    memory = "81bef3ff90bddc1b597ce5c0b20e55dda352af4a"
    git.replace(memory, [path for _, path in git.changed(memory + "^", memory)])
    stage("0004-settings-realtime-memory.patch", [memory])

    # Reconstruct just the independent power fix: the original file also grants
    # notification access to ModeBridge, which does not belong in this bundle.
    later_overlay = git.run("show", f"{LATER}:{OVERLAY}")
    if b'<bool name="config_flipToScreenOffEnabled">false</bool>' not in later_overlay:
        raise ValueError("The recorded independent power fix is no longer present")
    git.replace_bytes(OVERLAY, b'<?xml version="1.0" encoding="utf-8"?>\n'
                      b'<resources>\n'
                      b'    <!-- The pen is commonly held with the phone-style Z axis facing down. -->\n'
                      b'    <bool name="config_flipToScreenOffEnabled">false</bool>\n'
                      b'</resources>\n')
    stage("0005-display-face-down-gesture.patch", [LATER,
          "Extract only the display power bool; omit ModeBridge listener permission."])
    return stages, previous


def export(git, output):
    groups = {name: [] for name, _ in MODULES}
    for _, path in git.changed(BASE, SNAPSHOT):
        groups[classify(path)].append(path)
    patches = []
    for index, (name, title) in enumerate(MODULES, 1):
        if not groups[name]:
            continue
        item = emit(git, output, f"final12/{index:04d}-{name}.patch", BASE, SNAPSHOT,
                    paths=groups[name])
        item["module"] = name
        item["title"] = title
        patches.append(item)
    extra, native_tree = supplement(git, output)
    manifest = {"format": 1, "base_commit": BASE, "snapshot_commit": SNAPSHOT,
                "snapshot_tree": git.text("rev-parse", f"{SNAPSHOT}^{{tree}}"),
                "later_history_commit": LATER, "native_tree": native_tree,
                "snapshot_patches": patches, "supplement_patches": extra}
    rows = ["phase\tmodule\tstatus\tpath"]
    for phase, items in (("final12", patches), ("supplement", extra)):
        save(output / phase / "series", "".join(Path(p["file"]).name + "\n" for p in items))
        for item in items:
            for path in item["paths"]:
                rows.append(f"{phase}\t{item.get('module', Path(item['file']).stem)}"
                            f"\t{path['status']}\t{path['path']}")
    save(output / "PATHS.tsv", "\n".join(rows) + "\n")
    save(output / "series", "".join(p["file"] + "\n" for p in patches + extra))
    save(output / "SHA256SUMS", "".join(f"{p['sha256']}  {p['file']}\n" for p in patches + extra))
    save(output / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    covered = {p["path"] for item in extra for p in item["paths"]}
    excluded = [f"{status}\t{path}" for status, path in git.changed(SNAPSHOT, LATER)
                if path not in covered]
    save(output / "EXCLUDED.tsv", "status\tpath\n" + "\n".join(excluded) + "\n")
    print(f"Exported {len(patches)} final12 patches / {sum(map(len, groups.values()))} paths; "
          f"{len(extra)} curated supplement patches. {output}", flush=True)


def check(git, output):
    manifest = json.loads((output / "manifest.json").read_text())
    if (manifest["format"], manifest["base_commit"], manifest["snapshot_commit"],
            manifest["later_history_commit"]) != (1, BASE, SNAPSHOT, LATER):
        raise ValueError("Bundle references do not match the recorded non-chroot scope")
    snapshot, extra = manifest["snapshot_patches"], manifest["supplement_patches"]
    for phase, items in (("final12", snapshot), ("supplement", extra)):
        expected_series = "".join(Path(p["file"]).name + "\n" for p in items)
        if (output / phase / "series").read_text() != expected_series:
            raise ValueError(f"Unexpected patch order: {phase}/series")
    expected_series = "".join(p["file"] + "\n" for p in snapshot + extra)
    if (output / "series").read_text() != expected_series:
        raise ValueError("Unexpected combined patch order")
    checksums = "".join(f"{p['sha256']}  {p['file']}\n" for p in snapshot + extra)
    if (output / "SHA256SUMS").read_text() != checksums:
        raise ValueError("Checksum inventory differs from the manifest")
    paths = [p["path"] for item in snapshot for p in item["paths"]]
    expected = {p for _, p in git.changed(manifest["base_commit"], manifest["snapshot_commit"])}
    if len(paths) != len(set(paths)) or set(paths) != expected:
        raise ValueError("Snapshot patch coverage has gaps or overlapping paths")
    for item in snapshot + extra:
        if hashlib.sha256((output / item["file"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Patch hash mismatch: {item['file']}")
        for entry in item["paths"]:
            path = entry["path"].lower()
            if "/x7root/" in path or "/x7modebridge/" in path:
                raise ValueError(f"Container source leaked into bundle: {path}")
    git.run("read-tree", manifest["base_commit"])
    for label, items, target in (("final12", snapshot, manifest["snapshot_tree"]),
                                 ("supplement", extra, manifest["native_tree"])):
        for item in items:
            git.run("apply", "--cached", "--whitespace=nowarn", (output / item["file"]).resolve())
        actual = git.text("write-tree")
        if actual != target:
            raise ValueError(f"{label} tree mismatch: {actual} != {target}")
        print(f"PASS forward {label}: {actual}", flush=True)
    config = git.run("show", f"{manifest['native_tree']}:{KCONFIG}")
    base_config = git.run("show", f"{manifest['snapshot_commit']}:{KCONFIG}")
    if config != base_config.replace(b"CONFIG_VIDEO_SC035GS=y\n",
                                    b"CONFIG_VIDEO_SC035GS=y\nCONFIG_LEDS_CLASS_FLASH=y\n"
                                    b"CONFIG_LEDS_X7PRO_SCAN=y\n"):
        raise ValueError("Unexpected kernel config changes in supplement")
    overlay = git.run("show", f"{manifest['native_tree']}:{OVERLAY}")
    if b"modebridge" in overlay.lower() or b"ListenerAccess" in overlay:
        raise ValueError("Container notification access leaked into power overlay")
    for label, items, target in (("supplement", extra, manifest["snapshot_tree"]),
                                 ("final12", snapshot, git.text("rev-parse", manifest["base_commit"] + "^{tree}"))):
        for item in reversed(items):
            git.run("apply", "--cached", "--reverse", "--whitespace=nowarn",
                    (output / item["file"]).resolve())
        if git.text("write-tree") != target:
            raise ValueError(f"Reverse {label} did not reproduce its baseline")
        print(f"PASS reverse {label}: {target}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("export", "check"))
    parser.add_argument("--sdk", type=Path, default=SDK)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--git", dest="git_binary")
    args = parser.parse_args()
    git = Git(args.sdk, args.git_binary)
    with git.isolated():
        if args.action == "export":
            export(git, args.output)
        else:
            check(git, args.output)


if __name__ == "__main__":
    main()
