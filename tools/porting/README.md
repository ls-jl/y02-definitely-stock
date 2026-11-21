# 非 chroot 代码整理工具

`non_chroot.py` 从 SDK 的固定提交导出模块补丁，避免把当前工作分支的容器代码一起拷走。
默认 SDK 路径为 `android13_sdk/RK3562_Android13.0_SDK`，默认输出为
`patches/android13/non-chroot/`。SDK 不随本仓库发布；从仓库根目录执行时用 `--sdk` 指定：

```bash
python3 tools/porting/non_chroot.py export --sdk /path/to/RK3562_Android13.0_SDK
python3 tools/porting/non_chroot.py check --sdk /path/to/RK3562_Android13.0_SDK
python3 -m unittest discover -s tools/porting/tests -v
```

可用 `--sdk`、`--output` 和 `--git` 指定其他本地路径。请安装系统 Git 或用 `--git`
传入可执行文件路径。整个导出/校验流程不访问远端、不创建提交、不切换分支。

导出规则在 `MODULES` / `classify()` 中；未分类的 SDK 改动会直接报错。
`supplement()` 明确列出后续修复的提交来源与混合文件取舍。
生成的 `series`、SHA-256、文件索引和 manifest 由代码统一产生。
再次导出时只接受字节相同的已有文件；如果已有补丁被编辑，工具会拒绝覆盖。
需要维护新版本时，应先复核固定提交和选取规则，再输出到新的目录。

`check` 使用隔离的 Git index 和对象目录，验证正向、反向完整 tree ID、
二进制补丁、应用顺序、398 个文件的无重叠覆盖，以及容器配置是否误入补充集。
单元测试额外覆盖二进制与文件权限往返、SDK 状态隔离及已有文件覆盖保护。

原厂 Buildroot 系统上的 ADB 自启动属于另一类工具，保留在
`tools/stock_adb/skip_login.sh`，不混入 Android SDK 补丁。
