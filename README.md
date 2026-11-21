# X7 Pro Android 13 Go：非 chroot 移植代码

有道 X7 Pro（RK3562）的 Android 13 Go 移植补丁与配套源码工具。
以原始 Rockchip SDK 为基线，包含 final12 的完整改动，以及剥离容器依赖的后续独立修复。

## 仓库内容

- [补丁集说明](patches/android13/non-chroot/README.md)：13 个 final12 模块补丁，
  覆盖 398 个文件；另有 5 组触摸/扫描灯/RGA、双摄、Python 3、内存显示和息屏修复。
- [PATHS.tsv](patches/android13/non-chroot/PATHS.tsv)：逐文件归属和修改状态。
- [manifest.json](patches/android13/non-chroot/manifest.json)：基线、来源和补丁校验值。
- [SDK 改动清单](SDK_CHANGES_BY_MODULE.md)：按硬件和平台模块整理的源码路径。
- [导出与验证工具](tools/porting/README.md)：可复现导出和完整源码树双向校验。
- [原厂 ADB 自启动脚本](tools/stock_adb/README.md)：原厂 Buildroot 系统的独立辅助工具。

SDK 全量源码、原厂刷机镜像、设备分区备份和构建输出由本地另行保存。
补丁中的模块、固件与 IQ 资产属于已记录的 Android 产品改动，使用 Git binary patch 保存。
本仓库不包含 x7root、X7ModeBridge、容器显示交接或通知桥实现。

## 验证

只校验补丁文件：

```bash
cd patches/android13/non-chroot
sha256sum -c SHA256SUMS
```

工具测试无需 Android SDK：

```bash
python3 -m unittest discover -s tools/porting/tests -v
```

完整正向/反向 tree ID 校验需要另行准备含 manifest 中固定提交的 SDK Git 仓库：

```bash
python3 tools/porting/non_chroot.py check --sdk /path/to/RK3562_Android13.0_SDK
```

校验过程使用临时 Git index 和对象目录。补丁顺序、基线要求与应用方法见补丁集说明。
补充修复剥离容器后的组合尚需独立 Android 构建和实机回归，仓库发布不代表新增硬件验证。
