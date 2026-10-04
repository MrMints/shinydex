# Reproducible Windows build using the compiler included with .NET Framework.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$outputDirectory = Join-Path $projectRoot 'dist'
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
$bundlePath = Join-Path $outputDirectory 'web.zip'
$env:SHINYDEX_BUILD_ROOT = $projectRoot
python (Join-Path $PSScriptRoot 'bundle.py')
if ($LASTEXITCODE -ne 0) { throw 'Static bundle creation failed.' }
$compilerPath = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (!(Test-Path -LiteralPath $compilerPath)) { throw '.NET Framework 4.x compiler was not found.' }
$executablePath = Join-Path $outputDirectory 'ShinyDex.exe'
& $compilerPath /nologo /target:winexe /optimize+ /platform:anycpu "/out:$executablePath" /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll "/resource:$bundlePath,ShinyDex.Web.zip" (Join-Path $PSScriptRoot 'Launcher.cs')
if ($LASTEXITCODE -ne 0) { throw 'Launcher compilation failed.' }
$checksum = (Get-FileHash -LiteralPath $executablePath -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -LiteralPath (Join-Path $outputDirectory 'ShinyDex.exe.sha256') -Value "$checksum  ShinyDex.exe" -Encoding ascii
Write-Output "Built $executablePath"
