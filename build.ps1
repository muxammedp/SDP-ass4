param([string]$JavaHome = $env:JAVA_HOME)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not $JavaHome) {
    $localJdk = Get-ChildItem -Path "$PSScriptRoot\.tools\jdk*" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($localJdk) { $JavaHome = $localJdk.FullName }
}
if ($JavaHome) {
    $compiler = Join-Path $JavaHome 'bin\javac.exe'
    $runtime = Join-Path $JavaHome 'bin\java.exe'
} else {
    $compiler = (Get-Command javac -ErrorAction Stop).Source
    $runtime = Join-Path (Split-Path $compiler) 'java.exe'
}
New-Item -ItemType Directory -Force out | Out-Null
& $compiler --release 17 -encoding UTF-8 -Xlint:all -Werror -d out '@sources.txt' tests/FacadeTests.java
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed.' }
& $runtime -cp out FacadeTests
if ($LASTEXITCODE -ne 0) { throw 'Verification failed.' }
