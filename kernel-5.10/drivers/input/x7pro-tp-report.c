// SPDX-License-Identifier: GPL-2.0-only
/*
 * X7 Pro vendor touchscreen report hook.
 *
 * The stock Buildroot kernel exported report_tp_unvalid() so that the
 * Sitronix touchscreen driver (sitronix-ts.ko) could report persistent
 * invalid touch data to a userspace diagnostics framework. Android has
 * no consumer for this report; keep a log-only stub to preserve the
 * module ABI.
 */

#include <linux/export.h>
#include <linux/printk.h>

void report_tp_unvalid(void)
{
	pr_info_ratelimited("touchscreen: persistent invalid touch data reported\n");
}
EXPORT_SYMBOL_GPL(report_tp_unvalid);
