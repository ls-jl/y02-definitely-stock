# X7 Pro Android 13 Go：非 chroot 代码集

这是一套可重建、可校验的代码补丁。目录以功能模块组织，没有改动 SDK 当前的
`chroot-container` 工作树，也没有改写原有分支。

## 固定基线

- 原始 Android SDK：`2739aad12478b269998fbac4ea39f396f4695f9f`。
- 非 chroot final12：`1a2da0cd230e447abd85f1eaaa7e0b5e50fda036`（`ls-jl`）。
- final12 完整源码树：`173736490a35b8d299094860e9d509dbf37da2eb`。
- 后续修复的来源上限：`2f8600284e4f869435f1b3689fb79ab9f55a8aee`。
- 加入精选修复后的源码树：`8ebc2d72225ea10e0363f826e7d32d64dd3b6420`。

最后一个是校验时生成的合成 tree ID，不是已有分支或提交。

## final12：13 个模块，398 个文件

| 补丁 | 文件数 | 范围 |
| --- | ---: | --- |
| `0001-host-build` | 5 | 构建入口、Java 环境、仓库指引与 rkbin 配置 |
| `0002-product` | 62 | X7 Pro 产品、FIT 打包、配置、模块/固件/IQ 资产 |
| `0003-rockchip-common` | 7 | 共享 init、权限、恢复环境与构建集成 |
| `0004-kernel-stable-abi` | 228 | 5.10.160 对齐、核心兼容和其他稳定版差异 |
| `0005-kernel-board` | 3 | DTS、DTB 构建列表和内核配置片段 |
| `0006-kernel-display-input` | 14 | 显示、触摸和传感器 |
| `0007-kernel-camera` | 4 | 摄像头传感器 |
| `0008-kernel-audio` | 30 | Codec 和 AW883xx 功放 |
| `0009-kernel-usb-radio-power` | 19 | DWC3、Type-C、SDIO、rfkill、电池 |
| `0010-hal-connectivity` | 7 | BES Wi-Fi/蓝牙 HAL 与构建接口 |
| `0011-hal-media` | 5 | Rockchip 音频、摄像头与 TEE 服务 |
| `0012-framework-storage-adb` | 7 | Framework、A/B、ADB 与 seccomp |
| `0013-settings-camera` | 7 | Settings 内存页面、解锁入口和 Camera2 |

每个文件只属于一个模块；`final12/series` 记录应用顺序。
[PATHS.tsv](PATHS.tsv) 提供逐文件的状态和模块，[manifest.json](manifest.json)
保存树 ID、来源和补丁 SHA-256。二进制资产保留为 Git binary patch，不另存一套固件副本。

## supplement：后续独立修复

按 `supplement/series` 应用在 final12 上：

1. `0001-touch-led-rga`：触摸轮询恢复、白光/红外 LED class 驱动、RGA DMA 地址修复。
   内核配置只增加两项 LED 开关。没有导入 namespace/cgroup 配置，亦未导入
   原厂 CaptureFrame 专用 `RKMODULE_SET_QUICK_STREAM_ONLY` ioctl。
2. `0002-camera-pipeline-flash`：双摄 media-controller 路由、帧处理等待和 Android 闪光灯接口。
3. `0003-python3-fileslist`：将文件清单工具更新为 Python 3 语法。
4. `0004-settings-realtime-memory`：Go 设备开发者选项采用实时内存数据，包含原有 Robolectric 测试改动。
5. `0005-display-face-down-gesture`：只提取关闭手机式翻转息屏的资源开关；
   没有导入原文件中的 ModeBridge 通知监听授权。

其余后续改动列在 [EXCLUDED.tsv](EXCLUDED.tsv)，包括 x7root、X7ModeBridge、
Home+Power 切换、HWC/SurfaceFlinger 交接、容器 SELinux 和通知桥。
该清单按文件列出“完全未选入”的后续差异；上述混合文件的局部取舍以 manifest 的 provenance 为准。

## 验证与使用

从本仓库根目录运行，另行指定含固定提交的本地 SDK：

```bash
python3 tools/porting/non_chroot.py check --sdk /path/to/RK3562_Android13.0_SDK
python3 -m unittest discover -s tools/porting/tests -v
```

校验使用临时 index 和临时对象目录，依次验证：原 SDK → final12 → 精选修复树，
再反向还原至原 SDK。验证的是整个源码树 ID，涵盖二进制内容、删除文件和可执行权限；
不会切换 SDK 分支或更改其 index、工作树和对象库。

要在另一个**干净、HEAD 为上述原始 SDK 提交**的工作目录中应用完整代码集：

```bash
PATCH_DIR=/absolute/path/to/y02-definitely-stock/patches/android13/non-chroot
while IFS= read -r patch; do
    git apply --index --binary "$PATCH_DIR/$patch" || break
done < "$PATCH_DIR/series"
```

`series` 包含 final12 和 supplement。若只需要历史 final12，使用 `final12/series`
并将补丁前缀改为 `$PATCH_DIR/final12/`。应用后仍沿用
`lunch rk3562_x7pro_go-userdebug` 和 SDK 的构建入口。

本次完成补丁双向重建与工具测试，没有重新编译或刷机。精选补丁虽来自已有硬件修复，
剥离容器后的这一组合仍需单独做 Android 构建及硬件回归。

本地原工程另有基于 `rockchip-5.10.160-d0782c9411db` 参考树的内核补丁，
适用于不含 RK3562 BSP 的另一种基线。它没有重复发布到本仓库，亦不是本系列的前置依赖。
