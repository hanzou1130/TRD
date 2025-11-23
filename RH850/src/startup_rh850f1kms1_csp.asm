;----------------------------------------------------------------------
; Startup file for RH850F1KMS-1
; Converted for Renesas CC-RH
;----------------------------------------------------------------------

;----------------------------------------------------------------------
; Symbol Definitions (Dummy values for build)
;----------------------------------------------------------------------
__data_start    .set    0xFEBD0000
__data_end      .set    0xFEBD0000
__data_load     .set    0xFEBD0000
__bss_start     .set    0xFEBD0000
__bss_end       .set    0xFEBD0000
__stkend        .set    0xFEC10000

    .public _start
    .public _exit

    .section .text, TEXT

_start:
    ; Initialize Stack Pointer
    mov     __stkend, sp

    ; Initialize GP (Global Pointer)
    ; mov     __gp, gp  ; GP not used in this simple example

    ; Initialize TP (Text Pointer)
    ; mov     __tp, tp  ; TP not used

    ;------------------------------------------------------------------
    ; Data Initialization (ROM -> RAM)
    ;------------------------------------------------------------------
    mov     high(__data_load), r6
    mov     low(__data_load), r6
    mov     high(__data_start), r7
    mov     low(__data_start), r7
    mov     high(__data_end), r8
    mov     low(__data_end), r8

    ; Calculate size
    mov     r8, r9
    sub     r7, r9
    cmp     0, r9
    bz      .L_bss_init

.L_data_loop:
    ld.b    [r6], r10
    st.b    r10, [r7]
    add     1, r6
    add     1, r7
    add     -1, r9
    bnz     .L_data_loop

    ;------------------------------------------------------------------
    ; BSS Initialization (Zero out)
    ;------------------------------------------------------------------
.L_bss_init:
    mov     high(__bss_start), r6
    mov     low(__bss_start), r6
    mov     high(__bss_end), r7
    mov     low(__bss_end), r7

    ; Calculate size
    mov     r7, r8
    sub     r6, r8
    cmp     0, r8
    bz      .L_main

.L_bss_loop:
    st.b    r0, [r6]
    add     1, r6
    add     -1, r8
    bnz     .L_bss_loop

    ;------------------------------------------------------------------
    ; Call Main
    ;------------------------------------------------------------------
.L_main:
    jarl    _main, lp

_exit:
    br      _exit

    ; .end removed
