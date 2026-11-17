# MHM-1 — Limpeza oficial do Windows (requer admin, executada via UAC)
# Escopo: apenas mecanismos oficiais de limpeza (cleanmgr, SoftwareDistribution, DISM).
# NAO toca em arquivos de usuario (Downloads, Documentos, Desktop, etc).
$ErrorActionPreference = 'Continue'
$log = 'C:\Users\edval\Desktop\MHM-1\registros\limpeza_admin.log'
Start-Transcript -Path $log -Force

$free0 = (Get-PSDrive C).Free
Write-Output ("=== LIMPEZA ADMIN MHM-1 - livre antes: {0:N2} GB ===" -f ($free0/1GB))

# 1) Limpeza de disco silenciosa (itens oficiais e seguros)
$handlers = @(
  'Delivery Optimization Files',
  'Windows Error Reporting Archive Files',
  'Windows Error Reporting Queue Files',
  'Windows Error Reporting System Archive Files',
  'Windows Error Reporting System Queue Files',
  'Temporary Files',
  'Temporary Setup Files',
  'Windows Upgrade Log Files',
  'Update Cleanup'
)
foreach ($h in $handlers) {
    $k = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\$h"
    if (Test-Path $k) { Set-ItemProperty -Path $k -Name StateFlags0001 -Value 2 -Type DWord }
}
Write-Output "Executando cleanmgr /sagerun:1 (pode demorar)..."
Start-Process cleanmgr -ArgumentList '/sagerun:1' -Wait -NoNewWindow
Write-Output "cleanmgr concluido."

# 2) Cache de downloads do Windows Update
Write-Output "Limpando SoftwareDistribution\Download..."
Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item 'C:\Windows\SoftwareDistribution\Download\*' -Recurse -Force -ErrorAction SilentlyContinue
Start-Service wuauserv -ErrorAction SilentlyContinue
Write-Output "Cache do Windows Update limpo."

# 3) Component Store (WinSxS) - limpeza oficial, SEM /ResetBase
Write-Output "Executando DISM /StartComponentCleanup (pode demorar 10-20 min)..."
DISM.exe /Online /Cleanup-Image /StartComponentCleanup
Write-Output "DISM concluido."

$free1 = (Get-PSDrive C).Free
Write-Output ("=== FIM - livre depois: {0:N2} GB | liberado: {1:N2} GB ===" -f ($free1/1GB), (($free1-$free0)/1GB))
Stop-Transcript
