LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_PRODUCT),rk3562_x7pro_go)

X7PRO_FIT_WRAPPER := $(LOCAL_PATH)/mkbootimg_x7pro.py
X7PRO_FIT_BUILDER := $(abspath $(TOPDIR)../../tools/fit/make_android_fit.py)
X7PRO_FIT_DTC := $(abspath $(TOPDIR)../kernel_out_x7pro/scripts/dtc/dtc)
X7PRO_FIT_FALLBACK_DTB := $(LOCAL_PATH)/prebuilt/dtb/rk3562-y02-saradc-ch2-228.dtb
X7PRO_FIT_INPUTS := \
    $(PRODUCT_OUT)/kernel \
    $(PRODUCT_OUT)/ramdisk-recovery.img \
    $(PRODUCT_OUT)/dtb.img \
    $(X7PRO_FIT_WRAPPER) \
    $(X7PRO_FIT_BUILDER) \
    $(X7PRO_FIT_DTC) \
    $(X7PRO_FIT_FALLBACK_DTB)

X7PRO_BOOT_A_IMAGE := $(PRODUCT_OUT)/boot_a.img
X7PRO_BOOT_B_IMAGE := $(PRODUCT_OUT)/boot_b.img
X7PRO_RECOVERY_IMAGE := $(PRODUCT_OUT)/recovery.img

$(X7PRO_BOOT_A_IMAGE): $(PRODUCT_OUT)/boot.img
	@echo "Target X7 Pro slot-A FIT: $@"
	$(hide) cp -f $< $@

$(X7PRO_BOOT_B_IMAGE): $(X7PRO_FIT_INPUTS)
	@echo "Target X7 Pro slot-B FIT: $@"
	$(hide) ANDROID_BUILD_TOP=$(abspath $(TOPDIR)) \
	    X7PRO_FIT_MODE=normal X7PRO_SLOT_SUFFIX=_b \
	    $(X7PRO_FIT_WRAPPER) --kernel $(PRODUCT_OUT)/kernel \
	    --ramdisk $(PRODUCT_OUT)/ramdisk-recovery.img \
	    --dtb $(PRODUCT_OUT)/dtb.img \
	    --cmdline "$(INTERNAL_KERNEL_CMDLINE)" --output $@

$(X7PRO_RECOVERY_IMAGE): $(X7PRO_FIT_INPUTS)
	@echo "Target X7 Pro recovery FIT: $@"
	$(hide) ANDROID_BUILD_TOP=$(abspath $(TOPDIR)) \
	    X7PRO_FIT_MODE=recovery X7PRO_SLOT_SUFFIX=_a \
	    $(X7PRO_FIT_WRAPPER) --kernel $(PRODUCT_OUT)/kernel \
	    --ramdisk $(PRODUCT_OUT)/ramdisk-recovery.img \
	    --dtb $(PRODUCT_OUT)/dtb.img \
	    --cmdline "$(INTERNAL_KERNEL_CMDLINE)" --output $@

ALL_DEFAULT_INSTALLED_MODULES += \
    $(X7PRO_BOOT_A_IMAGE) \
    $(X7PRO_BOOT_B_IMAGE) \
    $(X7PRO_RECOVERY_IMAGE)

.PHONY: x7pro-fit-images
x7pro-fit-images: $(X7PRO_BOOT_A_IMAGE) $(X7PRO_BOOT_B_IMAGE) $(X7PRO_RECOVERY_IMAGE)

endif
