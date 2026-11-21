// SPDX-License-Identifier: GPL-2.0
#include <linux/delay.h>
#include <linux/gpio.h>
#include <linux/input.h>
#include <linux/input/mt.h>
#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/of_gpio.h>
#include <linux/regulator/consumer.h>
#include <linux/spi/spi.h>
#include <linux/workqueue.h>

struct x7_sitronix {
	struct spi_device *spi;
	struct input_dev *input;
	struct delayed_work init_work;
	struct regulator_bulk_data supplies[2];
	int reset_gpio;
	int irq_gpio;
	int panel_reset_gpio;
	int irq;
	u16 max_x;
	u16 max_y;
	u8 max_touches;
	bool initialized;
	bool touch_active;
	bool force_recovery;
	bool stopping;
};

extern const u8 x7_77921_fw_start[];
extern const u8 x7_77921_fw_end[];

static void x7_st_disable_supplies(void *data)
{
	struct x7_sitronix *st = data;

	regulator_bulk_disable(ARRAY_SIZE(st->supplies), st->supplies);
}

static void x7_st_cancel_init(void *data)
{
	struct x7_sitronix *st = data;

	st->stopping = true;
	cancel_delayed_work_sync(&st->init_work);
}

static int x7_st_raw_write(struct x7_sitronix *st, const u8 *data,
			   size_t len)
{
	return spi_write(st->spi, data, len);
}

static int x7_st_pram_write(struct x7_sitronix *st, u32 address,
			    const u8 *data, size_t len)
{
	const size_t chunk_size = 1024;
	u8 *packet;
	int ret = 0;

	packet = kmalloc(chunk_size + 3, GFP_KERNEL);
	if (!packet)
		return -ENOMEM;

	while (len) {
		size_t chunk = min(len, chunk_size);

		packet[0] = address >> 16;
		packet[1] = address >> 8;
		packet[2] = address;
		memcpy(&packet[3], data, chunk);
		ret = x7_st_raw_write(st, packet, chunk + 3);
		if (ret)
			break;
		address += chunk;
		data += chunk;
		len -= chunk;
	}

	kfree(packet);
	return ret;
}

static int x7_st_load_firmware(struct x7_sitronix *st)
{
	static const u8 enter[][5] = {
		{ 0x53, 0x71, 0x23, 0xa5, 0x3c },
		{ 0x53, 0x71, 0x23, 0x05, 0x55 },
		{ 0x53, 0x71, 0x23, 0x55, 0x55 },
		{ 0x53, 0x71, 0x23, 0x14, 0x55 },
		{ 0x00, 0xf3, 0x00, 0x5a, 0xa5 },
		{ 0x00, 0xf3, 0x02, 0x00, 0x01 },
		{ 0x00, 0xf3, 0x02, 0x00, 0x00 },
		{ 0x00, 0xf3, 0x02, 0x00, 0x01 },
	};
	static const u8 start[] = { 0x00, 0xf3, 0x02, 0x00, 0x03 };
	static const u8 post[][5] = {
		{ 0x00, 0xf3, 0x00, 0x00, 0x00 },
		{ 0x00, 0xf0, 0x06, 0x00, 0x01 },
		{ 0x53, 0x71, 0x23, 0x50, 0x4c },
		{ 0x53, 0x71, 0x23, 0x55, 0x4c },
		{ 0x53, 0x71, 0x23, 0x41, 0x4c },
		{ 0x53, 0x71, 0x23, 0x5a, 0xc3 },
	};
	const u8 *fw = x7_77921_fw_start;
	size_t fw_size = x7_77921_fw_end - x7_77921_fw_start;
	u32 config_length;
	int ret;
	int i;

	if (fw_size < 0xf010)
		return -EINVAL;

	for (i = 0; i < ARRAY_SIZE(enter); i++) {
		ret = x7_st_raw_write(st, enter[i], sizeof(enter[i]));
		if (ret)
			return ret;
		msleep(1);
	}

	ret = x7_st_pram_write(st, 0x7f0000, fw, 0xc000);
	if (ret)
		return ret;

	if (memcmp(&fw[0xf000], "CFT1", 4))
		return -EINVAL;
	config_length = (fw[0xf00b] << 8) | fw[0xf00c];
	config_length += 3;
	if (0xf000 + config_length > fw_size)
		return -EINVAL;
	ret = x7_st_pram_write(st, 0x000300, &fw[0xf000], config_length);
	if (ret)
		return ret;

	ret = x7_st_raw_write(st, start, sizeof(start));
	if (ret)
		return ret;
	msleep(20);
	for (i = 0; i < ARRAY_SIZE(post); i++) {
		ret = x7_st_raw_write(st, post[i], sizeof(post[i]));
		if (ret)
			return ret;
		msleep(1);
	}
	dev_info(&st->spi->dev,
		 "loaded 77921 firmware: code=%u config=%u\n",
		 0xc000, config_length);
	msleep(20);

	return 0;
}

static int x7_st_read(struct x7_sitronix *st, u16 reg, u8 *data, size_t len)
{
	u8 tx[2] = { 0x80 | (reg >> 8), reg & 0xff };
	u8 rx[32] = { 0 };
	struct spi_transfer transfers[2] = {
		{
			.tx_buf = tx,
			.len = sizeof(tx),
			.delay_usecs = 10,
		}, {
			.rx_buf = rx,
			.len = len + 1,
		},
	};
	struct spi_message message;
	int ret;

	if (len + 1 > sizeof(rx))
		return -EINVAL;

	spi_message_init_with_transfers(&message, transfers,
					ARRAY_SIZE(transfers));
	ret = spi_sync(st->spi, &message);
	if (ret)
		return ret;
	memcpy(data, &rx[1], len);
	usleep_range(30, 40);
	return 0;
}

static irqreturn_t x7_st_irq_thread(int irq, void *context)
{
	struct x7_sitronix *st = context;
	u8 report[5 + 7 * 2];
	bool any = false;
	int ret;
	int slot;

	ret = x7_st_read(st, 0x0010, report, sizeof(report));
	if (ret)
		return IRQ_HANDLED;
	for (slot = 0; slot < st->max_touches; slot++) {
		const u8 *point = &report[4 + slot * 7];
		bool active = point[0] & BIT(7);
		u16 x = ((point[0] & 0x3f) << 8) | point[1];
		u16 y = ((point[2] & 0x3f) << 8) | point[3];

		input_mt_slot(st->input, slot);
		input_mt_report_slot_state(st->input, MT_TOOL_FINGER, active);
		if (active) {
			input_report_abs(st->input, ABS_MT_POSITION_X,
					 min_t(u16, x, st->max_x - 1));
			input_report_abs(st->input, ABS_MT_POSITION_Y,
					 min_t(u16, y, st->max_y - 1));
			any = true;
		}
	}
	input_report_key(st->input, BTN_TOUCH, any);
	input_mt_sync_frame(st->input);
	input_sync(st->input);
	st->touch_active = any;
	return IRQ_HANDLED;
}

static int x7_st_input_init(struct x7_sitronix *st)
{
	struct input_dev *input;
	u8 info[10];
	int ret;

	ret = x7_st_read(st, 0x0000, info, sizeof(info));
	if (ret)
		return ret;
	st->max_x = ((info[5] & 0x3f) << 8) | info[6];
	st->max_y = ((info[7] & 0x3f) << 8) | info[8];
	st->max_touches = clamp_t(u8, info[9], 1, 2);
	if (!st->max_x || !st->max_y ||
	    st->max_x > 4096 || st->max_y > 4096)
		return -EINVAL;

	input = devm_input_allocate_device(&st->spi->dev);
	if (!input)
		return -ENOMEM;
	st->input = input;
	input->name = "Sitronix ST77921 Touchscreen";
	input->id.bustype = BUS_SPI;
	input_set_capability(input, EV_KEY, BTN_TOUCH);
	input_set_abs_params(input, ABS_MT_POSITION_X, 0, st->max_x - 1, 0, 0);
	input_set_abs_params(input, ABS_MT_POSITION_Y, 0, st->max_y - 1, 0, 0);
	ret = input_mt_init_slots(input, st->max_touches,
				  INPUT_MT_DIRECT | INPUT_MT_DROP_UNUSED);
	if (ret)
		return ret;
	ret = input_register_device(input);
	if (ret)
		return ret;

	st->irq = gpio_to_irq(st->irq_gpio);
	if (st->irq < 0)
		return st->irq;
	ret = devm_request_threaded_irq(&st->spi->dev, st->irq, NULL,
					x7_st_irq_thread,
					IRQF_TRIGGER_FALLING | IRQF_ONESHOT,
					dev_name(&st->spi->dev), st);
	if (ret)
		return ret;

	dev_info(&st->spi->dev, "registered %ux%u, %u touches, irq=%d\n",
		 st->max_x, st->max_y, st->max_touches, st->irq);
	return 0;
}

static void x7_st_release_all(struct x7_sitronix *st)
{
	int slot;

	for (slot = 0; slot < st->max_touches; slot++) {
		input_mt_slot(st->input, slot);
		input_mt_report_slot_state(st->input, MT_TOOL_FINGER, false);
	}
	input_report_key(st->input, BTN_TOUCH, false);
	input_mt_sync_frame(st->input);
	input_sync(st->input);
	st->touch_active = false;
}

static void x7_st_init_work(struct work_struct *work)
{
	struct x7_sitronix *st = container_of(to_delayed_work(work),
					       struct x7_sitronix, init_work);
	bool recovering = st->initialized;
	bool force_recovery = st->force_recovery;
	int ret;

	if (recovering && gpio_is_valid(st->panel_reset_gpio) &&
	    !gpio_get_value(st->panel_reset_gpio)) {
		/* Reload as soon as the panel reset line is released. */
		st->force_recovery = true;
		goto reschedule;
	}

	if (recovering && !force_recovery) {
		/*
		 * The X7 panel does not generate an edge for every coordinate frame.
		 * Poll at touch rate while active and at a lower idle rate to discover
		 * the next contact. Never reset the TDDI from this health path:
		 * repeated resets also disturb the LCD controller.
		 */
		x7_st_irq_thread(st->irq, st);
		goto reschedule_poll;
	}
	if (recovering) {
		st->force_recovery = false;
		dev_warn(&st->spi->dev, "resume recovery; reloading touchscreen firmware\n");
		disable_irq(st->irq);
	}

	if (gpio_is_valid(st->reset_gpio)) {
		gpio_set_value(st->reset_gpio, 0);
		msleep(20);
		gpio_set_value(st->reset_gpio, 1);
		msleep(100);
	}
	dev_info(&st->spi->dev, "delayed init: IRQ after reset: %d\n",
		 gpio_get_value(st->irq_gpio));

	ret = x7_st_load_firmware(st);
	if (ret) {
		dev_err(&st->spi->dev, "delayed firmware load failed: %d\n",
			ret);
		if (recovering)
			enable_irq(st->irq);
		goto reschedule;
	}
	dev_info(&st->spi->dev, "delayed init: IRQ after firmware: %d\n",
		 gpio_get_value(st->irq_gpio));
	if (recovering) {
		x7_st_release_all(st);
		enable_irq(st->irq);
		if (!gpio_get_value(st->irq_gpio))
			x7_st_irq_thread(st->irq, st);
		dev_info(&st->spi->dev, "touchscreen firmware recovered\n");
	} else {
		ret = x7_st_input_init(st);
		if (ret) {
			dev_err(&st->spi->dev,
				"delayed input init failed: %d\n", ret);
			goto reschedule;
		}
		st->initialized = true;
		if (!gpio_get_value(st->irq_gpio))
			x7_st_irq_thread(st->irq, st);
	}

reschedule:
	if (!st->stopping)
		schedule_delayed_work(&st->init_work, msecs_to_jiffies(1000));
	return;

reschedule_poll:
	if (!st->stopping)
		schedule_delayed_work(&st->init_work,
			msecs_to_jiffies(st->touch_active ? 10 : 50));
}

static int x7_st_probe(struct spi_device *spi)
{
	struct x7_sitronix *st;
	int ret;

	st = devm_kzalloc(&spi->dev, sizeof(*st), GFP_KERNEL);
	if (!st)
		return -ENOMEM;
	st->spi = spi;
	spi_set_drvdata(spi, st);
	st->supplies[0].supply = "power";
	st->supplies[1].supply = "vdd";
	ret = devm_regulator_bulk_get(&spi->dev, ARRAY_SIZE(st->supplies),
				      st->supplies);
	if (ret)
		return dev_err_probe(&spi->dev, ret,
				     "failed to get panel supplies\n");
	ret = regulator_bulk_enable(ARRAY_SIZE(st->supplies), st->supplies);
	if (ret)
		return dev_err_probe(&spi->dev, ret,
				     "failed to enable panel supplies\n");
	ret = devm_add_action_or_reset(&spi->dev, x7_st_disable_supplies, st);
	if (ret)
		return ret;
	msleep(10);

	spi->mode = SPI_MODE_3;
	spi->bits_per_word = 8;
	spi->max_speed_hz = min_t(u32, spi->max_speed_hz, 8000000);
	ret = spi_setup(spi);
	if (ret)
		return dev_err_probe(&spi->dev, ret, "spi_setup failed\n");

	st->reset_gpio = of_get_named_gpio(spi->dev.of_node, "rst-gpio", 0);
	st->irq_gpio = of_get_named_gpio(spi->dev.of_node, "irq-gpio", 0);
	st->panel_reset_gpio = of_get_named_gpio(spi->dev.of_node,
						 "panel-reset-gpio", 0);
	dev_info(&spi->dev,
		 "probe: speed=%u mode=%u reset=%d irq=%d panel-reset=%d\n",
		 spi->max_speed_hz, spi->mode, st->reset_gpio, st->irq_gpio,
		 st->panel_reset_gpio);

	if (gpio_is_valid(st->reset_gpio)) {
		ret = devm_gpio_request_one(&spi->dev, st->reset_gpio,
					    GPIOF_OUT_INIT_LOW, "sitronix-reset");
		if (ret)
			return dev_err_probe(&spi->dev, ret,
					     "request reset GPIO failed\n");
	}

	if (gpio_is_valid(st->irq_gpio)) {
		ret = devm_gpio_request_one(&spi->dev, st->irq_gpio, GPIOF_IN,
					    "sitronix-irq");
		if (ret)
			return dev_err_probe(&spi->dev, ret,
					     "request IRQ GPIO failed\n");
	}

	INIT_DELAYED_WORK(&st->init_work, x7_st_init_work);
	ret = devm_add_action_or_reset(&spi->dev, x7_st_cancel_init, st);
	if (ret)
		return ret;
	schedule_delayed_work(&st->init_work, msecs_to_jiffies(12000));
	dev_info(&spi->dev, "touch initialization scheduled after panel start\n");
	return 0;
}

static int x7_st_resume(struct device *dev)
{
	struct x7_sitronix *st = dev_get_drvdata(dev);

	if (st && st->initialized && !st->stopping) {
		st->force_recovery = true;
		mod_delayed_work(system_wq, &st->init_work,
				 msecs_to_jiffies(200));
		dev_info(dev, "resume: touchscreen recovery scheduled\n");
	}

	return 0;
}

static const struct dev_pm_ops x7_st_pm_ops = {
	SET_SYSTEM_SLEEP_PM_OPS(NULL, x7_st_resume)
};

static const struct of_device_id x7_st_of_match[] = {
	{ .compatible = "sitronix_ts" },
	{ }
};
MODULE_DEVICE_TABLE(of, x7_st_of_match);

static struct spi_driver x7_st_driver = {
	.driver = {
		.name = "x7-sitronix-probe",
		.of_match_table = x7_st_of_match,
		.pm = &x7_st_pm_ops,
	},
	.probe = x7_st_probe,
};
module_spi_driver(x7_st_driver);

MODULE_DESCRIPTION("X7 Pro Sitronix ST77921 touchscreen driver");
MODULE_LICENSE("GPL");
