# Repository Guidelines

## Project Structure & Module Organization

This is a Rockchip Android 13/AOSP tree. Android framework and application code
lives under `frameworks/`, `packages/`, `system/`, and `hardware/`. Rockchip
board configuration is under `device/rockchip/`; X7 Pro work belongs in
`device/rockchip/rk3562/rk3562_x7pro_go/`. The vendor kernel is in
`kernel-5.10/`, with the X7 Pro DTS at
`arch/arm64/boot/dts/rockchip/rk3562-y02-v10.dts` and its config fragment at
`kernel/configs/x7pro.config`. Generated Android files go to `out/`; the current
out-of-tree kernel build is in `../kernel_out_x7pro/`. Device dumps and reference
sources under `../../device_dump_*` and `../../reference_sources/` are inputs,
not repository source.

## Build, Test, and Development Commands

Run commands from the repository root:

```bash
source build/envsetup.sh
export PATH="$PWD/tools/x7pro-host:$PATH"
lunch rk3562_x7pro_go-userdebug
./build.sh -C -J16          # kernel with the SDK Clang toolchain
./build.sh -A -J16          # Android userspace
./build.sh -C -A -p -J16    # kernel, Android, and packaged images
m <module>                  # rebuild one Android module
atest <test-name>           # run a supported host/device test
```

Before Android builds, ensure `build.sh` uses
`prebuilts/jdk/jdk11/linux-x86`; do not rely on a host Java installation.
After moving the tree, regenerate stale output directories rather than editing
generated absolute paths.

## Coding Style & Naming Conventions

Follow the nearest subsystem style. Use four spaces for Java/Kotlin and Android
make/config files; kernel C and DTS follow Linux kernel tab conventions. Keep
product names lowercase with underscores (`rk3562_x7pro_go`) and DTS names
lowercase with hyphens (`rk3562-y02-v10.dts`). Run the subsystem's existing
`clang-format`, lint, or checkpatch tooling when present; avoid formatting
unrelated code.

## Testing Guidelines

At minimum, verify `lunch` resolves, the kernel builds, `kernelrelease` is
`5.10.160`, and module vermagic is `5.10.160 SMP mod_unload aarch64`. Compare the
built DTB byte-for-byte with the captured device DTB. For framework changes,
run focused `atest` targets and report the exact command and result. Run
`../../tools/verify_kernel_delta.py` after changing the kernel delta set.

## Commit & Pull Request Guidelines

History contains only an initial import, so use concise imperative subjects with
a scope, for example `kernel: add X7 Pro module ABI config`. Keep generated
outputs, firmware dumps, keys, and reference archives out of commits. PRs should
describe hardware impact, list tested build targets, include logs or hashes, and
call out untested device behavior.

## Safety & Agent Instructions

Do not add remotes, push changes, flash partitions, or alter device data unless
explicitly requested. Preserve local user changes and keep reference-source
comparisons separate from production patches.
