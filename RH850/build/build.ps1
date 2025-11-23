# Build script for RH850F1KMS-1 Startup Code
# PowerShell version for Windows

param(
	[string]$Toolchain = "ccrh"  # gcc, ghs, or ccrh
)

# Set encoding to Shift-JIS to fix mojibake in Japanese environment
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(932)

Write-Host "RH850F1KMS-1 Build Script" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$TARGET = "application"
$SRC_DIR = "..\src"
$BUILD_DIR = "."

# Auto-detect Renesas CC-RH
$CC_RH_PATH = "C:\Program Files (x86)\Renesas Electronics\CS+\CC\CC-RH\V2.07.00\bin"
$CC_RH_EXE = "ccrh"
$RLINK_EXE = "rlink"
if (Test-Path $CC_RH_PATH) {
	if ($env:Path -notlike "*$CC_RH_PATH*") {
		Write-Host "Adding CC-RH to PATH..." -ForegroundColor Yellow
		$env:Path += ";$CC_RH_PATH"
	}
	$CC_RH_EXE = "$CC_RH_PATH\ccrh.exe"
	$RLINK_EXE = "$CC_RH_PATH\rlink.exe"
}

if ($Toolchain -eq "gcc") {
	Write-Host "Using GCC toolchain..." -ForegroundColor Green
	$PREFIX = "rh850-elf-"
	$CC = "${PREFIX}gcc"
	$AS = "${PREFIX}gcc"
	$LD = "${PREFIX}gcc"
	$OBJCOPY = "${PREFIX}objcopy"
	$SIZE = "${PREFIX}size"

	$STARTUP_SRC = "$SRC_DIR\startup_rh850f1kms1.S"
	$LINKER_SCRIPT = "$SRC_DIR\rh850f1kms1.ld"

	$ASFLAGS = "-c"
	$CFLAGS = "-Wall -O2 -g -mcpu=g3m -c"
	$LDFLAGS = "-T $LINKER_SCRIPT -Wl,-Map=output.map"

}
elseif ($Toolchain -eq "ghs") {
	Write-Host "Using GHS MULTI toolchain..." -ForegroundColor Green
	$CC = "ccrh850"
	$AS = "ccrh850"
	$LD = "ccrh850"
	$OBJCOPY = "gsrec"

	$STARTUP_SRC = "$SRC_DIR\startup_rh850f1kms1_ghs.800"
	$LINKER_SCRIPT = "$SRC_DIR\rh850f1kms1_ghs.ld"

	$ASFLAGS = "-c"
	$CFLAGS = "-c -cpu=rh850g3m -O2 -g -Wall"
	$LDFLAGS = "-T $LINKER_SCRIPT -map"

}
elseif ($Toolchain -eq "ccrh") {
	Write-Host "Using Renesas CC-RH toolchain..." -ForegroundColor Green
	$CC = $CC_RH_EXE
	$AS = $CC_RH_EXE
	$LD = $RLINK_EXE

	$STARTUP_SRC = "$SRC_DIR\startup_rh850f1kms1_csp.asm"
	# Device file is handled manually in link step because it's a GNU LD script
	$DEVICE_FILE = "$SRC_DIR\rh850f1kms1_csp.dr"

	$ASFLAGS = "-c -Xcpu=g3m"
	$CFLAGS = "-c -Xcpu=g3m -Ospeed -g"
}
else {
	Write-Host "Error: Unknown toolchain '$Toolchain'" -ForegroundColor Red
	Write-Host "Valid options: gcc, ghs, ccrh" -ForegroundColor Yellow
	exit 1
}

# Check if toolchain is available
Write-Host "Checking toolchain availability..." -ForegroundColor Yellow
if ($CC -match ":\\") {
	$toolchainAvailable = Test-Path $CC
}
else {
	$toolchainAvailable = Get-Command $CC -ErrorAction SilentlyContinue
}

if (-not $toolchainAvailable) {
	Write-Host ""
	Write-Host "WARNING: Toolchain not found!" -ForegroundColor Red
	Write-Host "Command '$CC' is not available" -ForegroundColor Yellow
	Write-Host ""
	Write-Host "This is a demonstration build script." -ForegroundColor Cyan
	Write-Host "To actually build, you need to install:" -ForegroundColor Cyan

	if ($Toolchain -eq "gcc") {
		Write-Host "  - GCC for RH850 (rh850-elf-gcc)" -ForegroundColor White
	}
	elseif ($Toolchain -eq "ccrh") {
		Write-Host "  - Renesas CC-RH Compiler" -ForegroundColor White
	}
	else {
		Write-Host "  - Green Hills MULTI for RH850" -ForegroundColor White
	}

	exit 0
}

# Clean previous build
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
Remove-Item -Path "*.o", "*.obj", "*.elf", "*.bin", "*.mot", "*.map", "*.dis", "*.abs" -Force -ErrorAction SilentlyContinue

# Step 1: Assemble startup code
Write-Host ""
Write-Host "Step 1: Assembling startup code..." -ForegroundColor Yellow
if ($Toolchain -eq "ccrh") {
	$cmd = "& `"$AS`" $ASFLAGS $STARTUP_SRC"
	Write-Host "  > $cmd" -ForegroundColor Gray
	Invoke-Expression $cmd
}
else {
	$cmd = "$AS $ASFLAGS $STARTUP_SRC -o startup.o"
	Write-Host "  > $cmd" -ForegroundColor Gray
	Invoke-Expression $cmd
}

if ($LASTEXITCODE -ne 0) {
	Write-Host "Error: Assembly failed!" -ForegroundColor Red
	exit 1
}
Write-Host "  [OK] Startup object created" -ForegroundColor Green

# Step 2: Compile main.c
Write-Host ""
Write-Host "Step 2: Compiling main.c..." -ForegroundColor Yellow
if ($Toolchain -eq "ccrh") {
	$cmd = "& `"$CC`" $CFLAGS $SRC_DIR\main.c"
	Write-Host "  > $cmd" -ForegroundColor Gray
	Invoke-Expression $cmd
}
else {
	$cmd = "$CC $CFLAGS $SRC_DIR\main.c -o main.o"
	Write-Host "  > $cmd" -ForegroundColor Gray
	Invoke-Expression $cmd
}

if ($LASTEXITCODE -ne 0) {
	Write-Host "Error: Compilation failed!" -ForegroundColor Red
	exit 1
}
Write-Host "  [OK] Main object created" -ForegroundColor Green

# Step 3: Link
Write-Host ""
Write-Host "Step 3: Linking..." -ForegroundColor Yellow
if ($Toolchain -eq "ccrh") {
	# The provided .dr file is a GNU LD script, incompatible with rlink.
	# We must manually configure rlink to match the memory layout.
	# RAM: 0xFEBD0000, Size: 256KB -> End: 0xFEC10000
	# Symbols expected by startup code: __data_start, __data_end, __data_load, __bss_start, __bss_end, __stkend

	$linkArgs = @(
		"-output=$TARGET.abs",
		# Map .data to .data.R in ROM
		"-rom=.data=.data.R",
		# Place sections: .intvect at 0, others follow in ROM. RAM sections at FEBD0000.
		"-start=.intvect/0,.text,.const,.ctors,.dtors,.data.R/200,.data,.bss,.sbss,.stack/FEBD0000",
		"-nomessage", # Suppress some warnings
		"startup_rh850f1kms1_csp.obj",
		"main.obj"
	)
	Write-Host "  > & `"$LD`" $linkArgs" -ForegroundColor Gray
	& $LD $linkArgs
}
else {
	$cmd = "$LD $LDFLAGS startup.o main.o -o $TARGET.elf"
	Write-Host "  > $cmd" -ForegroundColor Gray
	Invoke-Expression $cmd
}

if ($LASTEXITCODE -ne 0) {
	Write-Host "Error: Linking failed!" -ForegroundColor Red
	exit 1
}
Write-Host "  [OK] Linked successfully" -ForegroundColor Green

# Step 4: Create binary/S-record (GCC/GHS only for now)
if ($Toolchain -ne "ccrh") {
	Write-Host ""
	if ($Toolchain -eq "gcc") {
		Write-Host "Step 4: Creating binary file..." -ForegroundColor Yellow
		$cmd = "$OBJCOPY -O binary $TARGET.elf $TARGET.bin"
		Write-Host "  > $cmd" -ForegroundColor Gray
		Invoke-Expression $cmd

		if ($LASTEXITCODE -eq 0) {
			Write-Host "  [OK] $TARGET.bin created" -ForegroundColor Green
		}

		# Show size
		Write-Host ""
		Write-Host "Memory usage:" -ForegroundColor Yellow
		& $SIZE "$TARGET.elf"

	}
	else {
		Write-Host "Step 4: Creating Motorola S-record..." -ForegroundColor Yellow
		$cmd = "$OBJCOPY -o $TARGET.mot $TARGET.elf"
		Write-Host "  > $cmd" -ForegroundColor Gray
		Invoke-Expression $cmd

		if ($LASTEXITCODE -eq 0) {
			Write-Host "  [OK] $TARGET.mot created" -ForegroundColor Green
		}
	}
}

# Summary
Write-Host ""
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Output files:" -ForegroundColor Cyan
Get-ChildItem -Path "*.elf", "*.bin", "*.mot", "*.map", "*.abs" -ErrorAction SilentlyContinue | ForEach-Object {
	$size = [math]::Round($_.Length / 1KB, 2)
	Write-Host "  $($_.Name) - $size KB" -ForegroundColor White
}
Write-Host ""
