# Gerado por 'packaging/gerar_pacotes.py'. Nao edite aqui.
$ErrorActionPreference = 'Stop'

# 'checksum' nao e opcional: sem ele o Chocolatey instala o que baixou,
# seja o que for. Com ele, um arquivo trocado no meio do caminho para a
# instalacao com uma mensagem sobre integridade.
$pacote = @{
  packageName    = 'dataforge'
  fileType       = 'exe'
  url64bit       = 'https://github.com/estevam5s/DataForge/releases/download/v1.1.0/DataForge-1.1.0-windows-x64-setup.exe'
  checksum64     = '0000000000000000000000000000000000000000000000000000000000000000'
  checksumType64 = 'sha256'
  # Os silenciosos do Inno Setup. '/NORESTART' porque reiniciar a
  # maquina de quem rodou um 'choco install' e inaceitavel.
  silentArgs     = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes = @(0)
}

Install-ChocolateyPackage @pacote
