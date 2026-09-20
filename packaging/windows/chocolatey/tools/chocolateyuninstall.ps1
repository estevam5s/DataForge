# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
$ErrorActionPreference = 'Stop'

# O Inno Setup deixa o proprio desinstalador; o registro e que diz onde.
$chave = Get-ChildItem -Path @(
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
  'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
) -ErrorAction SilentlyContinue |
  Where-Object { $_.GetValue('DisplayName') -like 'DataForge*' } |
  Select-Object -First 1

if (-not $chave) {
  Write-Host 'DataForge nao esta instalado por aqui.'
  return
}

$desinstalador = $chave.GetValue('UninstallString')
Uninstall-ChocolateyPackage -PackageName 'dataforge' -FileType 'exe' `
  -SilentArgs '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' -File $desinstalador
