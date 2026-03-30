@echo off
setlocal
title CigerTool Live

set LIVEOS_ROOT=X:\CigerToolLive
set LIVEOS_SHELL=X:\CigerToolLive\shell\Start-CigerToolLiveShell.ps1
set POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe
set LIVEOS_LOG=%LIVEOS_ROOT%\liveos\logs\cigertool.log
set LIVEOS_STATUS=%LIVEOS_ROOT%\liveos\logs\liveos-status.json

if exist "%LIVEOS_SHELL%" (
  if exist "%POWERSHELL_EXE%" (
    echo [CigerTool Live] Canli ortam baslatiliyor...
    "%POWERSHELL_EXE%" -ExecutionPolicy Bypass -File "%LIVEOS_SHELL%"
    if errorlevel 1 (
      echo [CigerTool Live] Live shell hata ile dondu.
    )
    goto :interactive
  )
)

echo [CigerTool Live] Live shell bulunamadi veya baslatilamadi.
:interactive
echo [CigerTool Live] Etkilesimli recovery shell acik kalacak.
echo [CigerTool Live] Log dosyasi: %LIVEOS_LOG%
echo [CigerTool Live] Startup durum dosyasi: %LIVEOS_STATUS%
