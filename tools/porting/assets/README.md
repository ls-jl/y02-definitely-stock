# SDK 构建依赖清单

`source.json` 记录完整 SDK 快照、文件数和存储划分；`manifest.json` 记录同一私有仓库
Release 中各分卷的大小、SHA-256 和 asset ID。分卷拼接后是一条 zstd 压缩的 tar 数据流。

`files.tsv.zst` 是依赖逐文件清单，解压后每行四列：Git mode、Git blob ID、原始字节数、
JSON 编码的仓库相对路径。恢复工具既检查分卷 SHA-256，也逐文件检查 Git blob ID，
保留可执行权限和符号链接。

快照共 1,047,381 个文件：804,253 个源码及常规资源进入 Git，243,127 个预编译依赖、
工具链及大文件存放于 Release。另一个文件是原 SDK 的 `.gitignore`，原样保存在
`original-sdk.gitignore`，根目录改用本仓库的构建输出和依赖缓存规则。
构建产物和设备分区备份不在此清单中。

```bash
python3 tools/porting/sdk_assets.py fetch
```

该命令使用当前 `gh` 登录账号读取私有 Release，不需要 Git LFS。
已有且内容不同的本地依赖不会被覆盖；下载缓存位于 `.git/sdk-assets/`。
完整依赖约 55.8 GiB，还需为压缩下载、源码展开及编译输出留足空间。
