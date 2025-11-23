/*
 * RH850F1KMS-1 Linker Script
 *
 * Memory layout and section placement for RH850F1KMS-1 microcontroller
 * Based on RH850F1KM-S4 memory map extracted from hardware manual database
 *
 * Memory Regions:
 * - Code Flash: 0x00000000 - (size depends on variant, typically 4MB)
 * - Local RAM (CPU1): 0xFEBD0000 - 0xFEBD7FFF (256 KB)
 * - Global RAM: 0xFEEF0000 - 0xFEEF3FFF (64 KB)
 * - Retention RAM: 0xFEF00000 - 0xFEF0FFFF (64 KB)
 */

OUTPUT_FORMAT("elf32-v850-rh850", "elf32-v850-rh850", "elf32-v850-rh850")
OUTPUT_ARCH(v850:rh850)
ENTRY(_reset_handler)

/* Memory Regions Definition */
MEMORY
{
    /* Code Flash - Adjust size based on your specific device variant
     * RH850F1KM-S4 typically has 4MB Flash
     * Start address: 0x00000000
     */
    FLASH (rx)   : ORIGIN = 0x00000000, LENGTH = 4M

    /* Local RAM for CPU1 - 256 KB
     * Address range: 0xFEBD0000 - 0xFEBD7FFF
     * Used for stack, heap, and general data
     */
    RAM (rwx)    : ORIGIN = 0xFEBD0000, LENGTH = 256K

    /* Global RAM - 64 KB (optional, can be used for shared data)
     * Address range: 0xFEEF0000 - 0xFEEF3FFF
     */
    GLOBAL_RAM (rwx) : ORIGIN = 0xFEEF0000, LENGTH = 64K

    /* Retention RAM - 64 KB (optional, data retained in low power modes)
     * Address range: 0xFEF00000 - 0xFEF0FFFF
     */
    RETENTION_RAM (rwx) : ORIGIN = 0xFEF00000, LENGTH = 64K
}

/* Stack size configuration */
__stack_size = DEFINED(__stack_size) ? __stack_size : 4K;
__heap_size = DEFINED(__heap_size) ? __heap_size : 4K;

SECTIONS
{
    /*
     * Interrupt Vector Table
     * Must be placed at the beginning of Flash
     * Must be 512-byte aligned for RBASE/EBASE registers
     */
    .vectors :
    {
        KEEP(*(.vectors))
        . = ALIGN(512);
    } > FLASH

    /*
     * Program Code Section
     * Contains all executable code
     */
    .text :
    {
        *(.text.reset_handler)
        *(.text.default_handlers)
        *(.text)
        *(.text.*)

        /* C++ constructor/destructor tables */
        KEEP(*(.init))
        KEEP(*(.fini))

        /* .ctors */
        *crtbegin.o(.ctors)
        *crtbegin?.o(.ctors)
        *(EXCLUDE_FILE(*crtend?.o *crtend.o) .ctors)
        *(SORT(.ctors.*))
        *(.ctors)

        /* .dtors */
        *crtbegin.o(.dtors)
        *crtbegin?.o(.dtors)
        *(EXCLUDE_FILE(*crtend?.o *crtend.o) .dtors)
        *(SORT(.dtors.*))
        *(.dtors)

        . = ALIGN(4);
    } > FLASH

    /*
     * Read-only Data Section
     * Contains constants and strings
     */
    .rodata :
    {
        *(.rodata)
        *(.rodata.*)
        . = ALIGN(4);
    } > FLASH

    /*
     * Exception handling frames (C++)
     */
    .eh_frame :
    {
        KEEP(*(.eh_frame))
        . = ALIGN(4);
    } > FLASH

    /*
     * ARM.exidx section (for exception handling)
     */
    .ARM.exidx :
    {
        __exidx_start = .;
        *(.ARM.exidx* .gnu.linkonce.armexidx.*)
        __exidx_end = .;
    } > FLASH

    /* End of Flash sections */
    __etext = .;

    /*
     * Initialized Data Section
     * Loaded from Flash, copied to RAM at startup
     */
    .data : AT(__etext)
    {
        __data_start = .;
        *(.data)
        *(.data.*)
        . = ALIGN(4);
        __data_end = .;
    } > RAM

    /* Load address of .data section in Flash */
    __data_load = LOADADDR(.data);

    /*
     * Uninitialized Data Section (BSS)
     * Zeroed at startup
     */
    .bss (NOLOAD) :
    {
        __bss_start = .;
        *(.bss)
        *(.bss.*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > RAM

    /*
     * Heap Section
     * Used for dynamic memory allocation
     */
    .heap (NOLOAD) :
    {
        __heap_start = .;
        . = . + __heap_size;
        __heap_end = .;
        . = ALIGN(4);
    } > RAM

    /*
     * Stack Section
     * Grows downward from top of RAM
     * Stack pointer initialized to __stack_top in startup code
     */
    .stack (NOLOAD) :
    {
        . = ALIGN(8);
        __stack_bottom = .;
        . = . + __stack_size;
        __stack_top = .;
    } > RAM

    /*
     * Global RAM Section (optional)
     * Can be used for shared data between cores or DMA buffers
     */
    .global_data (NOLOAD) :
    {
        __global_data_start = .;
        *(.global_data)
        *(.global_data.*)
        . = ALIGN(4);
        __global_data_end = .;
    } > GLOBAL_RAM

    /*
     * Retention RAM Section (optional)
     * Data retained during low-power modes
     */
    .retention_data (NOLOAD) :
    {
        __retention_data_start = .;
        *(.retention_data)
        *(.retention_data.*)
        . = ALIGN(4);
        __retention_data_end = .;
    } > RETENTION_RAM

    /*
     * Debug Sections
     * Not loaded into device, used for debugging only
     */
    .comment 0 : { *(.comment) }
    .debug_abbrev 0 : { *(.debug_abbrev) }
    .debug_aranges 0 : { *(.debug_aranges) }
    .debug_frame 0 : { *(.debug_frame) }
    .debug_info 0 : { *(.debug_info) }
    .debug_line 0 : { *(.debug_line) }
    .debug_loc 0 : { *(.debug_loc) }
    .debug_macinfo 0 : { *(.debug_macinfo) }
    .debug_pubnames 0 : { *(.debug_pubnames) }
    .debug_pubtypes 0 : { *(.debug_pubtypes) }
    .debug_ranges 0 : { *(.debug_ranges) }
    .debug_str 0 : { *(.debug_str) }

    /* Discard unwanted sections */
    /DISCARD/ :
    {
        *(.note.GNU-stack)
        *(.gnu_debuglink)
        *(.gnu.lto_*)
    }
}

/*
 * Provide symbols for memory usage calculation
 */
__flash_used = __etext;
__ram_used = __stack_top - ORIGIN(RAM);
__flash_size = LENGTH(FLASH);
__ram_size = LENGTH(RAM);
