#define  ESLOG_MSGID "main"
#include <lr_base_pkg.h>
#include "sline.h"
#include "string.h"
#include "nbpdef.h"
#include "thread.h"
#include "lr_gpio.h"
#ifdef ENABLE_MPU_2K1500
#include "ls2k1500.h"
#include "ls2k1500_reg.h"
#include "loongarchregs.h"
#endif
#ifdef ESLOG_ENABLE
#include "eslog.h"
#endif
#include "stddef.h"
#include "lr_config.h"
#include "lr_uart.h"

#include "lr_hpet.h"
// #include "lr_emmc.h"
#include "lr_osal.h"

static lr_uart_t *puart = NULL;
static lr_hpet_t *hp = NULL;


static void bsp_init(void);

int main(int argc, char **argv)
{
    bsp_init();   
    lr_osal_startup();
	
    return 1;
}

static void tgt_fpuenable()
{
#ifdef ENABLE_MPU_2K1500
	asm(					\
	"csrrd $r4, 0x2;\n\t"			\
	"ori   $r4, $r4, 1;\n\t"		\
	"csrwr $r4, 0x2;\n\t"			\
	:::"$r4"
	);
#endif
}

static void set_ebase(void)
{
    extern char __ebase_entry;
    unsigned long long ebase = (unsigned long long)&__ebase_entry;
    ebase |= 0x1234;
    write_64bit_csr(0xc, ebase);
    ebase = read_64bit_csr(0xc);
}


int my_gc(void)
{
    return puart->getc(0);
}

int my_pc(char c)
{
    puart->putc(0,c);
    return 0;
}

static void bsp_init(void)
{
    puart = lr_get_uart_handler();
    lr_printf_config(my_pc);
    hp = lr_get_hpet_handler();
    hp->start();
    // em = lr_get_emmc_handle();
    // em->open();
    
    set_ebase();
    tgt_fpuenable();
}

#define APP_THREAD_STACK_SIZE   (20*1024)
/* task stack */
static nbp_uint8_t sline_thread_stack[APP_THREAD_STACK_SIZE];
static struct nbp_thread sline_thread;
#ifdef LWIP_ENABLE
static nbp_uint8_t lwip_thread_stack[APP_THREAD_STACK_SIZE];
static struct nbp_thread lwip_thread;
#endif
static nbp_uint8_t idle_thread_stack[2*1024];
static struct nbp_thread idle_thread;

void sline_task(void*para)
{
    #if defined LR_SLINE_USED

    sl_register_func_t sl_rfunc = {
    .getc = (void *)my_gc,
    .putc = (void *)my_pc
    };
    #endif

    #if(SL_KEYWORD_ENABLE)
    char* keys[50]= {"print()","exit","if",
                    "then","else","zhuxuanlin","sline","end",
                    "while","class","and","break","do"
                    ,"elseif","false","for","function","in",
                    "local","nil","not","or","repeat","return",
                    "true","until"};
    sl_keys_add(keys,50);
    #endif
    
    sl_create( &sl_rfunc);
    while (1)
    {
        sl_waitcmd();
        nbp_thread_sleep(1);
    }
}
void sys_task2(void*para)
{
    while (1)
    {
        nbp_tick_increase();       
    }	
}

#ifdef LWIP_ENABLE
extern int lwip_test(void *para);
#endif

void app_init(void)
{
    nbp_thread_init(&sline_thread, "sline", sline_task, NULL,
    		sline_thread_stack, sizeof(sline_thread_stack), 29, 2);
    nbp_thread_startup(&sline_thread);

#ifdef LWIP_ENABLE
    nbp_thread_init(&lwip_thread, "lwip", lwip_test, NULL,
    		lwip_thread_stack, sizeof(lwip_thread_stack), 10, 2);
    nbp_thread_startup(&lwip_thread);
#endif

    nbp_thread_init(&idle_thread, "idle", sys_task2, NULL,
    		idle_thread_stack, sizeof(idle_thread_stack), 31, 2);
    nbp_thread_startup(&idle_thread);

}


