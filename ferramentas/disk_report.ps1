# MHM-1 — Relatorio de uso de disco (SOMENTE LEITURA — nao apaga nada)
$targets = @(
  'C:\Users\edval\Downloads',
  'C:\Users\edval\Documents',
  'C:\Users\edval\Desktop',
  'C:\Users\edval\Videos',
  'C:\Users\edval\Pictures',
  'C:\Users\edval\Music',
  'C:\Users\edval\AppData\Local\Temp',
  'C:\Users\edval\AppData\Local\pip',
  'C:\Users\edval\AppData\Roaming',
  'C:\Windows',
  'C:\Program Files',
  'C:\Program Files (x86)',
  'C:\ProgramData'
)
Write-Output "=== TAMANHO POR PASTA ==="
foreach ($t in $targets) {
    if (Test-Path $t) {
        $s = (Get-ChildItem $t -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $s) { $s = 0 }
        Write-Output ("{0}`t{1:N2} GB" -f $t, ($s/1GB))
    }
}
Write-Output ""
Write-Output "=== OUTRAS PASTAS NA RAIZ DE C: COM MAIS DE 100 MB ==="
Get-ChildItem C:\ -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $targets -notcontains $_.FullName } |
    ForEach-Object {
        $s = (Get-ChildItem $_.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($s -gt 100MB) { Write-Output ("{0}`t{1:N2} GB" -f $_.FullName, ($s/1GB)) }
    }
Write-Output ""
Write-Output "=== ARQUIVOS DE SISTEMA NA RAIZ ==="
Get-Item C:\hiberfil.sys, C:\pagefile.sys, C:\swapfile.sys -Force -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Output ("{0}`t{1:N2} GB" -f $_.Name, ($_.Length/1GB)) }
Write-Output ""
Write-Output "=== 25 MAIORES ARQUIVOS EM C:\Users\edval ==="
Get-ChildItem C:\Users\edval -Recurse -Force -File -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending | Select-Object -First 25 |
    ForEach-Object { Write-Output ("{0}`t{1:N2} GB" -f $_.FullName, ($_.Length/1GB)) }
$free = (Get-PSDrive C).Free
Write-Output ""
Write-Output ("Livres: {0:N2} GB" -f ($free/1GB))
