# Flat OLED example PNGs — active display area only (no bezel / photo).
# Dual-colour SSD1306 style: yellow rows 0-15, blue rows 16-63.

Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = "Stop"
$OutDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Scale = 4
$W = 128
$H = 64

$Yellow = [System.Drawing.Color]::FromArgb(255, 210, 0)
$Blue = [System.Drawing.Color]::FromArgb(70, 170, 255)
$Black = [System.Drawing.Color]::Black

function Format-Num([double]$v) {
    if ($v -gt 999.9) { $v = 999.9 }
    if ($v -lt -999.9) { $v = -999.9 }
    $inv = [System.Globalization.CultureInfo]::InvariantCulture
    return [string]::Format($inv, "{0,6:0.0}", $v)
}

function Save-OledExample {
    param(
        [string]$Path,
        [string]$Status,
        [double]$Pos,
        [double]$Spd,
        [double]$Acc,
        [string]$App
    )

    $src = New-Object System.Drawing.Bitmap $W, $H
    $g = [System.Drawing.Graphics]::FromImage($src)
    $g.Clear($Black)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::SingleBitPerPixelGridFit

    $fontBig = New-Object System.Drawing.Font "Consolas", 7, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
    $fontSmall = New-Object System.Drawing.Font "Consolas", 6, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
    $brushY = New-Object System.Drawing.SolidBrush $Yellow
    $brushB = New-Object System.Drawing.SolidBrush $Blue

    if ($Status) {
        $g.DrawString($Status, $fontBig, $brushY, 0, 3)
    }

    $labels = @(
        @{ Y = 17; L = "Pos"; N = (Format-Num $Pos); U = "mm" },
        @{ Y = 27; L = "Spd"; N = (Format-Num $Spd); U = "mm/s" },
        @{ Y = 37; L = "Acc*"; N = (Format-Num $Acc); U = "mm/s2" }
    )
    foreach ($row in $labels) {
        $g.DrawString($row.L, $fontSmall, $brushB, 0, ($row.Y + 1))
        $g.DrawString($row.N, $fontBig, $brushB, 26, $row.Y)
        $g.DrawString($row.U, $fontSmall, $brushB, 76, ($row.Y + 1))
    }
    if ($App) {
        $g.DrawString($App, $fontSmall, $brushB, 0, 48)
    }

    # Nearest-neighbour upscale for docs readability
    $dst = New-Object System.Drawing.Bitmap ($W * $Scale), ($H * $Scale)
    $gd = [System.Drawing.Graphics]::FromImage($dst)
    $gd.Clear($Black)
    $gd.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $gd.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    $gd.DrawImage($src, 0, 0, ($W * $Scale), ($H * $Scale))

    $dst.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $gd.Dispose(); $dst.Dispose()
    $g.Dispose(); $src.Dispose()
    $fontBig.Dispose(); $fontSmall.Dispose()
    $brushY.Dispose(); $brushB.Dispose()
    Write-Host "wrote $Path"
}

Save-OledExample (Join-Path $OutDir "oled-idle.png") "" 142.5 0.0 200.0 "Ready"
Save-OledExample (Join-Path $OutDir "oled-moving.png") "" 87.4 -42.0 150.0 "Cruising L"
Save-OledExample (Join-Path $OutDir "oled-homing.png") "HOMING" 12.3 -5.0 200.0 "Homing..."
Save-OledExample (Join-Path $OutDir "oled-disabled.png") "DISABLED" 200.0 0.0 200.0 "Disabled"
Save-OledExample (Join-Path $OutDir "oled-limit.png") "LIMIT" 300.0 0.0 200.0 "Soft limit"
