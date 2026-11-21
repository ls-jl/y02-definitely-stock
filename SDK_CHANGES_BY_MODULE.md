# X7 Pro 相对原始 SDK 的硬件相关更改路径

可直接应用和校验的代码已整理到
[非 chroot Android 补丁集](patches/android13/non-chroot/README.md)。
其中 `final12/` 完整覆盖原始 SDK 到下述目标的 398 个文件，`supplement/`
另外保存后续可独立使用的硬件、内存和显示修复；逐文件归属以
[PATHS.tsv](patches/android13/non-chroot/PATHS.tsv) 为准。

## 范围

- 基线：`2739aad12478b269998fbac4ea39f396f4695f9f`
- 目标：`1a2da0cd230e447abd85f1eaaa7e0b5e50fda036`（`ls-jl`）
- 不包含：`chroot-container` 后续的 x7root、X7ModeBridge、容器热切换及相关驱动
- 状态：`A` 新增，`M` 修改，`D` 删除

## Device（69）

```text
M  device/rockchip/common/build/rockchip/RebuildParameter.mk
M  device/rockchip/common/build/rockchip/build.sh
M  device/rockchip/common/modules/recovery.mk
M  device/rockchip/common/modules/rockchip_apps.mk
M  device/rockchip/common/rootdir/init.insmod.cfg
M  device/rockchip/common/rootdir/init.rk30board.usb.rc
M  device/rockchip/common/rootdir/ueventd.rockchip.rc
M  device/rockchip/rk3562/AndroidProducts.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/Android.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/AndroidBoard.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/BoardConfig.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/README.md
A  device/rockchip/rk3562/rk3562_x7pro_go/besbt.conf
A  device/rockchip/rk3562/rk3562_x7pro_go/bt_vendor.conf
A  device/rockchip/rk3562/rk3562_x7pro_go/config.cfg
A  device/rockchip/rk3562/rk3562_x7pro_go/config.cfg_ab
A  device/rockchip/rk3562/rk3562_x7pro_go/dt-overlay.in
A  device/rockchip/rk3562/rk3562_x7pro_go/init.x7pro.bluetooth.rc
A  device/rockchip/rk3562/rk3562_x7pro_go/media_profiles_default.xml
A  device/rockchip/rk3562/rk3562_x7pro_go/mkbootimg_x7pro.py
A  device/rockchip/rk3562/rk3562_x7pro_go/ota/loader/readme.txt
A  device/rockchip/rk3562/rk3562_x7pro_go/overlay/frameworks/base/packages/SettingsProvider/res/values/defaults.xml
A  device/rockchip/rk3562/rk3562_x7pro_go/parameter_ab.txt
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/dtb/rk3562-y02-saradc-ch2-228.dtb
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/aw883xx_acf.bin
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/bes2600_dpd.bin
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/bes2600_factory.txt
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/best2002_fw_boot_sdio.bin
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/best2002_fw_sdio.bin
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/best2002_fw_sdio_btrf.bin
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/firmware/best2002_fw_sdio_nosignal.bin
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/gc05a2_default_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/gc08a8_default_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/gc08a8_default_default_y03.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/gc8034_KYT-10203-v1_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/gc8034_RK-CMK-8M-2-v1_CK8401.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/ov13855_KYT-10203-v1_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/ov50c40_HZGA06_ZE0082C1.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/ov7251_default_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/sc035gs_default_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/sc035hgs_default_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/iqfiles/sc2356_default_default.json
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules.load
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/bes2600.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/dio4480.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/fake_keys.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/gc08a8.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/gs-da267.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/iqs323.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/sitronix-ts.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/snd-soc-aw883xx-v16.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/typec_aw35616.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/prebuilt/modules/usb_device_notify.ko
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall/Android.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall/README.txt
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall/preinstall.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall_del/Android.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall_del/README.txt
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall_del/preinstall.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall_del_forever/Android.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall_del_forever/README.txt
A  device/rockchip/rk3562/rk3562_x7pro_go/preinstall_del_forever/preinstall.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/recovery.fstab
A  device/rockchip/rk3562/rk3562_x7pro_go/recovery.fstab_AB
A  device/rockchip/rk3562/rk3562_x7pro_go/resolution_white.xml
A  device/rockchip/rk3562/rk3562_x7pro_go/rk3562_x7pro_go.mk
A  device/rockchip/rk3562/rk3562_x7pro_go/sepolicy/vendor/file_contexts
A  device/rockchip/rk3562/rk3562_x7pro_go/sepolicy/vendor/hal_wifi_default.te
A  device/rockchip/rk3562/rk3562_x7pro_go/sepolicy/vendor/hal_wifi_supplicant_default.te
```

## HAL 与驱动接口（13）

```text
M  frameworks/opt/net/wifi/libwifi_hal/Android.mk
M  frameworks/opt/net/wifi/libwifi_hal/rk_wifi_ctrl.cpp
M  frameworks/opt/net/wifi/libwifi_hal/wifi_hal_common.cpp
M  hardware/bes/bluetooth/libbt-vendor/src/Android.mk
M  hardware/bes/wireless/wlan/bes2600/wpa_supplicant_8_lib/Android.mk
M  hardware/interfaces/bluetooth/1.0/default/vendor_interface.cc
M  hardware/interfaces/wifi/1.6/default/wifi_legacy_hal.cpp
M  hardware/rockchip/audio/tinyalsa_hal/alsa_route.c
M  hardware/rockchip/audio/tinyalsa_hal/audio_hw.c
M  hardware/rockchip/camera/etc/camera/camera3_profiles_rk3562.xml
M  hardware/rockchip/camera/psl/rkisp2/RKISP2ControlUnit.cpp
M  hardware/rockchip/optee/init.tee-supplicant.rc
M  packages/modules/adb/daemon/usb_ffs.cpp
```

## Kernel：X7 专用驱动与配置（70）

```text
A  kernel-5.10/arch/arm64/boot/dts/rockchip/rk3562-y02-v10.dts
M  kernel-5.10/drivers/android/vendor_hooks.c
M  kernel-5.10/drivers/input/Kconfig
M  kernel-5.10/drivers/input/Makefile
M  kernel-5.10/drivers/input/sensors/accel/Kconfig
M  kernel-5.10/drivers/input/sensors/accel/da223_core.c
M  kernel-5.10/drivers/input/sensors/accel/da223_cust.c
M  kernel-5.10/drivers/input/touchscreen/Kconfig
M  kernel-5.10/drivers/input/touchscreen/Makefile
M  kernel-5.10/drivers/input/touchscreen/raydium_i2c_ts.c
A  kernel-5.10/drivers/input/touchscreen/x7_sitronix_77921.dump
A  kernel-5.10/drivers/input/touchscreen/x7_sitronix_77921_fw.S
A  kernel-5.10/drivers/input/touchscreen/x7_sitronix_ts_main.c
A  kernel-5.10/drivers/input/x7pro-tp-report.c
M  kernel-5.10/drivers/media/i2c/Kconfig
M  kernel-5.10/drivers/media/i2c/Makefile
A  kernel-5.10/drivers/media/i2c/gc08a8.c
M  kernel-5.10/drivers/media/i2c/sc035gs.c
M  kernel-5.10/drivers/mmc/core/core.c
M  kernel-5.10/drivers/mmc/core/host.c
M  kernel-5.10/drivers/mmc/core/mmc_test.c
M  kernel-5.10/drivers/power/supply/rk817_battery.c
M  kernel-5.10/drivers/usb/dwc3/Makefile
M  kernel-5.10/drivers/usb/dwc3/core.h
M  kernel-5.10/drivers/usb/dwc3/ep0.c
M  kernel-5.10/drivers/usb/dwc3/gadget.c
M  kernel-5.10/drivers/usb/dwc3/trace.h
A  kernel-5.10/drivers/usb/dwc3/x7regdump.c
M  kernel-5.10/drivers/usb/typec/Kconfig
M  kernel-5.10/drivers/usb/typec/Makefile
A  kernel-5.10/drivers/usb/typec/typec_aw35616.c
A  kernel-5.10/drivers/usb/typec/typec_aw35616.h
M  kernel-5.10/drivers/usb/typec/ucsi/ucsi.c
M  kernel-5.10/drivers/usb/typec/ucsi/ucsi.h
M  kernel-5.10/include/linux/mmc/host.h
M  kernel-5.10/include/linux/mmc/mmc.h
M  kernel-5.10/include/trace/hooks/dtask.h
A  kernel-5.10/kernel/configs/x7pro.config
M  kernel-5.10/kernel/locking/percpu-rwsem.c
M  kernel-5.10/net/rfkill/rfkill-wlan.c
M  kernel-5.10/sound/soc/codecs/Kconfig
M  kernel-5.10/sound/soc/codecs/Makefile
M  kernel-5.10/sound/soc/codecs/aw883xx/aw883xx.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/Kconfig
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/LICENSE
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/Makefile
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/README.md
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_bin_parse.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_bin_parse.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_calib.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_calib.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_data_type.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_device.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_device.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_init.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_log.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_monitor.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_monitor.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_pid_2049_init.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_pid_2049_reg.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_pid_2066_init.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_pid_2066_reg.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_pid_2183_init.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_pid_2183_reg.h
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_spin.c
A  kernel-5.10/sound/soc/codecs/aw883xx_v16/aw883xx_spin.h
M  kernel-5.10/sound/soc/codecs/cs42l51.c
M  kernel-5.10/sound/soc/codecs/wm8962.c
```

## Kernel：5.10.160 同步与核心改动（228）

```text
M  kernel-5.10/Makefile
M  kernel-5.10/arch/alpha/kernel/rtc.c
M  kernel-5.10/arch/arm/boot/dts/at91rm9200.dtsi
M  kernel-5.10/arch/arm/boot/dts/imx7s.dtsi
M  kernel-5.10/arch/arm/boot/dts/rk3036-evb.dts
M  kernel-5.10/arch/arm/boot/dts/rk3188-radxarock.dts
M  kernel-5.10/arch/arm/boot/dts/rk3188.dtsi
M  kernel-5.10/arch/arm/boot/dts/rk3288-evb-act8846.dts
M  kernel-5.10/arch/arm/boot/dts/rk3288-firefly.dtsi
M  kernel-5.10/arch/arm/boot/dts/rk3288-miqi.dts
M  kernel-5.10/arch/arm/boot/dts/rk3288-rock2-square.dts
M  kernel-5.10/arch/arm/boot/dts/rk3xxx.dtsi
M  kernel-5.10/arch/arm/include/asm/perf_event.h
M  kernel-5.10/arch/arm/include/asm/pgtable-nommu.h
M  kernel-5.10/arch/arm/include/asm/pgtable.h
M  kernel-5.10/arch/arm/mm/nommu.c
M  kernel-5.10/arch/arm64/Kconfig
M  kernel-5.10/arch/arm64/boot/dts/rockchip/Makefile
M  kernel-5.10/arch/arm64/boot/dts/rockchip/rk3308-roc-cc.dts
M  kernel-5.10/arch/arm64/boot/dts/rockchip/rk3399-rock-pi-4.dtsi
M  kernel-5.10/arch/arm64/configs/gki_defconfig
M  kernel-5.10/arch/arm64/configs/rockchip_gki.fragment
M  kernel-5.10/arch/arm64/include/asm/cache.h
M  kernel-5.10/arch/arm64/include/asm/mte-kasan.h
M  kernel-5.10/arch/arm64/include/asm/percpu.h
M  kernel-5.10/arch/csky/include/asm/processor.h
M  kernel-5.10/arch/microblaze/include/asm/page.h
M  kernel-5.10/arch/riscv/kernel/vdso/Makefile
M  kernel-5.10/arch/s390/kvm/vsie.c
M  kernel-5.10/arch/x86/configs/gki_defconfig
M  kernel-5.10/arch/x86/include/asm/cpufeatures.h
M  kernel-5.10/arch/x86/include/asm/nospec-branch.h
M  kernel-5.10/arch/x86/kernel/cpu/bugs.c
M  kernel-5.10/arch/x86/kernel/cpu/mtrr/mtrr.c
M  kernel-5.10/arch/x86/kernel/cpu/tsx.c
M  kernel-5.10/arch/x86/kernel/hpet.c
M  kernel-5.10/arch/x86/kernel/process.c
M  kernel-5.10/arch/x86/kernel/smpboot.c
M  kernel-5.10/arch/x86/power/cpu.c
M  kernel-5.10/block/partitions/core.c
M  kernel-5.10/build.config.allmodconfig
M  kernel-5.10/drivers/acpi/numa/hmat.c
M  kernel-5.10/drivers/base/power/trace.c
M  kernel-5.10/drivers/bluetooth/btusb.c
M  kernel-5.10/drivers/char/tpm/tpm-interface.c
M  kernel-5.10/drivers/clk/at91/at91rm9200.c
M  kernel-5.10/drivers/clocksource/timer-riscv.c
M  kernel-5.10/drivers/dma-buf/dma-buf-sysfs-stats.c
M  kernel-5.10/drivers/firmware/smccc/kvm_guest.c
M  kernel-5.10/drivers/gpio/gpio-amd8111.c
M  kernel-5.10/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.c
M  kernel-5.10/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c
M  kernel-5.10/drivers/gpu/drm/bridge/synopsys/dw-hdmi.c
M  kernel-5.10/drivers/gpu/drm/bridge/ti-sn65dsi86.c
M  kernel-5.10/drivers/gpu/drm/drm_dp_mst_topology.c
M  kernel-5.10/drivers/gpu/drm/drm_gem_shmem_helper.c
M  kernel-5.10/drivers/gpu/drm/i915/gt/intel_gt_requests.c
M  kernel-5.10/drivers/gpu/drm/panel/panel-simple.c
M  kernel-5.10/drivers/gpu/drm/rockchip/rockchip_drm_vop2.c
M  kernel-5.10/drivers/gpu/drm/vmwgfx/vmwgfx_scrn.c
M  kernel-5.10/drivers/hid/hid-core.c
M  kernel-5.10/drivers/hid/hid-ids.h
M  kernel-5.10/drivers/hid/hid-lg4ff.c
M  kernel-5.10/drivers/hid/hid-quirks.c
M  kernel-5.10/drivers/hwmon/coretemp.c
M  kernel-5.10/drivers/hwmon/i5500_temp.c
M  kernel-5.10/drivers/hwmon/ibmpex.c
M  kernel-5.10/drivers/hwmon/ina3221.c
M  kernel-5.10/drivers/hwmon/ltc2947-core.c
M  kernel-5.10/drivers/i2c/busses/i2c-imx.c
M  kernel-5.10/drivers/i2c/busses/i2c-npcm7xx.c
M  kernel-5.10/drivers/iio/health/afe4403.c
M  kernel-5.10/drivers/iio/health/afe4404.c
M  kernel-5.10/drivers/iio/light/Kconfig
M  kernel-5.10/drivers/iommu/intel/dmar.c
M  kernel-5.10/drivers/iommu/intel/iommu.c
M  kernel-5.10/drivers/media/common/videobuf2/videobuf2-core.c
M  kernel-5.10/drivers/media/v4l2-core/v4l2-dv-timings.c
M  kernel-5.10/drivers/mfd/rk808.c
M  kernel-5.10/drivers/mmc/host/dw_mmc.c
M  kernel-5.10/drivers/mmc/host/sdhci-esdhc-imx.c
M  kernel-5.10/drivers/mmc/host/sdhci-sprd.c
M  kernel-5.10/drivers/net/can/cc770/cc770_isa.c
M  kernel-5.10/drivers/net/can/sja1000/sja1000_isa.c
M  kernel-5.10/drivers/net/can/usb/esd_usb2.c
M  kernel-5.10/drivers/net/can/usb/mcba_usb.c
M  kernel-5.10/drivers/net/dsa/lan9303-core.c
M  kernel-5.10/drivers/net/dsa/sja1105/sja1105_devlink.c
M  kernel-5.10/drivers/net/ethernet/aeroflex/greth.c
M  kernel-5.10/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.c
M  kernel-5.10/drivers/net/ethernet/aquantia/atlantic/aq_main.c
M  kernel-5.10/drivers/net/ethernet/aquantia/atlantic/aq_main.h
M  kernel-5.10/drivers/net/ethernet/cavium/thunder/nicvf_main.c
M  kernel-5.10/drivers/net/ethernet/hisilicon/hisi_femac.c
M  kernel-5.10/drivers/net/ethernet/hisilicon/hix5hd2_gmac.c
M  kernel-5.10/drivers/net/ethernet/intel/e100.c
M  kernel-5.10/drivers/net/ethernet/intel/e1000e/netdev.c
M  kernel-5.10/drivers/net/ethernet/intel/fm10k/fm10k_main.c
M  kernel-5.10/drivers/net/ethernet/intel/i40e/i40e_ethtool.c
M  kernel-5.10/drivers/net/ethernet/intel/i40e/i40e_main.c
M  kernel-5.10/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.c
M  kernel-5.10/drivers/net/ethernet/intel/iavf/iavf_main.c
M  kernel-5.10/drivers/net/ethernet/intel/igb/igb_ethtool.c
M  kernel-5.10/drivers/net/ethernet/intel/ixgbevf/ixgbevf_main.c
M  kernel-5.10/drivers/net/ethernet/marvell/mvneta.c
M  kernel-5.10/drivers/net/ethernet/mellanox/mlx5/core/cmd.c
M  kernel-5.10/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c
M  kernel-5.10/drivers/net/ethernet/mellanox/mlx5/core/steering/dr_table.c
M  kernel-5.10/drivers/net/ethernet/microchip/encx24j600-regmap.c
M  kernel-5.10/drivers/net/ethernet/ni/nixge.c
M  kernel-5.10/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.c
M  kernel-5.10/drivers/net/ethernet/renesas/ravb_main.c
M  kernel-5.10/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c
M  kernel-5.10/drivers/net/ethernet/stmicro/stmmac/stmmac_main.c
M  kernel-5.10/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.c
M  kernel-5.10/drivers/net/ieee802154/ca8210.c
M  kernel-5.10/drivers/net/ieee802154/cc2520.c
M  kernel-5.10/drivers/net/macsec.c
M  kernel-5.10/drivers/net/ntb_netdev.c
M  kernel-5.10/drivers/net/phy/phy_device.c
M  kernel-5.10/drivers/net/plip/plip.c
M  kernel-5.10/drivers/net/tun.c
M  kernel-5.10/drivers/net/usb/qmi_wwan.c
M  kernel-5.10/drivers/net/vmxnet3/vmxnet3_drv.c
M  kernel-5.10/drivers/net/xen-netback/common.h
M  kernel-5.10/drivers/net/xen-netback/interface.c
M  kernel-5.10/drivers/net/xen-netback/netback.c
M  kernel-5.10/drivers/net/xen-netback/rx.c
M  kernel-5.10/drivers/net/xen-netfront.c
M  kernel-5.10/drivers/nvme/host/core.c
M  kernel-5.10/drivers/nvme/host/pci.c
M  kernel-5.10/drivers/of/property.c
M  kernel-5.10/drivers/pinctrl/intel/pinctrl-intel.c
M  kernel-5.10/drivers/pinctrl/mediatek/mtk-eint.c
M  kernel-5.10/drivers/pinctrl/pinctrl-single.c
M  kernel-5.10/drivers/regulator/slg51000-regulator.c
M  kernel-5.10/drivers/regulator/twl6030-regulator.c
M  kernel-5.10/drivers/rtc/rtc-cmos.c
M  kernel-5.10/drivers/rtc/rtc-mc146818-lib.c
M  kernel-5.10/drivers/spi/spi-imx.c
M  kernel-5.10/drivers/tty/n_gsm.c
M  kernel-5.10/drivers/usb/gadget/function/f_mass_storage.c
M  kernel-5.10/drivers/usb/gadget/function/f_uvc.c
M  kernel-5.10/drivers/video/fbdev/core/fbcon.c
M  kernel-5.10/fs/afs/fs_probe.c
M  kernel-5.10/fs/btrfs/backref.c
M  kernel-5.10/fs/btrfs/backref.h
M  kernel-5.10/fs/btrfs/ioctl.c
M  kernel-5.10/fs/btrfs/qgroup.c
M  kernel-5.10/fs/btrfs/send.c
M  kernel-5.10/fs/fuse/dir.c
M  kernel-5.10/fs/nfsd/vfs.c
M  kernel-5.10/fs/nilfs2/dat.c
M  kernel-5.10/fs/pstore/ram.c
M  kernel-5.10/fs/read_write.c
M  kernel-5.10/include/asm-generic/tlb.h
M  kernel-5.10/include/crypto/hash.h
M  kernel-5.10/include/linux/can/platform/sja1000.h
M  kernel-5.10/include/linux/cgroup.h
M  kernel-5.10/include/linux/clk-provider.h
M  kernel-5.10/include/linux/debug_locks.h
M  kernel-5.10/include/linux/fs.h
M  kernel-5.10/include/linux/hugetlb.h
M  kernel-5.10/include/linux/jump_label.h
A  kernel-5.10/include/linux/kasan-enabled.h
M  kernel-5.10/include/linux/kasan.h
M  kernel-5.10/include/linux/mc146818rtc.h
M  kernel-5.10/include/linux/printk.h
M  kernel-5.10/include/linux/slab.h
M  kernel-5.10/include/net/sctp/stream_sched.h
A  kernel-5.10/include/trace/hooks/dmabuf.h
M  kernel-5.10/ipc/sem.c
M  kernel-5.10/kernel/bpf/bpf_local_storage.c
M  kernel-5.10/kernel/bpf/bpf_lru_list.h
M  kernel-5.10/kernel/cgroup/cgroup-internal.h
M  kernel-5.10/kernel/events/core.c
M  kernel-5.10/kernel/trace/trace_dynevent.c
M  kernel-5.10/kernel/trace/trace_events.c
M  kernel-5.10/lib/Kconfig.debug
M  kernel-5.10/mm/frame_vector.c
M  kernel-5.10/mm/gup.c
M  kernel-5.10/mm/hugetlb.c
M  kernel-5.10/mm/khugepaged.c
M  kernel-5.10/mm/madvise.c
M  kernel-5.10/mm/memcontrol.c
M  kernel-5.10/mm/mmu_gather.c
M  kernel-5.10/mm/page_alloc.c
M  kernel-5.10/mm/slab.c
M  kernel-5.10/mm/slab_common.c
M  kernel-5.10/mm/slob.c
M  kernel-5.10/net/9p/trans_fd.c
M  kernel-5.10/net/9p/trans_xen.c
M  kernel-5.10/net/bluetooth/6lowpan.c
M  kernel-5.10/net/bluetooth/af_bluetooth.c
M  kernel-5.10/net/bluetooth/hci_core.c
M  kernel-5.10/net/can/af_can.c
M  kernel-5.10/net/dsa/tag_ksz.c
M  kernel-5.10/net/hsr/hsr_forward.c
M  kernel-5.10/net/ipv4/fib_frontend.c
M  kernel-5.10/net/ipv4/fib_semantics.c
M  kernel-5.10/net/ipv4/ip_gre.c
M  kernel-5.10/net/ipv6/ip6_output.c
M  kernel-5.10/net/mac80211/airtime.c
M  kernel-5.10/net/mac802154/iface.c
M  kernel-5.10/net/netfilter/nf_conntrack_netlink.c
M  kernel-5.10/net/netfilter/nft_set_pipapo.c
M  kernel-5.10/net/nfc/nci/ntf.c
M  kernel-5.10/net/packet/af_packet.c
M  kernel-5.10/net/sctp/stream.c
M  kernel-5.10/net/sctp/stream_sched.c
M  kernel-5.10/net/sctp/stream_sched_prio.c
M  kernel-5.10/net/sctp/stream_sched_rr.c
M  kernel-5.10/net/tipc/crypto.c
M  kernel-5.10/net/tipc/link.c
M  kernel-5.10/net/tipc/node.c
M  kernel-5.10/net/unix/diag.c
M  kernel-5.10/net/wireless/scan.c
M  kernel-5.10/scripts/faddr2line
M  kernel-5.10/sound/core/seq/seq_memory.c
M  kernel-5.10/sound/soc/fsl/fsl_micfil.c
M  kernel-5.10/sound/soc/soc-ops.c
M  kernel-5.10/sound/soc/soc-pcm.c
M  kernel-5.10/tools/lib/bpf/libbpf_probes.c
M  kernel-5.10/tools/lib/bpf/ringbuf.c
M  kernel-5.10/tools/testing/selftests/net/fib_nexthops.sh
M  kernel-5.10/tools/testing/selftests/net/fib_tests.sh
M  kernel-5.10/tools/testing/selftests/net/rtnetlink.sh
M  kernel-5.10/tools/vm/slabinfo-gnuplot.sh
```

## Android 平台接口（12）

```text
M  frameworks/av/services/mediacodec/seccomp_policy/mediacodec-arm.policy
M  frameworks/av/services/mediacodec/seccomp_policy/mediacodec-arm64.policy
M  frameworks/base/services/core/java/com/android/server/PersistentDataBlockService.java
M  frameworks/base/services/core/java/com/android/server/wm/ActivityTaskManagerService.java
M  packages/apps/Camera2/src/com/android/camera/CameraActivity.java
M  packages/apps/Settings/res/values-zh-rCN/strings.xml
M  packages/apps/Settings/res/values/strings.xml
M  packages/apps/Settings/res/xml/process_stats_summary.xml
M  packages/apps/Settings/src/com/android/settings/applications/ProcessStatsBase.java
M  packages/apps/Settings/src/com/android/settings/applications/ProcessStatsSummary.java
M  packages/apps/Settings/src/com/android/settings/development/OemUnlockPreferenceController.java
M  system/core/fs_mgr/fs_mgr_slotselect.cpp
```

## 构建工具与其他接口（6）

以下路径补齐本清单原先未列出的构建、仓库指引及 vendor seccomp 改动。

```text
A  AGENTS.md
M  build.sh
M  javaenv.sh
M  rkbin/.gitignore
D  rkbin/tools/config.ini
M  vendor/rockchip/hardware/interfaces/rockit/hw/hidl/services/seccomp_policy/rockit.vendor.base-arm.policy
```

## 复核命令

```bash
"$GIT" -C "$SDK" diff --name-status 2739aad12478..ls-jl
python3 tools/porting/non_chroot.py check --sdk /path/to/RK3562_Android13.0_SDK
```
