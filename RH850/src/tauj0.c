/***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products.
* No other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws.
***********************************************************************************************************************/

#include "tauj0.h"
#include "tauj0_regs.h"

/* System Clock Frequency (Assuming 80MHz for now, should be defined in system header) */
#ifndef SYSTEM_CLOCK_HZ
#define SYSTEM_CLOCK_HZ (80000000UL)
#endif

/* TAUJ0 Clock Source Prescaler (Assuming PCLK/1 for simplicity) */
/* This needs to match the CKS setting in CMOR0 */
#define TAUJ0_PRESCALER (1UL)

void TAUJ0_Init(uint32_t interval_us)
{
    /* 1. Stop the timer channel */
    TAUJ0.TT0 |= TAUJ0_TT0_TT0_Msk;

    /* 2. Configure Operating Mode (Interval Timer Mode) */
    /* CKS[1:0] = 00 (Select CK0) */
    /* MD0 = 0 (Interval Timer Mode) */
    TAUJ0.CMOR0 = 0x00000000UL;

    /* 3. Set Interval */
    TAUJ0_SetInterval(interval_us);

    /* 4. Enable Interrupts (Logic to be added based on interrupt controller) */
    /* For now, we assume interrupt controller is configured externally or via separate API */
}

void TAUJ0_Start(void)
{
    /* Start the timer channel */
    TAUJ0.TS0 |= TAUJ0_TS0_TS0_Msk;
}

void TAUJ0_Stop(void)
{
    /* Stop the timer channel */
    TAUJ0.TT0 |= TAUJ0_TT0_TT0_Msk;
}

void TAUJ0_SetInterval(uint32_t interval_us)
{
    uint32_t counts;

    /* Calculate counts based on interval and clock */
    /* counts = (interval_us * (SYSTEM_CLOCK_HZ / TAUJ0_PRESCALER)) / 1000000 */
    /* Simplified calculation: 80MHz / 1MHz = 80 counts per us */
    /* Note: This assumes SYSTEM_CLOCK_HZ is a multiple of 1MHz */
    counts = interval_us * (SYSTEM_CLOCK_HZ / 1000000UL);

    /* Set Data Register */
    TAUJ0.CDR0 = counts;
}
