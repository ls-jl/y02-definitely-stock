# RK3562 X7 Pro Android Go product

This product is derived from `rk3562_tgo` for the Youdao X7 Pro hardware.

- Android 13 / API 33
- Android Go low-RAM configuration
- Traditional A/B slots (virtual A/B disabled)
- Kernel release target: 5.10.160
- Kernel DTS: `rk3562-y02-v10`
- Display: 280 x 936 MIPI-DSI

The DTS is a lossless decompile of the DTB read from the live X7 Pro. Building
it through the kernel Makefile reproduces the stock DTB exactly:

`f8da8a05ba52fe98e3ef39adf6d456471a5f832e1dc07dd4fd66662b97eca8a4`

The local Android SDK contains a 5.10.157 source snapshot but no local
5.10.158--5.10.160 stable patches. The current 5.10.160 change therefore
aligns the kernel release and module ABI only. Do not treat it as a source-level
backport of all three stable releases.

The final kernel config order is:

```text
rockchip_defconfig android-13-go.config rk356x.config x7pro.config
```

`x7pro.config` disables module symbol versions and full preemption to match the
stock X7 Pro modules' `5.10.160 SMP mod_unload aarch64` vermagic. It also
enables the ALSA sequencer symbols required by the stock MIDI modules.

The X7 Pro build path passes an empty `LOCALVERSION`, preventing a dirty local
tree from adding `+` to the module ABI. A symbol audit of all 46 stock modules
leaves three device-specific interfaces to implement before packaging:
`_trace_android_vh_record_pcpu_rwsem_starttime`, `report_tp_unvalid`, and
`mmc_host_rescan`.
