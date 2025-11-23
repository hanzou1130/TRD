/*
 * Simple test application for RH850F1KMS-1
 */

/* Global variables for testing BSS and DATA initialization */
int bss_test_var;                    /* BSS section - should be zeroed */
int data_test_var = 0x12345678;      /* DATA section - should be initialized */

/* Function prototypes */
void delay(unsigned int count);

/*
 * Main function
 */
int main(void)
{
    volatile unsigned int counter = 0;

    /* Verify BSS initialization */
    if (bss_test_var != 0) {
        /* BSS not properly cleared - error */
        while(1);
    }

    /* Verify DATA initialization */
    if (data_test_var != 0x12345678) {
        /* DATA not properly initialized - error */
        while(1);
    }

    /* Main loop */
    while(1) {
        counter++;

        /* Simple delay */
        delay(10000);

        /* Toggle or perform periodic tasks here */
    }

    return 0;
}

/*
 * Simple delay function
 */
void delay(unsigned int count)
{
    volatile unsigned int i;
    for (i = 0; i < count; i++) {
        /* Do nothing - just delay */
    }
}

/*
 * Example interrupt handler override
 * Uncomment to use custom interrupt handler
 */
/*
void _int0_handler(void)
{
    // Handle INT0 interrupt
}
*/
