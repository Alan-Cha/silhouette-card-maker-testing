<#
.SYNOPSIS
    Batch convert DXF files to Silhouette Studio .studio3 format using GUI automation.

.DESCRIPTION
    This script automates Silhouette Studio to open DXF files and save them as .studio3.
    It uses Windows UI Automation and SendKeys for reliable automation.

.PARAMETER InputFolder
    Folder containing DXF files to convert.

.PARAMETER OutputFolder
    Output folder for .studio3 files. Defaults to InputFolder.

.PARAMETER SilhouetteStudioPath
    Path to Silhouette Studio executable.

.EXAMPLE
    .\dxf_to_studio3.ps1 -InputFolder "C:\DXF_Files" -OutputFolder "C:\Studio3_Files"

.NOTES
    - Do not use the computer during conversion
    - Press Ctrl+C to abort
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InputFolder,

    [string]$OutputFolder = $null,

    [string]$SilhouetteStudioPath = "C:\Program Files\Silhouette America\Silhouette Studio\Silhouette Studio.exe"
)

# Load required assemblies for UI Automation
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

# Configuration
$StartupWait = 8
$ActionDelay = 500  # milliseconds
$SaveDelay = 2000

function Send-KeysToWindow {
    param([string]$Keys)
    [System.Windows.Forms.SendKeys]::SendWait($Keys)
    Start-Sleep -Milliseconds $ActionDelay
}

function Set-ClipboardText {
    param([string]$Text)
    [System.Windows.Forms.Clipboard]::SetText($Text)
}

function Start-SilhouetteStudio {
    Write-Host "Starting Silhouette Studio..."

    if (-not (Test-Path $SilhouetteStudioPath)) {
        throw "Silhouette Studio not found at: $SilhouetteStudioPath"
    }

    $process = Start-Process -FilePath $SilhouetteStudioPath -PassThru
    Write-Host "Waiting $StartupWait seconds for startup..."
    Start-Sleep -Seconds $StartupWait

    return $process
}

function Stop-SilhouetteStudio {
    param($Process)
    Write-Host "Closing Silhouette Studio..."

    # Try to close gracefully with Alt+F4
    Send-KeysToWindow "%{F4}"
    Start-Sleep -Milliseconds 500

    # Handle save dialog - press N for No
    Send-KeysToWindow "n"
    Start-Sleep -Seconds 1

    # Force kill if still running
    if (-not $Process.HasExited) {
        $Process | Stop-Process -Force -ErrorAction SilentlyContinue
    }
}

function Open-DXFFile {
    param([string]$FilePath)

    $FullPath = (Resolve-Path $FilePath).Path
    Write-Host "Opening: $FullPath"

    # Ctrl+O to open file dialog
    Send-KeysToWindow "^o"
    Start-Sleep -Milliseconds ($ActionDelay * 2)

    # Clear existing text and paste file path
    Send-KeysToWindow "^a"
    Start-Sleep -Milliseconds 100

    Set-ClipboardText $FullPath
    Send-KeysToWindow "^v"
    Start-Sleep -Milliseconds $ActionDelay

    # Press Enter to open
    Send-KeysToWindow "{ENTER}"
    Start-Sleep -Milliseconds ($ActionDelay * 3)
}

function Save-AsStudio3 {
    param([string]$OutputPath)

    $FullPath = [System.IO.Path]::GetFullPath($OutputPath)

    # Ensure .studio3 extension
    if (-not $FullPath.ToLower().EndsWith(".studio3")) {
        $FullPath = [System.IO.Path]::ChangeExtension($FullPath, ".studio3")
    }

    Write-Host "Saving as: $FullPath"

    # Ctrl+Shift+S for Save As
    Send-KeysToWindow "^+s"
    Start-Sleep -Milliseconds ($ActionDelay * 2)

    # Clear and paste output path
    Send-KeysToWindow "^a"
    Start-Sleep -Milliseconds 100

    Set-ClipboardText $FullPath
    Send-KeysToWindow "^v"
    Start-Sleep -Milliseconds $ActionDelay

    # Press Enter to save
    Send-KeysToWindow "{ENTER}"
    Start-Sleep -Milliseconds $SaveDelay

    # Handle overwrite confirmation
    if (Test-Path $FullPath) {
        Start-Sleep -Milliseconds 300
        Send-KeysToWindow "y"
        Start-Sleep -Milliseconds $SaveDelay
    }
}

function New-Document {
    # Ctrl+N for new document
    Send-KeysToWindow "^n"
    Start-Sleep -Milliseconds $ActionDelay

    # Handle save dialog - press N for No
    Send-KeysToWindow "n"
    Start-Sleep -Milliseconds $ActionDelay
}

function Convert-DXFToStudio3 {
    param(
        [string]$InputDXF,
        [string]$OutputStudio3
    )

    Open-DXFFile -FilePath $InputDXF
    Save-AsStudio3 -OutputPath $OutputStudio3
    New-Document
}

# Main script
try {
    # Validate input folder
    if (-not (Test-Path $InputFolder)) {
        throw "Input folder does not exist: $InputFolder"
    }

    # Set output folder
    if ([string]::IsNullOrEmpty($OutputFolder)) {
        $OutputFolder = $InputFolder
    }
    if (-not (Test-Path $OutputFolder)) {
        New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null
    }

    # Find DXF files
    $dxfFiles = Get-ChildItem -Path $InputFolder -Filter "*.dxf" | Sort-Object Name

    if ($dxfFiles.Count -eq 0) {
        Write-Host "No DXF files found in: $InputFolder"
        exit 0
    }

    Write-Host "Found $($dxfFiles.Count) DXF files to convert:"
    foreach ($dxf in $dxfFiles) {
        $outputFile = Join-Path $OutputFolder ($dxf.BaseName + ".studio3")
        Write-Host "  $($dxf.Name) -> $([System.IO.Path]::GetFileName($outputFile))"
    }

    Write-Host ""
    Write-Host "=" * 60
    Write-Host "IMPORTANT: This script will take control of your mouse/keyboard."
    Write-Host "Do not use the computer during conversion."
    Write-Host "Press Ctrl+C to abort."
    Write-Host "=" * 60
    Write-Host ""

    $response = Read-Host "Proceed with conversion? [y/N]"
    if ($response.ToLower() -ne 'y') {
        Write-Host "Aborted."
        exit 0
    }

    # Start Silhouette Studio
    $process = Start-SilhouetteStudio

    $successful = 0
    $failed = 0
    $total = $dxfFiles.Count

    foreach ($i in 0..($dxfFiles.Count - 1)) {
        $dxf = $dxfFiles[$i]
        $outputFile = Join-Path $OutputFolder ($dxf.BaseName + ".studio3")

        Write-Host ""
        Write-Host "[$($i + 1)/$total] Converting: $($dxf.Name)"

        try {
            Convert-DXFToStudio3 -InputDXF $dxf.FullName -OutputStudio3 $outputFile
            $successful++
            Write-Host "  Success!"
        }
        catch {
            $failed++
            Write-Host "  FAILED: $_" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "=" * 60
    Write-Host "Conversion complete: $successful successful, $failed failed"

}
catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
finally {
    if ($process) {
        Stop-SilhouetteStudio -Process $process
    }
}
