$w = New-Object -ComObject WScript.Shell
Write-Host "☕ Caffeine Mode: ON" -ForegroundColor Cyan
Write-Host "Your PC will stay awake while this window is open."
Write-Host "Press Ctrl+C to finish your training session."

while ($true) {
    # Send F15 key (phantom key) every 60 seconds
    $w.SendKeys('{F15}')
    Start-Sleep -Seconds 60
}
