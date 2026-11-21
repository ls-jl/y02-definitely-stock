#
# Copyright 2014 The Android Open-Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# First lunching is T, api_level is 33
PRODUCT_SHIPPING_API_LEVEL := 33

# Keep fingerprints identical across partial boot/super rebuilds.  Android
# shows an "internal problem" dialog when system/vendor timestamps diverge.
ROCKCHIP_BUILD_NUMBER := X7PRO_A13_20260825

# The stock X7 Pro kernel modules carry no symbol versions, so the kernel
# keeps CONFIG_MODVERSIONS off; the FCM level 7 kernel config requirements
# (which mandate MODVERSIONS) cannot be enforced for this port.
PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false
PRODUCT_DTBO_TEMPLATE := $(LOCAL_PATH)/dt-overlay.in
PRODUCT_SDMMC_DEVICE := ff880000.mmc

include device/rockchip/common/build/rockchip/DynamicPartitions.mk
include device/rockchip/rk3562/rk3562_x7pro_go/BoardConfig.mk
include device/rockchip/common/BoardConfig.mk

# common/wifi_bt_common.mk forces BOARD_WLAN_DEVICE := auto and the Rockchip
# "auto" driver-command libs; re-point them at the BES2600 libraries.
# It also enables the BCM/RTK/AIC BT stacks, which clash with the BES ones
# (duplicate libbt-codec module), so leave BES as the only BT vendor.
BOARD_WLAN_DEVICE := bes2600
BOARD_WPA_SUPPLICANT_PRIVATE_LIB := lib_driver_cmd_bes2600
BOARD_HOSTAPD_PRIVATE_LIB := lib_driver_cmd_bes2600
BOARD_HAVE_BLUETOOTH_BCM := false
BOARD_HAVE_BLUETOOTH_RTK := false
BOARD_HAVE_BLUETOOTH_AIC := false

# Do not let the generic Rockchip app list add persistent factory stress and
# device-test packages to this 1 GiB end-user Android Go product.
ROCKCHIP_EXCLUDE_FACTORY_APPS := true
$(call inherit-product, device/rockchip/rk3562/device.mk)
$(call inherit-product, device/rockchip/common/device.mk)

# common/device.mk includes wifi_bt_common.mk and resets these to the Rockchip
# auto/bcmdhd defaults.  The final product values must be applied afterwards.
BOARD_WLAN_DEVICE := bes2600
BOARD_WPA_SUPPLICANT_PRIVATE_LIB := lib_driver_cmd_bes2600
BOARD_HOSTAPD_PRIVATE_LIB := lib_driver_cmd_bes2600
BOARD_HAVE_BLUETOOTH_BCM := false
BOARD_HAVE_BLUETOOTH_RTK := false
BOARD_HAVE_BLUETOOTH_AIC := false

# The stock GPT has no standalone DTBO/VBMeta partitions and keeps its
# bootloader/trust slots unchanged. OTA updates cover the custom FIT boot slot
# and the logical partitions inside super only.
AB_OTA_PARTITIONS := \
    boot \
    system \
    system_dlkm \
    system_ext \
    vendor \
    vendor_dlkm \
    odm \
    odm_dlkm \
    product

DEVICE_PACKAGE_OVERLAYS += $(LOCAL_PATH)/overlay

PRODUCT_CHARACTERISTICS := tablet

PRODUCT_NAME := rk3562_x7pro_go
PRODUCT_DEVICE := rk3562_x7pro_go
PRODUCT_BRAND := Youdao
PRODUCT_MODEL := X7 Pro
PRODUCT_MANUFACTURER := Youdao
PRODUCT_AAPT_PREF_CONFIG := hdpi

## add Rockchip properties
PRODUCT_PROPERTY_OVERRIDES += ro.sf.lcd_density=213
PRODUCT_PROPERTY_OVERRIDES += ro.wifi.sleep.power.down=true
PRODUCT_PROPERTY_OVERRIDES += persist.wifi.sleep.delay.ms=0
PRODUCT_PROPERTY_OVERRIDES += persist.bt.power.down=true
PRODUCT_PROPERTY_OVERRIDES += ro.vendor.hdmirotationlock=true
PRODUCT_PROPERTY_OVERRIDES += dalvik.vm.dex2oat64.enabled=true

# The generic SKV ANR path returns silence with the X7 Pro's RK817 PDM input.
# Use the HAL's working Speex path for built-in microphone capture.
PRODUCT_VENDOR_PROPERTIES += vendor.audio.anr.speex=1

# The binary-only X7 Pro modules require no MODVERSIONS and voluntary
# preemption, which cannot satisfy Android 13's generic level-7 kernel FCM.
# Suppress only the user-facing consistency warning for this port.
PRODUCT_SYSTEM_PROPERTIES += ro.x7pro.allow_legacy_kernel_fcm=true

# Repeated development reboots must not make RescueParty redirect this
# bring-up image into recovery. Remove this once the product is productionized.
PRODUCT_PRODUCT_PROPERTIES += persist.sys.disable_rescue=1

# BES2600 Wi-Fi userspace config (wpa_supplicant/p2p overlays).
include hardware/bes/wireless/wlan/bes2600/config/config-bes.mk

# The generic Bluetooth HAL selects this library at runtime when
# librkwifi-ctrl reports the BES2600 chip.
PRODUCT_PACKAGES += libbt-vendor-bes2600

# Stock vendor assets captured from the X7 Pro:
#   prebuilt/modules   - binary-only kernel modules (no source in the SDK)
#   prebuilt/firmware  - BES2600 Wi-Fi/BT firmware and AW883xx smart-PA config
#   prebuilt/iqfiles   - rkaiq camera tuning files (isp32_lite / rkisp2)
X7PRO_PREBUILT := $(LOCAL_PATH)/prebuilt
X7PRO_FW := $(X7PRO_PREBUILT)/firmware
PRODUCT_COPY_FILES += \
	$(LOCAL_PATH)/init.x7pro.bluetooth.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.x7pro.bluetooth.rc \
	$(LOCAL_PATH)/besbt.conf:$(TARGET_COPY_OUT_VENDOR)/etc/bluetooth/besbt.conf \
	$(X7PRO_PREBUILT)/modules/bes2600.ko:$(TARGET_COPY_OUT_VENDOR_DLKM)/lib/modules/bes2600.ko \
	$(X7PRO_PREBUILT)/modules/snd-soc-aw883xx-v16.ko:$(TARGET_COPY_OUT_VENDOR_DLKM)/lib/modules/snd-soc-aw883xx-v16.ko \
    $(X7PRO_PREBUILT)/modules.load:$(TARGET_COPY_OUT_VENDOR_DLKM)/lib/modules/modules.load \
    $(call find-copy-subdir-files,*.json,$(X7PRO_PREBUILT)/iqfiles,$(TARGET_COPY_OUT_VENDOR)/etc/camera/rkisp2) \
    $(X7PRO_FW)/aw883xx_acf.bin:$(TARGET_COPY_OUT_VENDOR)/firmware/aw883xx_acf.bin \
    $(X7PRO_FW)/aw883xx_acf.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/aw883xx_acf.bin \
    $(X7PRO_FW)/bes2600_dpd.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/bes2600_dpd.bin \
    $(X7PRO_FW)/bes2600_factory.txt:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/bes2600_factory.txt \
    $(X7PRO_FW)/best2002_fw_boot_sdio.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/best2002_fw_boot_sdio.bin \
    $(X7PRO_FW)/best2002_fw_sdio.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/best2002_fw_sdio.bin \
    $(X7PRO_FW)/best2002_fw_sdio_btrf.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/best2002_fw_sdio_btrf.bin \
    $(X7PRO_FW)/best2002_fw_sdio_nosignal.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/best2002_fw_sdio_nosignal.bin
# Kernel request_firmware() is served by init only from
# /etc/firmware /odm/firmware /vendor/firmware /firmware/image, so the
# BES2600 firmware binaries are duplicated to /vendor/firmware as well.
PRODUCT_COPY_FILES += \
    $(X7PRO_FW)/best2002_fw_boot_sdio.bin:$(TARGET_COPY_OUT_VENDOR)/firmware/best2002_fw_boot_sdio.bin \
    $(X7PRO_FW)/best2002_fw_sdio.bin:$(TARGET_COPY_OUT_VENDOR)/firmware/best2002_fw_sdio.bin \
    $(X7PRO_FW)/best2002_fw_sdio_btrf.bin:$(TARGET_COPY_OUT_VENDOR)/firmware/best2002_fw_sdio_btrf.bin \
    $(X7PRO_FW)/best2002_fw_sdio_nosignal.bin:$(TARGET_COPY_OUT_VENDOR)/firmware/best2002_fw_sdio_nosignal.bin
