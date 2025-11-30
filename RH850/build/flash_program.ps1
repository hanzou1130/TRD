Write-Host "RH850 Flash Programming Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if HEX file exists
if (-not (Test-Path $HexFile)) {
	Write-Host "ERROR: HEX file not found: $HexFile" -ForegroundColor Red
	Write-Host "Please run build.ps1 first to generate the HEX file." -ForegroundColor Yellow
	exit 1
}

$hexSize = (Get-Item $HexFile).Length
Write-Host "HEX File: $HexFile ($hexSize bytes)" -ForegroundColor Green

# Check for Renesas Flash Programmer
$RFP_PATHS = @(
	"C:\Program Files (x86)\Renesas Electronics\Programming Tools\Renesas Flash Programmer V3.19\rfp-cli.exe",
	"C:\Program Files\Renesas Electronics\Programming Tools\Renesas Flash Programmer V3.19\rfp-cli.exe",
	"C:\Program Files (x86)\Renesas Electronics\Programming Tools\Renesas Flash Programmer\rfp-cli.exe"
)

$RFP_CLI = $null
foreach ($path in $RFP_PATHS) {
	if (Test-Path $path) {
		$RFP_CLI = $path
		break
	}
}

if (-not $RFP_CLI) {
	Write-Host ""
	Write-Host "ERROR: Renesas Flash Programmer CLI not found!" -ForegroundColor Red
	Write-Host "Searched paths:" -ForegroundColor Yellow
	foreach ($path in $RFP_PATHS) {
		Write-Host "  - $path" -ForegroundColor Gray
	}
	Write-Host ""
	Write-Host "Please install Renesas Flash Programmer V3.19 or later." -ForegroundColor Yellow
	exit 1
}

Write-Host "RFP CLI: $RFP_CLI" -ForegroundColor Green
Write-Host ""

# Check E2 emulator connection
Write-Host "Checking E2 emulator connection..." -ForegroundColor Yellow
$e2Device = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*E2*" -and $_.Status -eq "OK" }
if ($e2Device) {
	Write-Host "  [OK] E2 emulator detected: $($e2Device.FriendlyName)" -ForegroundColor Green
}
else {
	Write-Host "  [WARN] E2 emulator not detected in Device Manager" -ForegroundColor Yellow
	Write-Host "  Proceeding anyway..." -ForegroundColor Gray
}
Write-Host ""

# Execute flash programming
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Flash Programming..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target Device: $Device (RH850/F1KM-S1)" -ForegroundColor White
Write-Host "Emulator: $Tool (S/N: $SerialNumber)" -ForegroundColor White
Write-Host "Interface: 2-wire UART" -ForegroundColor White
Write-Host "Main Clock: 20 MHz" -ForegroundColor White
Write-Host "Supply Voltage: 3.3V" -ForegroundColor White
Write-Host ""

# Build command line arguments for rfp-cli
$toolArg = if ($SerialNumber) { "${Tool}:${SerialNumber}" } else { $Tool }

$rfpArgs = @(
	"-d", $Device,
	"-t", $toolArg,
	(Resolve-Path $HexFile).Path
)

# Run rfp-cli
Write-Host "Executing RFP CLI..." -ForegroundColor Yellow
$cmdLine = "`"$RFP_CLI`" " + ($rfpArgs -join " ")
Write-Host "> $cmdLine" -ForegroundColor Gray
Write-Host ""

& "$RFP_CLI" $rfpArgs

if ($LASTEXITCODE -eq 0) {
	Write-Host ""
	Write-Host "================================" -ForegroundColor Green
	Write-Host "Flash Programming Successful!" -ForegroundColor Green
	Write-Host "================================" -ForegroundColor Green
	Write-Host ""
	Write-Host "The test program has been written to the RH850 board." -ForegroundColor White
	Write-Host "You can now start debugging." -ForegroundColor White
	Write-Host ""
}
else {
	Write-Host ""
	Write-Host "================================" -ForegroundColor Red
	Write-Host "Flash Programming Failed!" -ForegroundColor Red
	Write-Host "================================" -ForegroundColor Red
	Write-Host ""
	Write-Host "Common issues:" -ForegroundColor Yellow
	Write-Host "  1. E2 emulator not connected or recognized" -ForegroundColor White
	Write-Host "  2. FLMD0 pin not connected to GND (required for programming)" -ForegroundColor White
	Write-Host "  3. Target board power supply issue" -ForegroundColor White
	Write-Host "  4. Wrong main clock frequency (should be 20MHz)" -ForegroundColor White
	Write-Host ""
	Write-Host "Please check:" -ForegroundColor Yellow
	Write-Host "  - E2 emulator USB connection" -ForegroundColor White
	Write-Host "  - Target board power (3.3V)" -ForegroundColor White
	Write-Host "  - FLMD0 pin connection to GND" -ForegroundColor White
	Write-Host ""

	# Show rfp-cli help for reference
	Write-Host "For more information, run:" -ForegroundColor Yellow
	Write-Host "  `"$RFP_CLI`" -help" -ForegroundColor Gray
	Write-Host ""
	exit 1
}
