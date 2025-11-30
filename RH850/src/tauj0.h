/***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products.
* No other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws.
***********************************************************************************************************************/

#ifndef TAUJ0_H
#define TAUJ0_H

#include <stdint.h>

/* API Function Prototypes */

/**
 * @brief Initialize TAUJ0 channel 0 as an interval timer.
 *
 * @param interval_us Interval in microseconds.
 */
void TAUJ0_Init(uint32_t interval_us);

/**
 * @brief Start TAUJ0 channel 0 counter.
 */
void TAUJ0_Start(void);

/**
 * @brief Stop TAUJ0 channel 0 counter.
 */
void TAUJ0_Stop(void);

/**
 * @brief Set the interval for TAUJ0 channel 0.
 *
 * @param interval_us Interval in microseconds.
 */
void TAUJ0_SetInterval(uint32_t interval_us);

#endif /* TAUJ0_H */
