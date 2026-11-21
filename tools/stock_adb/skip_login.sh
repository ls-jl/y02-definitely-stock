#!/bin/sh
# Invoked by the factory /etc/init.d/S99_run_test_scripts on every boot.
# Only writable state is changed; the factory EROFS image stays unmodified.

USB_SERVICE=/usr/bin/S98usbdevice
USB_CONFIG=/tmp/.usb_config
AUTH_MARKER=/tmp/.adb_auth_verified
UDC=/sys/kernel/config/usb_gadget/rockchip/UDC
LOCK=/tmp/x7pro-adb-autostart.lock

[ -x "$USB_SERVICE" ] || exit 1
mkdir "$LOCK" 2>/dev/null || exit 0
trap 'rmdir "$LOCK" 2>/dev/null' 0

umask 022
mkdir -p /userdata/applog
exec >>/userdata/applog/adb-autostart.log 2>&1
echo "$(date) starting persistent USB ADB"

# The original adbd_auth.sh accepts this marker without requesting a password.
touch "$AUTH_MARKER" || exit 1

# Initial USB setup runs asynchronously. Let it bind before requesting a
# restart, so the two S98usbdevice instances cannot race during cold boot.
attempt=0
while [ "$attempt" -lt 20 ]; do
    if [ -f "$USB_CONFIG" ] && [ -r "$UDC" ] && [ -n "$(cat "$UDC")" ]; then
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if grep -qx 'usb_adb_en' "$USB_CONFIG" 2>/dev/null && pidof adbd >/dev/null 2>&1; then
    echo "$(date) ADB already running; authentication marker ready"
    exit 0
fi

# Preserve any other factory USB functions while ensuring MTP and ADB are on.
next_config="${USB_CONFIG}.x7pro.$$"
if [ -f "$USB_CONFIG" ]; then
    grep -vx 'USB_FORCE_CHANGED' "$USB_CONFIG" >"$next_config"
else
    : >"$next_config"
fi
grep -qx 'usb_mtp_en' "$next_config" || printf '%s\n' usb_mtp_en >>"$next_config"
grep -qx 'usb_adb_en' "$next_config" || printf '%s\n' usb_adb_en >>"$next_config"
mv "$next_config" "$USB_CONFIG" || exit 1

"$USB_SERVICE" restart
result=$?
touch "$AUTH_MARKER"
if [ "$result" -eq 0 ] && pidof adbd >/dev/null 2>&1; then
    echo "$(date) USB ADB enabled; shell password verification skipped"
    exit 0
fi
echo "$(date) USB ADB startup failed (USB service status $result)"
exit 1
