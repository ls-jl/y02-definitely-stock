// SPDX-License-Identifier: GPL-2.0
	.section .rodata,"a"
	.balign 8
	.global x7_77921_fw_start
	.global x7_77921_fw_end
x7_77921_fw_start:
	.incbin "drivers/input/touchscreen/x7_sitronix_77921.dump"
x7_77921_fw_end:
