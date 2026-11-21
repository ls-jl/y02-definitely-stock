// SPDX-License-Identifier: GPL-2.0
/* X7 Pro dwc3 register dumper: prints registers via the driver's own mapping */
#include <linux/module.h>
#include <linux/io.h>
#include <linux/workqueue.h>
#include "core.h"
#include "io.h"

static struct delayed_work x7_dwork;
static struct dwc3 *x7_dwc_inst;
static int x7_dump_count;

static void x7_dump32(struct dwc3 *dwc, const char *name, u32 off)
{
	pr_err("REGDUMP %s = 0x%08x\n", name, dwc3_readl(dwc->regs, off));
}

static void x7_do_dump(struct work_struct *w)
{
	struct dwc3 *dwc = x7_dwc_inst;
	struct dwc3_ep *ep0out;
	struct dwc3_ep *ep0in;
	struct dwc3_trb *trb0;
	struct dwc3_trb *trb1;

	if (!dwc)
		return;
	ep0out = dwc->eps[0];
	ep0in = dwc->eps[1];
	trb0 = &dwc->ep0_trb[0];
	trb1 = &dwc->ep0_trb[1];
	pr_err("REGDUMP === pass %d ===\n", x7_dump_count);
	x7_dump32(dwc, "DCFG", DWC3_DCFG);
	x7_dump32(dwc, "DCTL", DWC3_DCTL);
	x7_dump32(dwc, "DSTS", DWC3_DSTS);
	x7_dump32(dwc, "GUSB2PHYCFG(0)", DWC3_GUSB2PHYCFG(0));
	x7_dump32(dwc, "GTXFIFOSIZ(0)", DWC3_GTXFIFOSIZ(0));
	x7_dump32(dwc, "GRXFIFOSIZ(0)", DWC3_GRXFIFOSIZ(0));
	x7_dump32(dwc, "GCTL", DWC3_GCTL);
	x7_dump32(dwc, "GTXTHRCFG", DWC3_GTXTHRCFG);
	x7_dump32(dwc, "GRXTHRCFG", DWC3_GRXTHRCFG);
	x7_dump32(dwc, "GEVNTCOUNT(0)", DWC3_GEVNTCOUNT(0));
	pr_err("REGDUMP EP0 state=%u next=%u pending=%u connected=%u delayed=%u out_flags=0x%x out_res=%u out_enq=%u in_flags=0x%x in_res=%u in_enq=%u\n",
		dwc->ep0state, dwc->ep0_next_event,
		dwc->setup_packet_pending, dwc->connected, dwc->delayed_status,
		ep0out->flags, ep0out->resource_index, ep0out->trb_enqueue,
		ep0in->flags, ep0in->resource_index, ep0in->trb_enqueue);
	pr_err("REGDUMP EP0TRB0 bpl=%08x bph=%08x size=%08x ctrl=%08x EP0TRB1 bpl=%08x bph=%08x size=%08x ctrl=%08x\n",
		trb0->bpl, trb0->bph, trb0->size, trb0->ctrl,
		trb1->bpl, trb1->bph, trb1->size, trb1->ctrl);
	if (++x7_dump_count < 8)
		schedule_delayed_work(&x7_dwork, 10 * HZ);
}

void x7_regdump_start(struct dwc3 *dwc)
{
	/* Pull-up can be toggled more than once; one trace per boot is enough. */
	if (x7_dwc_inst)
		return;

	x7_dwc_inst = dwc;
	INIT_DELAYED_WORK(&x7_dwork, x7_do_dump);
	schedule_delayed_work(&x7_dwork, 2 * HZ);
}
EXPORT_SYMBOL_GPL(x7_regdump_start);
