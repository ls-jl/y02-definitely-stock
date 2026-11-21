# y02-definitely-stock

Android 只是借住，原厂系统你别多想。

有道 X7 Pro（Y02 / RK3562）的 Android 13 Go 源码和设备适配工程。
以 Rockchip SDK 和 final12 为基础，包含触摸、双摄、扫描灯、音频、Wi-Fi/蓝牙、
实时内存显示与息屏行为修复。

## 仓库内容

- `frameworks/`、`packages/`、`system/`、`hardware/`：Android 平台和 HAL 源码。
- `kernel-5.10/`：Linux 5.10.160 和 Y02 板级驱动。
- `device/rockchip/rk3562/rk3562_x7pro_go/`：产品配置、设备树打包、固件与相机 IQ。
- [补丁集说明](patches/android13/y02/README.md)：13 个 final12 模块补丁，
  覆盖 398 个文件；另有 5 组触摸/扫描灯/RGA、双摄、Python 3、内存显示和息屏修复。
- [PATHS.tsv](patches/android13/y02/PATHS.tsv)：逐文件归属和修改状态。
- [manifest.json](patches/android13/y02/manifest.json)：基线、来源和补丁校验值。
- [SDK 改动清单](SDK_CHANGES_BY_MODULE.md)：按硬件和平台模块整理的源码路径。
- [导出与验证工具](tools/porting/README.md)：可复现导出和完整源码树双向校验。
- [原厂 ADB 自启动脚本](tools/stock_adb/README.md)：原厂 Buildroot 系统的独立辅助工具。

工具链、预编译依赖和大体积二进制单独存放在本私有仓库的 Release 资产中，
通过 `tools/porting/sdk_assets.py` 按校验清单恢复。源码使用普通 Git，不启用 Git LFS。
原厂分区备份和构建输出不属于源码树。

## 准备源码与构建依赖

```bash
gh repo clone ls-jl/y02-definitely-stock
cd y02-definitely-stock
python3 tools/porting/sdk_assets.py fetch
source build/envsetup.sh
lunch rk3562_x7pro_go-userdebug
```

恢复依赖需要 Python 3.12+、`gh` 和 `zstd`，并需留出下载及解包空间。
当前发布主机因磁盘空间有限采用稀疏检出；若使用的也是稀疏工作目录，先执行
`git sparse-checkout disable` 展开全部源码，再恢复依赖。正常的新克隆无需这一步。

## 验证

只校验补丁文件：

```bash
cd patches/android13/y02
sha256sum -c SHA256SUMS
```

工具测试无需 Android SDK：

```bash
python3 -m unittest discover -s tools/porting/tests -v
```

完整正向/反向 tree ID 校验需要另行准备含 manifest 中固定提交的 SDK Git 仓库：

```bash
python3 tools/porting/sdk_port.py check --sdk /path/to/original-sdk-git
```

校验过程使用临时 Git index 和对象目录。补丁顺序、基线要求与应用方法见补丁集说明。
本次源码导入验证文件内容和来源，不替代 Android 构建与实机硬件回归。
