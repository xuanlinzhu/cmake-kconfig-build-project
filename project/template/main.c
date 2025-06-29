#include <stdio.h>
#include "ck_config.h"

#ifdef DRV_DRV1
#include "drv1.h"
#endif

#ifdef PACK_PACK1
#include "pack1.h"
#endif

void main(void)
{
    printf("Hello World!\n");
    #ifdef DRV_DRV1
        drv_test();
    #endif
    #ifdef PACK_PACK1
        pack_test();
    #endif

}
