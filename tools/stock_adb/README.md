# 原厂系统 ADB 自启动

`skip_login.sh` 用于原厂 Buildroot 用户态。原厂
`/etc/init.d/S99_run_test_scripts` 会在开机时执行
`/userdisk/skip_re/skip_login.sh`。

脚本保持 MTP 和 USB ADB 开启，并创建 `/tmp/.adb_auth_verified`，
让原厂 `adbd_auth.sh` 跳过 shell 密码提示。日志保存到
`/userdata/applog/adb-autostart.log`，不修改只读 rootfs。

先取得设备的 root ADB，再从本仓库根目录安装：

```bash
SERIAL=YOUR_DEVICE_SERIAL
adb -s "$SERIAL" shell 'mkdir -p /userdisk/skip_re'
adb -s "$SERIAL" push tools/stock_adb/skip_login.sh /userdisk/skip_re/skip_login.sh
adb -s "$SERIAL" shell 'chmod 0755 /userdisk/skip_re/skip_login.sh; chown 0:0 /userdisk/skip_re/skip_login.sh; sync'
```

此脚本已在 X7 Pro 原厂系统上经过重启测试。恢复出厂或清空 userdisk 后需要重新安装。
它是原厂系统辅助工具，不属于 Android SDK 补丁系列。
