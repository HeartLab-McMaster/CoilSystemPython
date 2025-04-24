#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

#ifdef CONFIG_UNWINDER_ORC
#include <asm/orc_header.h>
ORC_HEADER;
#endif

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif



static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x1035c7c2, "__release_region" },
	{ 0x2f8479f2, "device_destroy" },
	{ 0xd58dd2b1, "cdev_del" },
	{ 0x37a0cba, "kfree" },
	{ 0xa915b11a, "pci_disable_device" },
	{ 0x4dfa8d4b, "mutex_lock" },
	{ 0x3213f038, "mutex_unlock" },
	{ 0x4c03a563, "random_kmalloc_seed" },
	{ 0xa63b4eed, "kmalloc_caches" },
	{ 0x59ffeca6, "kmalloc_trace" },
	{ 0x87a21cb3, "__ubsan_handle_out_of_bounds" },
	{ 0xd67eae7c, "boot_cpu_data" },
	{ 0xbc780795, "remap_pfn_range" },
	{ 0x46cf10eb, "cachemode2protval" },
	{ 0x5db27c3d, "__register_chrdev" },
	{ 0x38e073, "class_create" },
	{ 0x3bb4acde, "__pci_register_driver" },
	{ 0x9901e5e3, "class_destroy" },
	{ 0x6bc3fbc0, "__unregister_chrdev" },
	{ 0x459fa94a, "pci_unregister_driver" },
	{ 0xd9a5ea54, "__init_waitqueue_head" },
	{ 0xcefb0c9f, "__mutex_init" },
	{ 0xe26e4f68, "pci_enable_device" },
	{ 0xd72c74d1, "pci_set_master" },
	{ 0x66bc4897, "dma_set_mask" },
	{ 0x85bd1608, "__request_region" },
	{ 0xde80cd09, "ioremap" },
	{ 0x178f4a8a, "cdev_alloc" },
	{ 0x5c658724, "cdev_init" },
	{ 0xa2dc7695, "cdev_add" },
	{ 0x23a131f9, "device_create" },
	{ 0x92d5838e, "request_threaded_irq" },
	{ 0x13c49cc2, "_copy_from_user" },
	{ 0x6b10bee1, "_copy_to_user" },
	{ 0xf1969a8e, "__usecs_to_jiffies" },
	{ 0xe2c17b5d, "__SCT__might_resched" },
	{ 0xfe487975, "init_wait_entry" },
	{ 0x8c26d495, "prepare_to_wait_event" },
	{ 0x92540fbf, "finish_wait" },
	{ 0x1000e51, "schedule" },
	{ 0x8ddd8aad, "schedule_timeout" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0xb35af14c, "param_ops_int" },
	{ 0xbdfb6dbb, "__fentry__" },
	{ 0xe2964344, "__wake_up" },
	{ 0x34db050b, "_raw_spin_lock_irqsave" },
	{ 0xd35cce70, "_raw_spin_unlock_irqrestore" },
	{ 0x5b8239ca, "__x86_return_thunk" },
	{ 0x122c3a7e, "_printk" },
	{ 0xc1514a3b, "free_irq" },
	{ 0xedc03953, "iounmap" },
	{ 0x77358855, "iomem_resource" },
	{ 0xf079b8f9, "module_layout" },
};

MODULE_INFO(depends, "");

MODULE_ALIAS("pci:v000010B5d00009056sv00006000sd00000826bc*sc*i*");

MODULE_INFO(srcversion, "0D06F86313F45703E0D8862");
