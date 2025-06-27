GROUP(-lgcc)

ENTRY(_start)

MEMORY
{
	SRAM        (RW) : ORIGIN = 0x900000000a000000,LENGTH = 0x10000000
}

SECTIONS
{
	. = 0x900000000a000000;
	.text : 	
	{
		KEEP(*(.start))
		/* 此处需0x1000对齐，因为CSR.ebase域低12bit固定为0，写忽略 */
		. = ALIGN(0x1000);
		__ebase_entry = .;
        KEEP(*(.vectors))
        __ebase_end = .;		
		
		*(.text)

		/* 下述段用于autoinit组件 */
		. = ALIGN(8);
        __lr_init_start = .;
        KEEP(*(SORT(.lr_ai.*)))
        __lr_init_end = .;
        . = ALIGN(8);
	}

	cmd_list :{
		__start_cmd_list = .;
		*(cmd_list);
		__stop_cmd_list = .;
	}

	.LRtestTcTab :
	{
		. = ALIGN(8);
		__lrtest_tc_tab_start = .;
		KEEP(*(.LRtestTcTab))
		__lrtest_tc_tab_end = .;
	} > SRAM

	.rodata : 
	{ 
		*(.rodata) 
	}

	.data :
	{
		*(.data)
	}

	.stack :
    {
        . = ALIGN(8);
        _kernel_stack_start = .;		
        . = . + 0x10000;
        _kernel_stack = .;
    }


	.bss : 
	{
		/* 此处8字节对齐与startup_gcc.S内实现的清除bss段的代码实现相关 */
		. = ALIGN(8);
		_bss_start = .;
		PROVIDE(_bss_start = .);
			*(.bss)
		_bss_end = .;
	}

	.libc :
	{
		PROVIDE(__libc_start_main = .);
		KEEP(*(.libc*))
		PROVIDE(__libc_end_main = .);
	}



	/DISCARD/ :
	{
		*(.comment)
		*(.eh_frame)
	}
	_heap = . + 0x6400000;	/* 100MB for heap */
}
