# Shape Indic text with Windows' text engine; no font files are redistributed.
param([Parameter(Mandatory=$true)][string]$Manifest)
Add-Type -AssemblyName PresentationCore,PresentationFramework,WindowsBase
$taskManifest = (Resolve-Path -LiteralPath $Manifest).Path
$taskDirectory = Split-Path $taskManifest
$taskEntries = Get-Content -LiteralPath $taskManifest -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($taskEntry in $taskEntries) {
    $taskText = New-Object System.Windows.Controls.TextBlock
    $taskText.Text = $taskEntry.text
    $taskText.FontFamily = New-Object System.Windows.Media.FontFamily('Nirmala UI')
    $taskText.FontSize = 80
    $taskText.Foreground = [System.Windows.Media.Brushes]::White
    $taskText.Padding = New-Object System.Windows.Thickness(4)
    $taskText.Measure((New-Object System.Windows.Size([double]::PositiveInfinity,[double]::PositiveInfinity)))
    $taskWidth = [int][Math]::Ceiling($taskText.DesiredSize.Width)
    $taskHeight = [int][Math]::Ceiling($taskText.DesiredSize.Height)
    $taskText.Arrange((New-Object System.Windows.Rect(0,0,$taskWidth,$taskHeight)))
    $taskText.UpdateLayout()
    $taskImage = New-Object System.Windows.Media.Imaging.RenderTargetBitmap($taskWidth,$taskHeight,96,96,[System.Windows.Media.PixelFormats]::Pbgra32)
    $taskImage.Render($taskText)
    $taskEncoder = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
    $taskEncoder.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($taskImage))
    $taskTarget = Join-Path $taskDirectory $taskEntry.file
    $taskStream = [System.IO.File]::Create($taskTarget)
    try { $taskEncoder.Save($taskStream) } finally { $taskStream.Dispose() }
}
Write-Output "SHAPED_TEXT_READY=$($taskEntries.Count)"
