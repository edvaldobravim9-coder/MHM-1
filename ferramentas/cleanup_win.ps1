# MHM-1 — Limpeza segura de disco (autorizada pelo usuario em 16/11/2026)
# Escopo: cleanmgr silencioso (se admin). Nao toca em arquivos de usuario.
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Output "Admin: $isAdmin"
if ($isAdmin) {
    $handlers = @('Delivery Optimization Files','Windows Error Reporting Archive Files','Windows Error Reporting Queue Files','Temporary Files')
    foreach ($h in $handlers) {
        $k = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\$h"
        if (Test-Path $k) { Set-ItemProperty -Path $k -Name StateFlags0001 -Value 2 -Type DWord -ErrorAction SilentlyContinue }
    }
    Start-Process cleanmgr -ArgumentList '/sagerun:1' -Wait -NoNewWindow
    Write-Output "cleanmgr concluido"
} else {
    Write-Output "Sem privilegios de administrador - cleanmgr sera pulado (rodar manualmente se desejar)"
}
$free = (Get-PSDrive C).Free
Write-Output ("Livres agora: {0:N2} GB" -f ($free/1GB))
