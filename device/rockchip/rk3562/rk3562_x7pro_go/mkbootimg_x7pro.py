#!/usr/bin/env python3
"""Translate Android mkbootimg arguments into the X7 Pro's stock FIT format."""

import gzip
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


VALUE_OPTIONS = {
    "--kernel", "--ramdisk", "--dtb", "--output", "--second",
    "--cmdline", "--recovery_dtbo", "--os_version", "--os_patch_level",
    "--header_version", "--base", "--pagesize", "--kernel_offset",
    "--ramdisk_offset", "--second_offset", "--tags_offset", "--dtb_offset",
    "--board",
}
RAMDISK_LOAD_ADDR = 0x02800000


def parse_args(argv):
    values = {}
    index = 0
    while index < len(argv):
        option = argv[index]
        if option in VALUE_OPTIONS:
            if index + 1 >= len(argv):
                raise SystemExit(f"missing value for {option}")
            values[option] = argv[index + 1]
            index += 2
        else:
            raise SystemExit(f"unsupported mkbootimg argument: {option}")
    for required in ("--kernel", "--ramdisk", "--dtb", "--output"):
        if required not in values:
            raise SystemExit(f"missing required argument: {required}")
    return values


def patch_dtb_bootargs(dtc, source, destination, extra_bootargs,
                       initrd_start, initrd_end):
    """Round-trip a DTB and append boot arguments/initrd bounds to /chosen."""
    dts = destination.with_suffix(".dts")
    subprocess.run([
        str(dtc), "-q", "-I", "dtb", "-O", "dts", "-o", str(dts), str(source),
    ], check=True)
    text = dts.read_text()
    vop_start = text.find("\tvop@ff400000 {")
    vop_end = text.find("\n\tiommu@ff407e00 {", vop_start)
    if vop_start < 0 or vop_end < 0:
        raise SystemExit(f"DTB has no RK3562 VOP block: {source}")
    vop = text[vop_start:vop_end]
    vop = re.sub(
        r"(?m)^\s*rockchip,(?:plane-mask|primary-plane)\s*=\s*<[^>]+>\s*;\n?",
        "",
        vop,
    )
    port = re.search(r"(?m)^(\s*)port@0\s*\{", vop)
    if not port:
        raise SystemExit(f"RK3562 VOP has no port@0: {source}")
    plane_properties = (
        f"\n{port.group(1)}\trockchip,plane-mask = <0x30c>;"
        f"\n{port.group(1)}\trockchip,primary-plane = <0x2>;"
    )
    vop = vop[:port.end()] + plane_properties + vop[port.end():]
    text = text[:vop_start] + vop + text[vop_end:]
    if os.environ.get("X7PRO_FORCE_USB_PERIPHERAL") == "1":
        usb = re.search(
            r"(?ms)^\s*usb@fe500000\s*\{.*?^\s*\};",
            text,
        )
        if not usb:
            raise SystemExit(f"DTB has no RK3562 DWC3 block: {source}")
        block, count = re.subn(
            r'dr_mode\s*=\s*"otg"\s*;',
            'dr_mode = "peripheral";',
            usb.group(0),
            count=1,
        )
        if count != 1:
            raise SystemExit(f"RK3562 DWC3 is not in OTG mode: {source}")
        text = text[:usb.start()] + block + text[usb.end():]
    if os.environ.get("X7PRO_FORCE_USB_FULL_SPEED") == "1":
        usb = re.search(
            r"(?ms)^\s*usb@fe500000\s*\{.*?^\s*\};",
            text,
        )
        if not usb:
            raise SystemExit(f"DTB has no RK3562 DWC3 block: {source}")
        block, count = re.subn(
            r'maximum-speed\s*=\s*"high-speed"\s*;',
            'maximum-speed = "full-speed";',
            usb.group(0),
            count=1,
        )
        if count != 1:
            raise SystemExit(f"RK3562 DWC3 is not in high-speed mode: {source}")
        text = text[:usb.start()] + block + text[usb.end():]
    chosen = re.search(r"(?ms)^\s*chosen\s*\{.*?^\s*\};", text)
    if not chosen:
        raise SystemExit(f"DTB has no /chosen node: {source}")
    block = chosen.group(0)
    match = re.search(r'bootargs\s*=\s*"((?:\\.|[^"\\])*)"\s*;', block)
    if not match:
        raise SystemExit(f"DTB /chosen has no bootargs property: {source}")
    escaped = extra_bootargs.replace("\\", "\\\\").replace('"', '\\"')
    current = match.group(1).strip()
    merged = f"{current} {escaped}".strip()
    block = block[:match.start(1)] + merged + block[match.end(1):]
    block = re.sub(
        r"(?m)^\s*linux,initrd-(?:start|end)\s*=\s*<[^>]+>\s*;\n?",
        "",
        block,
    )
    closing = block.rfind("\n")
    if closing < 0:
        raise SystemExit(f"malformed /chosen node: {source}")
    properties = (
        f"\n\t\tlinux,initrd-start = <0x0 0x{initrd_start:x}>;"
        f"\n\t\tlinux,initrd-end = <0x0 0x{initrd_end:x}>;"
    )
    block = block[:closing] + properties + block[closing:]
    text = text[:chosen.start()] + block + text[chosen.end():]
    dts.write_text(text)
    subprocess.run([
        str(dtc), "-q", "-I", "dts", "-O", "dtb", "-o", str(destination), str(dts),
    ], check=True)
    dts.unlink()


def main():
    args = parse_args(sys.argv[1:])
    top = Path(os.environ.get("ANDROID_BUILD_TOP", Path.cwd())).resolve()
    x7pro_root = top.parents[1]
    builder = x7pro_root / "tools/fit/make_android_fit.py"
    fallback = Path(__file__).resolve().parent / "prebuilt/dtb/rk3562-y02-saradc-ch2-228.dtb"
    # Rockchip's kernel DTC accepts the stock '#_saradc_*' FIT node names;
    # the newer AOSP host DTC rejects '#', although stock U-Boot requires this
    # naming convention for its ADC-selected FDT list.
    dtc = x7pro_root / "android13_sdk/kernel_out_x7pro/scripts/dtc/dtc"
    for path in (builder, fallback, dtc):
        if not path.is_file():
            raise SystemExit(f"missing X7 Pro FIT dependency: {path}")

    output = Path(args["--output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    mode = os.environ.get("X7PRO_FIT_MODE", "normal")
    slot_suffix = os.environ.get("X7PRO_SLOT_SUFFIX", "_a")
    if mode not in ("normal", "recovery"):
        raise SystemExit(f"invalid X7PRO_FIT_MODE: {mode}")
    if slot_suffix not in ("_a", "_b"):
        raise SystemExit(f"invalid X7PRO_SLOT_SUFFIX: {slot_suffix}")
    bootargs = args.get("--cmdline", "").strip()
    bootargs = f"{bootargs} androidboot.slot_suffix={slot_suffix}".strip()
    if mode == "normal":
        bootargs += " androidboot.force_normal_boot=1"

    with tempfile.TemporaryDirectory(prefix="x7pro-fit-", dir=output.parent) as temp_dir:
        temp_dir = Path(temp_dir)
        compression = os.environ.get("X7PRO_KERNEL_COMPRESSION", "none")
        if compression not in ("none", "gzip"):
            raise SystemExit(f"invalid X7PRO_KERNEL_COMPRESSION: {compression}")
        kernel_input = Path(args["--kernel"])
        if compression == "gzip":
            kernel_input = temp_dir / "Image.gz"
            with kernel_input.open("wb") as temporary, open(args["--kernel"], "rb") as source:
                with gzip.GzipFile(filename="", mode="wb", compresslevel=9,
                                   mtime=0, fileobj=temporary) as archive:
                    archive.write(source.read())
        main_dtb = temp_dir / "main.dtb"
        fallback_dtb = temp_dir / "fallback-228.dtb"
        ramdisk_size = Path(args["--ramdisk"]).stat().st_size
        initrd_end = RAMDISK_LOAD_ADDR + ramdisk_size
        patch_dtb_bootargs(
            dtc, Path(args["--dtb"]), main_dtb, bootargs,
            RAMDISK_LOAD_ADDR, initrd_end,
        )
        patch_dtb_bootargs(
            dtc, fallback, fallback_dtb, bootargs,
            RAMDISK_LOAD_ADDR, initrd_end,
        )
        subprocess.run([
            str(builder), "--kernel", str(kernel_input), "--compression", compression,
            "--dtb", str(main_dtb), "--dtb-228", str(fallback_dtb),
            "--dtb-342", str(main_dtb), "--ramdisk", args["--ramdisk"],
            "--dtc", str(dtc), "--output", str(output), "--max-size",
            os.environ.get("X7PRO_FIT_MAX_SIZE", str(64 * 1024 * 1024)),
        ], check=True)


if __name__ == "__main__":
    main()
