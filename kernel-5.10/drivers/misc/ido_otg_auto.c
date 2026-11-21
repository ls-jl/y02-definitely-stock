
#include <linux/freezer.h>
#include <linux/syscalls.h>
#include <linux/fs.h>
#include <linux/gpio.h>
#include <linux/delay.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/pm.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/of_platform.h>
#include <linux/of_gpio.h>
#include <linux/miscdevice.h>
#include <linux/workqueue.h>

#define HOST_VALUE		1
#define DEVICE_VALUE	0

typedef struct {
	int32_t otg_id_pin; //控制OTG ID的电平，低：Host模式 高：Device模式,同时控制USB 5V输出
	int32_t pwr_check_pin; //检测USB口是否有电，有电则认为是连接到USB到PC
} init_io_ctrl_data;

static init_io_ctrl_data io_ctrl_data = {	
	.otg_id_pin=-1,
	.pwr_check_pin=-1,
};

static struct delayed_work delaywork;

static void host_delaywork_func (struct work_struct *work) {	
	gpio_set_value(io_ctrl_data.otg_id_pin, HOST_VALUE);//OTG Host and Output 5V
	
	printk("Auto OTG is Host mode!\n");
}

static int otg_id_open(struct inode *nodp, struct file *filp)
{    
    return 0;
}

static ssize_t otg_id_write(struct file *file,const char __user *buf,size_t count,loff_t *ppos)
{   
	char data[7];
	
	if (count <=7 && copy_from_user(data, buf, count) == 0) {	
		if (strncmp(data,"HOST",4) == 0) {
			gpio_set_value(io_ctrl_data.otg_id_pin, HOST_VALUE);//OTG Host and Output 5V	
			printk("OTG is Host mode!\n");
			return count;		
		}else if (strncmp(data,"DEVICE",6) == 0) {		
			gpio_set_value(io_ctrl_data.otg_id_pin, DEVICE_VALUE);//OTG Device
			printk("OTG is Device mode!\n");
			return count;
		}		
	}
	return -EINVAL;
}

static struct file_operations otg_id_ctrl_fops =
{
	.owner = THIS_MODULE,
	.open = otg_id_open,
	.write = otg_id_write,
	.read = NULL
};

static struct miscdevice otg_id_ctrl_misc = 
{
	.minor = MISC_DYNAMIC_MINOR,
	.name  = "otg_mode",
	.fops  = &otg_id_ctrl_fops
};

static int otg_auto_probe(struct platform_device *pdev)
{
	struct device_node *np = pdev->dev.of_node;	
	int ret;
			
	io_ctrl_data.otg_id_pin = of_get_named_gpio(np, "gpio-otg-id", 0);
	if (gpio_is_valid(io_ctrl_data.otg_id_pin)) {
		ret = gpio_request(io_ctrl_data.otg_id_pin, "gpio_otg_id");
		if (ret){
			dev_err(&pdev->dev,"gpio request otg id ctrl failed,%d\n",io_ctrl_data.otg_id_pin);
			return -EINVAL;
		}
		
		gpio_direction_output(io_ctrl_data.otg_id_pin, DEVICE_VALUE);//OTG DEVICE
		
		ret = misc_register(&otg_id_ctrl_misc);
		if(ret < 0) {
			dev_err(&pdev->dev, "misc register otg auto fail!\n");
			return ret;	
		}
	} else {
		dev_err(&pdev->dev, "Device tree not define of gpio-otg-id\n");
		return -EINVAL;
	}
		
	io_ctrl_data.pwr_check_pin = of_get_named_gpio(np, "gpio-pwr-check", 0);
	if (gpio_is_valid(io_ctrl_data.pwr_check_pin)) {
		ret = gpio_request(io_ctrl_data.pwr_check_pin, "gpio_pwr_check");
		if (ret) {
			INIT_DELAYED_WORK(&delaywork,host_delaywork_func);
			schedule_delayed_work(&delaywork, msecs_to_jiffies(300));
			dev_err(&pdev->dev,"gpio_request failed,%d\n",io_ctrl_data.pwr_check_pin);
			return -EINVAL;
		}
		
		gpio_direction_input(io_ctrl_data.pwr_check_pin);
		
		mdelay(2);
		
		if (gpio_get_value(io_ctrl_data.pwr_check_pin) == 0) {
			INIT_DELAYED_WORK(&delaywork,host_delaywork_func);
			schedule_delayed_work(&delaywork, msecs_to_jiffies(8000));			
		} else {
			printk("Auto OTG is Device mode!\n");			
		}
	} else {
		dev_err(&pdev->dev, "Device tree not define of gpio-pwr-check\n");
		INIT_DELAYED_WORK(&delaywork,host_delaywork_func);
		schedule_delayed_work(&delaywork, msecs_to_jiffies(300));	
		return -EINVAL;		
	}

	printk("Auto OTG is complete!\n");
	return 0;
}


static const struct of_device_id otg_auto_of_match[] = {
	{ .compatible = "ido,otg-auto" },
	{ /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, otg_auto_of_match);


static struct platform_driver otg_auto_driver = {
	.driver = {
		.owner	= THIS_MODULE,
		.name	= "ido-otg-auto",
		.of_match_table = of_match_ptr(otg_auto_of_match),
	},	
	.probe		= otg_auto_probe,
	.remove     = NULL
};


static int __init cust_io_ctl_init(void)
{
	return platform_driver_register(&otg_auto_driver);
}

static void __exit cust_io_ctl_exit(void)
{
	if (gpio_is_valid(io_ctrl_data.otg_id_pin))
		gpio_set_value(io_ctrl_data.otg_id_pin, DEVICE_VALUE);//OTG Device
	platform_driver_unregister(&otg_auto_driver);
}

module_init(cust_io_ctl_init);
module_exit(cust_io_ctl_exit);

MODULE_AUTHOR("lyle,20200522");
MODULE_DESCRIPTION("industio otg auto");
MODULE_LICENSE("GPL");
