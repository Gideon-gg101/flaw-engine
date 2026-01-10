# Zip the Flaw engine for cloud upload
$rootPath = Resolve-Path "."
$destination = Join-Path (Get-Item $rootPath).Parent.FullName "flaw_cloud_bundle.zip"

if (Test-Path $destination) { Remove-Item $destination -Force }

Write-Host "Gathering files (excluding builds and caches)..."
$files = Get-ChildItem -Path . -Recurse | Where-Object { 
    $_.FullName -notmatch "\\build" -and 
    $_.FullName -notmatch "\\build2" -and 
    $_.FullName -notmatch "__pycache__" -and 
    $_.Extension -notmatch "zip|pyd|exe|dll"
}

Write-Host "Zipping project..."
$files | Compress-Archive -DestinationPath $destination -Force

if (Test-Path $destination) {
    Write-Host "Success! Bundle created at: $destination"
    Write-Host "Upload this ZIP file to Google Colab to start training."
}
else {
    Write-Host "Error: Failed to create bundle."
}
