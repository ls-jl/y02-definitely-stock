// SPDX-License-Identifier: GPL-2.0-only
/* X7 Pro scan-head white and infrared LEDs. */

#include <linux/gpio/consumer.h>
#include <linux/led-class-flash.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/workqueue.h>

#define X7PRO_FLASH_TIMEOUT_US	250000U

struct x7pro_led_channel {
	struct gpio_desc *gpio;
	struct led_classdev_flash fled;
	struct delayed_work timeout_work;
	bool on;
};

struct x7pro_scan_leds {
	struct x7pro_led_channel ir;
	struct x7pro_led_channel white;
};

static struct x7pro_led_channel *to_x7pro_channel(struct led_classdev *cdev)
{
	return container_of(lcdev_to_flcdev(cdev),
			    struct x7pro_led_channel, fled);
}

static struct x7pro_led_channel *fled_to_x7pro_channel(
		struct led_classdev_flash *fled)
{
	return container_of(fled, struct x7pro_led_channel, fled);
}

static void x7pro_led_set(struct x7pro_led_channel *channel, bool on)
{
	gpiod_set_value_cansleep(channel->gpio, on);
	channel->on = on;
}

static int x7pro_brightness_set(struct led_classdev *cdev,
				enum led_brightness brightness)
{
	struct x7pro_led_channel *channel = to_x7pro_channel(cdev);

	cancel_delayed_work_sync(&channel->timeout_work);
	x7pro_led_set(channel, brightness != LED_OFF);
	return 0;
}

static void x7pro_timeout_work(struct work_struct *work)
{
	struct x7pro_led_channel *channel = container_of(
		to_delayed_work(work), struct x7pro_led_channel, timeout_work);

	x7pro_led_set(channel, false);
}

static int x7pro_strobe_set(struct led_classdev_flash *fled, bool state)
{
	struct x7pro_led_channel *channel = fled_to_x7pro_channel(fled);

	cancel_delayed_work_sync(&channel->timeout_work);
	x7pro_led_set(channel, state);
	if (state)
		schedule_delayed_work(&channel->timeout_work,
			usecs_to_jiffies(fled->timeout.val));
	return 0;
}

static int x7pro_strobe_get(struct led_classdev_flash *fled, bool *state)
{
	*state = fled_to_x7pro_channel(fled)->on;
	return 0;
}

static int x7pro_flash_brightness_set(struct led_classdev_flash *fled,
				      u32 brightness)
{
	fled->brightness.val = brightness;
	return 0;
}

static int x7pro_timeout_set(struct led_classdev_flash *fled, u32 timeout)
{
	fled->timeout.val = timeout;
	return 0;
}

static const struct led_flash_ops x7pro_flash_ops = {
	.flash_brightness_set = x7pro_flash_brightness_set,
	.strobe_set = x7pro_strobe_set,
	.strobe_get = x7pro_strobe_get,
	.timeout_set = x7pro_timeout_set,
};

static int x7pro_register_channel(struct device *dev,
				  struct x7pro_led_channel *channel,
				  struct gpio_desc *gpio, const char *name)
{
	struct led_classdev *cdev = &channel->fled.led_cdev;

	channel->gpio = gpio;
	INIT_DELAYED_WORK(&channel->timeout_work, x7pro_timeout_work);
	channel->fled.ops = &x7pro_flash_ops;
	channel->fled.brightness.min = 0;
	channel->fled.brightness.max = 1;
	channel->fled.brightness.step = 1;
	channel->fled.brightness.val = 1;
	channel->fled.timeout.min = 1000;
	channel->fled.timeout.max = 1000000;
	channel->fled.timeout.step = 1000;
	channel->fled.timeout.val = X7PRO_FLASH_TIMEOUT_US;
	cdev->name = name;
	cdev->max_brightness = 1;
	cdev->brightness_set_blocking = x7pro_brightness_set;
	cdev->flags = LED_DEV_CAP_FLASH;

	return devm_led_classdev_flash_register(dev, &channel->fled);
}

static int x7pro_scan_led_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct x7pro_scan_leds *leds;
	struct gpio_desc *gpio43;
	struct gpio_desc *gpio44;
	int ret;

	leds = devm_kzalloc(dev, sizeof(*leds), GFP_KERNEL);
	if (!leds)
		return -ENOMEM;

	/*
	 * Factory userspace and the board schematic use GPIO43 for infrared and
	 * GPIO44 for white.  The captured DT accidentally names those properties
	 * the other way around, so preserve the proven factory numbering here.
	 */
	gpio43 = devm_gpiod_get_from_of_node(dev, dev->of_node, "white-gpio", 0,
					      GPIOD_OUT_LOW, "x7pro-ir");
	if (IS_ERR(gpio43))
		return dev_err_probe(dev, PTR_ERR(gpio43), "get GPIO43/IR\n");
	gpio44 = devm_gpiod_get_from_of_node(dev, dev->of_node, "ir-gpio", 0,
					      GPIOD_OUT_LOW, "x7pro-white");
	if (IS_ERR(gpio44))
		return dev_err_probe(dev, PTR_ERR(gpio44), "get GPIO44/white\n");

	ret = x7pro_register_channel(dev, &leds->ir, gpio43,
				     "x7pro:ir:flash");
	if (ret)
		return ret;
	ret = x7pro_register_channel(dev, &leds->white, gpio44,
				     "x7pro:white:flash");
	if (ret)
		return ret;

	platform_set_drvdata(pdev, leds);
	dev_info(dev, "registered IR GPIO43 and white GPIO44 scan LEDs\n");
	return 0;
}

static int x7pro_scan_led_remove(struct platform_device *pdev)
{
	struct x7pro_scan_leds *leds = platform_get_drvdata(pdev);

	cancel_delayed_work_sync(&leds->ir.timeout_work);
	cancel_delayed_work_sync(&leds->white.timeout_work);
	x7pro_led_set(&leds->ir, false);
	x7pro_led_set(&leds->white, false);
	return 0;
}

static const struct of_device_id x7pro_scan_led_of_match[] = {
	{ .compatible = "led_control" },
	{}
};
MODULE_DEVICE_TABLE(of, x7pro_scan_led_of_match);

static struct platform_driver x7pro_scan_led_driver = {
	.probe = x7pro_scan_led_probe,
	.remove = x7pro_scan_led_remove,
	.driver = {
		.name = "x7pro-scan-led",
		.of_match_table = x7pro_scan_led_of_match,
	},
};
module_platform_driver(x7pro_scan_led_driver);

MODULE_DESCRIPTION("Youdao X7 Pro scan-head LED driver");
MODULE_LICENSE("GPL");
