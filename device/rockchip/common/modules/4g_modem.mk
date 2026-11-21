#
# Copyright 2021 Rockchip Limited
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

PRODUCT_PACKAGES += \
    CarrierDefaultApp \
    CarrierConfig \
    rild \
    librk-ril \
    dhcpcd

PRODUCT_COPY_FILES += vendor/rockchip/common/phone/etc/apns-full-conf.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/apns-conf.xml

PRODUCT_PACKAGES += \
    android.hardware.radio@1.5-radio-service \
    android.hardware.radio.config@1.2-service \
    android.hardware.radio.config@1.0-service \
    android.hardware.radio.config@1.0.vendor \
    android.hardware.radio.config@1.2.vendor \
    android.hardware.radio@1.5.vendor \
    libhwbinder.vendor
    
#PRODUCT_PACKAGES += \
#    android.hardware.radio@1.2-radio-service \
#    android.hardware.radio.config@1.0-service

PRODUCT_PROPERTY_OVERRIDES += \
    ro.boot.noril=false \
    ro.telephony.default_network=33

DEVICE_MANIFEST_FILE += device/rockchip/common/4g_modem/manifest.xml

ifeq ($(strip $(TARGET_ARCH)), arm64)

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/../4g_modem/bin64/dhcpcd:$(TARGET_COPY_OUT_VENDOR)/bin/dhcpcd 
# Quectel
PRODUCT_PROPERTY_OVERRIDES += \
    vendor.rild.libpath=/vendor/lib64/libquectel-ril.so

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/../4g_modem/quectel/lib64/libreference-ril.so:$(TARGET_COPY_OUT_VENDOR)/lib64/libquectel-ril.so \
    $(LOCAL_PATH)/../4g_modem/quectel/lib64/ql-ril.conf:$(TARGET_COPY_OUT_VENDOR)/etc/ql-ril.conf \
    $(LOCAL_PATH)/../4g_modem/quectel/lib64/gps_cfg.inf:$(TARGET_COPY_OUT_VENDOR)/etc/gps_cfg.inf \

LIBRIL_INSTALL_PATH = $(LOCAL_PATH)/../../../../out/target/product/$(TARGET_PRODUCT)/$(TARGET_COPY_OUT_VENDOR)/lib64
$(info $(shell if [ -d $(LIBRIL_INSTALL_PATH) ]; then cp $(LOCAL_PATH)/../4g_modem/quectel/lib64/libril.so  $(LIBRIL_INSTALL_PATH)/libril.so ; fi ))
else
PRODUCT_PROPERTY_OVERRIDES += \
    vendor.rild.libpath=/vendor/lib/librk-ril.so

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/4g_modem/bin32/dhcpcd:$(TARGET_COPY_OUT_VENDOR)/bin/dhcpcd \
    $(LOCAL_PATH)/4g_modem/lib32/librk-ril.so:$(TARGET_COPY_OUT_VENDOR)/lib/librk-ril.so
endif
