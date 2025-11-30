/***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products.
* No other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws.
***********************************************************************************************************************/

#ifndef TAUJ0_REGS_H
#define TAUJ0_REGS_H

#include <stdint.h>

/* TAUJ0 Base Address */
#define TAUJ0_BASE_ADDR  (0xFFE50000UL)

/* Register Offsets */
#define TAUJ0_CDR0_OFFSET  (0x0000UL)
#define TAUJ0_CNT0_OFFSET  (0x0000UL) /* Same offset as CDR0, access depends on mode */
#define TAUJ0_CMOR0_OFFSET (0x0080UL)
#define TAUJ0_CMUR0_OFFSET (0x00C0UL)
#define TAUJ0_CSR0_OFFSET  (0x0040UL)
#define TAUJ0_CSC0_OFFSET  (0x0044UL)
#define TAUJ0_TS0_OFFSET   (0x0014UL)
#define TAUJ0_TT0_OFFSET   (0x0018UL)
#define TAUJ0_TO0_OFFSET   (0x0010UL)
#define TAUJ0_TOE0_OFFSET  (0x001CUL)
#define TAUJ0_TOL0_OFFSET  (0x0020UL)
#define TAUJ0_RDE0_OFFSET  (0x0024UL)
#define TAUJ0_RDM0_OFFSET  (0x0028UL)

/* Register Definitions */
typedef struct {
    volatile uint32_t CDR0;  /* Channel Data Register 0 */
    volatile uint8_t  dummy1[0x10 - 0x04];
    volatile uint32_t TO0;   /* Timer Output Register 0 */
    volatile uint32_t TS0;   /* Timer Start Register 0 */
    volatile uint32_t TT0;   /* Timer Stop Register 0 */
    volatile uint32_t TOE0;  /* Timer Output Enable Register 0 */
    volatile uint32_t TOL0;  /* Timer Output Level Register 0 */
    volatile uint32_t RDE0;  /* Reload Data Enable Register 0 */
    volatile uint32_t RDM0;  /* Reload Data Mode Register 0 */
    volatile uint8_t  dummy2[0x40 - 0x2C];
    volatile uint32_t CSR0;  /* Channel Status Register 0 */
    volatile uint32_t CSC0;  /* Channel Status Clear Register 0 */
    volatile uint8_t  dummy3[0x80 - 0x48];
    volatile uint32_t CMOR0; /* Channel Mode OS Register 0 */
    volatile uint8_t  dummy4[0xC0 - 0x84];
    volatile uint32_t CMUR0; /* Channel Mode User Register 0 */
} TAUJ0_Regs_t;

#define TAUJ0  (*(TAUJ0_Regs_t *)TAUJ0_BASE_ADDR)

/* Bit Definitions */
/* CMOR0 */
#define TAUJ0_CMOR0_CKS_Pos   (14U)
#define TAUJ0_CMOR0_CKS_Msk   (0x3UL << TAUJ0_CMOR0_CKS_Pos)
#define TAUJ0_CMOR0_MD0_Pos   (0U)
#define TAUJ0_CMOR0_MD0_Msk   (0x1UL << TAUJ0_CMOR0_MD0_Pos)

/* TS0 */
#define TAUJ0_TS0_TS0_Pos     (0U)
#define TAUJ0_TS0_TS0_Msk     (0x1UL << TAUJ0_TS0_TS0_Pos)

/* TT0 */
#define TAUJ0_TT0_TT0_Pos     (0U)
#define TAUJ0_TT0_TT0_Msk     (0x1UL << TAUJ0_TT0_TT0_Pos)

#endif /* TAUJ0_REGS_H */
