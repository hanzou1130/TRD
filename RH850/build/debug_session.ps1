# Debug Session Script for RH850F1KMS-1
# Automates: Build -> Flash -> Debug

param(
	[switch]$SkipBuild = $false,
	[switch]$SkipFlash = $false,
	[switch]$OpenCSPlus = $false
)

# Set encoding to Shift-JIS
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(932)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "RH850 Debug Session Automation" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$startDir = Get-Location

try {
	# Step 1: Build
	if (-not $SkipBuild) {
		Write-Host "[1/3] Building project..." -ForegroundColor Yellow
		Write-Host ""

		& ".\build.ps1"

		if ($LASTEXITCODE -ne 0) {
			throw "Build failed with exit code $LASTEXITCODE"
		}

		Write-Host ""
		Write-Host "  [OK] Build completed" -ForegroundColor Green
		Write-Host ""
	}
 else {
		Write-Host "[1/3] Skipping build (using existing binary)" -ForegroundColor Yellow
		Write-Host ""
	}

	# Step 2: Flash Programming
	if (-not $SkipFlash) {
		Write-Host "[2/3] Programming flash memory..." -ForegroundColor Yellow
		Write-Host ""

		if (-not (Test-Path "application.hex")) {
			throw "HEX file not found. Please build first."
		}

		& ".\flash_program.ps1"

		if ($LASTEXITCODE -ne 0) {
			throw "Flash programming failed with exit code $LASTEXITCODE"
		}

		Write-Host ""
		Write-Host "  [OK] Flash programming completed" -ForegroundColor Green
		Write-Host ""
	}
 else {
		Write-Host "[2/3] Skipping flash programming" -ForegroundColor Yellow
		Write-Host ""
	}

	# Step 3: Start Debug Session
	Write-Host "[3/3] Starting debug session..." -ForegroundColor Yellow
	Write-Host ""

	if ($OpenCSPlus) {
		# Option A: Open CS+ IDE
		Write-Host "Opening CS+ IDE..." -ForegroundColor Cyan

		$CS_PLUS_PATHS = @(
			"C:\Program Files (x86)\Renesas Electronics\CS+\CC\CubeSuite+.exe",
			"C:\Program Files\Renesas Electronics\CS+\CC\CubeSuite+.exe"
		)

		$CS_PLUS = $null
		foreach ($path in $CS_PLUS_PATHS) {
			if (Test-Path $path) {
				$CS_PLUS = $path
				break
			}
		}

		if ($CS_PLUS) {
			$projectPath = "..\CS_Project\RH850.mtpj"
			if (Test-Path $projectPath) {
				Write-Host "Launching CS+ with project: $projectPath" -ForegroundColor White
				Start-Process $CS_PLUS -ArgumentList $projectPath
				Write-Host ""
				Write-Host "  [OK] CS+ launched" -ForegroundColor Green
				Write-Host ""
				Write-Host "Next steps in CS+:" -ForegroundColor Yellow
				Write-Host "  1. Debug -> Download (F3)" -ForegroundColor White
				Write-Host "  2. Set breakpoint at main()" -ForegroundColor White
				Write-Host "  3. Go (F5)" -ForegroundColor White
			}
			else {
				Write-Host "  [WARN] CS+ project not found at: $projectPath" -ForegroundColor Yellow
				Start-Process $CS_PLUS
			}
		}
		else {
			Write-Host "  [WARN] CS+ not found. Please open manually." -ForegroundColor Yellow
		}
	}
 else {
		# Option B: VS Code Debug Instructions
		Write-Host "VS Code Debug Setup:" -ForegroundColor Cyan
		Write-Host ""
		Write-Host "To debug in VS Code:" -ForegroundColor Yellow
		Write-Host "  1. Install 'Renesas Platform' extension" -ForegroundColor White
		Write-Host "  2. Install Renesas Debug Extension via Quick Install" -ForegroundColor White
		Write-Host "  3. Open Run and Debug panel (Ctrl+Shift+D)" -ForegroundColor White
		Write-Host "  4. Select 'RH850 E2 Debug' configuration" -ForegroundColor White
		Write-Host "  5. Press F5 to start debugging" -ForegroundColor White
		Write-Host ""
		Write-Host "Alternatively, use CS+ IDE:" -ForegroundColor Yellow
		Write-Host "  Run: .\debug_session.ps1 -OpenCSPlus" -ForegroundColor White
		Write-Host ""

		# Check if VS Code is available
		$vscode = Get-Command code -ErrorAction SilentlyContinue
		if ($vscode) {
			Write-Host "Opening VS Code..." -ForegroundColor Cyan
			Start-Process "code" -ArgumentList ".."
		}
	}

	Write-Host ""
	Write-Host "================================" -ForegroundColor Green
	Write-Host "Debug Session Ready!" -ForegroundColor Green
	Write-Host "================================" -ForegroundColor Green
	Write-Host ""

	Write-Host "Program Information:" -ForegroundColor Cyan
	Write-Host "  - Test Program: main.c" -ForegroundColor White
	Write-Host "  - TAUJ0 Timer: 1ms interval" -ForegroundColor White
	Write-Host "  - BSS/DATA: Auto-initialized" -ForegroundColor White
	Write-Host ""

	Write-Host "Debug Points to Check:" -ForegroundColor Cyan
	Write-Host "  - bss_test_var should be 0" -ForegroundColor White
	Write-Host "  - data_test_var should be 0x12345678" -ForegroundColor White
	Write-Host "  - counter increments in main loop" -ForegroundColor White
	Write-Host ""

}
catch {
	Write-Host ""
	Write-Host "================================" -ForegroundColor Red
	Write-Host "Error: $_" -ForegroundColor Red
	Write-Host "================================" -ForegroundColor Red
	Write-Host ""
	exit 1
}
finally {
	Set-Location $startDir
}
