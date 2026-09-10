#!/usr/bin/env pwsh

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$packagingRoot = $PSScriptRoot
$spectool = Get-Command spectool -ErrorAction SilentlyContinue

if (-not $spectool) {
    throw 'spectool was not found. Install the Fedora rpmdevtools package first.'
}

$packageDirectories = @(Get-ChildItem -LiteralPath $packagingRoot -Directory |
    Where-Object {
        @(Get-ChildItem -LiteralPath $_.FullName -Filter '*.spec' -File).Count -gt 0
    })

if ($packageDirectories.Count -eq 0) {
    Write-Warning "No package directories containing a .spec file were found in $packagingRoot."
    exit 0
}

foreach ($packageDirectory in $packageDirectories) {
    $specFiles = Get-ChildItem -LiteralPath $packageDirectory.FullName -Filter '*.spec' -File |
        Sort-Object Name

    Push-Location -LiteralPath $packageDirectory.FullName
    try {
        foreach ($specFile in $specFiles) {
            Write-Host "Fetching sources for $($packageDirectory.Name)/$($specFile.Name)"
            & $spectool.Source -g $specFile.Name
            if ($LASTEXITCODE -ne 0) {
                throw "spectool failed for $($packageDirectory.Name)/$($specFile.Name) with exit code $LASTEXITCODE."
            }
        }
    }
    finally {
        Pop-Location
    }
}
