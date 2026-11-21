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
include device/rockchip/rk3562/BoardConfig.mk
BUILD_WITH_GO_OPT := true
PRODUCT_KERNEL_CONFIG += x7pro.config
PRODUCT_UBOOT_CONFIG := rk3562
PRODUCT_KERNEL_DTS := rk3562-y02-v10
PRODUCT_PARAMETER_TEMPLATE := device/rockchip/rk3562/rk3562_x7pro_go/parameter_ab.txt
BOARD_USE_RAW_PARAMETER_TEMPLATE := true
CAMERA_SUPPORT_AUTOFOCUS := true
BOARD_CAMERA_SUPPORT_EXT := true

# Produce the stock U-Boot/SPL external-data FIT directly as boot.img. The
# wrapper gzip-compresses the kernel so the complete image fits boot_a/boot_b.
BOARD_CUSTOM_MKBOOTIMG := device/rockchip/rk3562/rk3562_x7pro_go/mkbootimg_x7pro.py

# X7 Pro wireless connectivity is the BES2600 SDIO combo chip.
BOARD_WLAN_DEVICE := bes2600
BOARD_HAVE_BLUETOOTH_BES := true
BOARD_BLUETOOTH_BES_UART_PORT := /dev/ttyS1

BOARD_SEPOLICY_DIRS += device/rockchip/rk3562/rk3562_x7pro_go/sepolicy/vendor

# The stock X7 Pro partition table and boot arguments use A/B slots.
BOARD_USES_AB_IMAGE := true
BOARD_ROCKCHIP_VIRTUAL_AB_ENABLE := false

ifeq ($(strip $(BOARD_USES_AB_IMAGE)), true)
  include device/rockchip/common/BoardConfig_AB.mk
  # Keep the generic parameter generator's build-time DTBO size non-zero even
  # though X7 Pro embeds its DTB in FIT and excludes DTBO from the physical GPT.
  BOARD_DTBOIMG_PARTITION_SIZE := 4194304
  # BoardConfig_AB.mk points TARGET_RECOVERY_FSTAB at recovery.fstab_AB,
  # whose slotselect/logical flags crash the Rockchip recovery binary;
  # use the classic simple fstab instead.
  TARGET_RECOVERY_FSTAB := device/rockchip/rk3562/rk3562_x7pro_go/recovery.fstab
endif
