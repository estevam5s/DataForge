<#
    Instalador do DataForge para Windows.

        irm https://dataforge-lang.vercel.app/instalar.ps1 | iex

    Variáveis (opcionais, antes de rodar):
        $env:DATAFORGE_VERSION = "1.0.0"
        $env:DATAFORGE_PREFIX  = "$HOME\.dataforge"
#>

$ErrorActionPreference = 'Stop'

$Versao  = if ($env:DATAFORGE_VERSION) { $env:DATAFORGE_VERSION } else { '1.0.0' }
$Prefixo = if ($env:DATAFORGE_PREFIX)  { $env:DATAFORGE_PREFIX }  else { "$HOME\.dataforge" }
$Site    = if ($env:DATAFORGE_SITE)    { $env:DATAFORGE_SITE }    else { 'https://dataforge-lang.vercel.app' }

function Info($m)  { Write-Host "==> " -ForegroundColor Cyan -NoNewline; Write-Host $m }
function Ok($m)    { Write-Host "  ok " -ForegroundColor Green -NoNewline; Write-Host $m }
function Aviso($m) { Write-Host "  !  " -ForegroundColor Yellow -NoNewline; Write-Host $m }
function Erro($m)  { Write-Host "erro: $m" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  DataForge" -ForegroundColor Cyan -NoNewline
Write-Host " · linguagem de programação · v$Versao" -ForegroundColor DarkGray
Write-Host ""

# ── Python ──────────────────────────────────────────────────

$Python = $null
foreach ($candidato in @('python', 'python3', 'py')) {
    try {
        $saida = & $candidato -c 'import sys; print(sys.version_info[:2])' 2>$null
        if ($LASTEXITCODE -eq 0) {
            $ok = & $candidato -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { $Python = $candidato; break }
        }
    } catch { }
}

if (-not $Python) {
    Erro @"
não achei Python 3.10 ou mais novo.

Instale de uma destas formas:
  winget install Python.Python.3.12
  https://python.org/downloads

Marque 'Add Python to PATH' durante a instalação,
abra um terminal novo e rode este instalador de novo.
"@
}
Ok "python: $(& $Python --version)"

# ── Ambiente virtual ────────────────────────────────────────

Info "instalando em $Prefixo"
if (Test-Path $Prefixo) {
    Aviso "já existe — substituindo"
    Remove-Item -Recurse -Force $Prefixo
}
New-Item -ItemType Directory -Path $Prefixo -Force | Out-Null

& $Python -m venv "$Prefixo\venv"
if ($LASTEXITCODE -ne 0) { Erro "não consegui criar o ambiente virtual" }
Ok "ambiente virtual criado"

$Pip = "$Prefixo\venv\Scripts\pip.exe"

# ── Download ────────────────────────────────────────────────

Info "baixando o DataForge $Versao"
$Temp    = Join-Path ([System.IO.Path]::GetTempPath()) "dataforge-$(Get-Random)"
New-Item -ItemType Directory -Path $Temp -Force | Out-Null
$Arquivo = "$Temp\dataforge.tar.gz"

$origens = @(
    "$Site/dist/dataforge-$Versao.tar.gz",
    "https://github.com/estevam5s/DataForge/archive/refs/tags/v$Versao.tar.gz",
    "https://github.com/estevam5s/DataForge/archive/refs/heads/main.tar.gz"
)

$baixou = $false
foreach ($url in $origens) {
    try {
        Invoke-WebRequest -Uri $url -OutFile $Arquivo -UseBasicParsing
        Ok "baixado de $([System.Uri]$url).Host"
        $baixou = $true
        break
    } catch { }
}
if (-not $baixou) {
    Erro "não consegui baixar o DataForge $Versao. Confira sua conexão."
}

# tar faz parte do Windows 10 build 17063 em diante
$Fonte = "$Temp\fonte"
New-Item -ItemType Directory -Path $Fonte -Force | Out-Null
tar -xzf $Arquivo -C $Fonte --strip-components=1
if ($LASTEXITCODE -ne 0) { Erro "falha ao descompactar" }
Ok "código baixado"

# ── Instalação ──────────────────────────────────────────────

Info "instalando"
& $Pip install --quiet $Fonte
if ($LASTEXITCODE -ne 0) { Erro "a instalação falhou" }
Ok "pacote instalado"

New-Item -ItemType Directory -Path "$Prefixo\bin" -Force | Out-Null
foreach ($nome in @('dataforge', 'df')) {
    @"
@echo off
"$Prefixo\venv\Scripts\dataforge.exe" %*
"@ | Set-Content -Path "$Prefixo\bin\$nome.cmd" -Encoding ASCII
}
Ok "comandos: dataforge, df"

# ── PATH do usuário ─────────────────────────────────────────

$PathUsuario = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($PathUsuario -notlike "*$Prefixo\bin*") {
    [Environment]::SetEnvironmentVariable(
        'Path', "$Prefixo\bin;$PathUsuario", 'User')
    Ok "adicionado ao PATH do usuário"
    $novoTerminal = $true
}

$env:Path = "$Prefixo\bin;$env:Path"
$versaoInstalada = & "$Prefixo\bin\dataforge.cmd" version 2>&1 | Select-Object -First 1

# Coloracao no VS Code. Sem editor instalado o comando avisa e sai — nao
# e motivo para a instalacao inteira falhar.
if (-not $env:DATAFORGE_SEM_EDITOR) {
    & "$Prefixo\bin\dataforge.cmd" editor *> $null
    if ($LASTEXITCODE -eq 0) { Ok "coloração de sintaxe instalada no editor" }
}

Write-Host ""
Write-Host "  $versaoInstalada instalado" -ForegroundColor Green
Write-Host ""
if ($novoTerminal) {
    Write-Host "  Abra um terminal novo para o PATH valer." -ForegroundColor Yellow
    Write-Host ""
}
Write-Host "  Comece por:"
Write-Host "    dataforge repl" -ForegroundColor Cyan
Write-Host "    dataforge init meu-projeto" -ForegroundColor Cyan
Write-Host ""
Write-Host "  documentação: https://dataforge-lang.vercel.app/docs" -ForegroundColor DarkGray
Write-Host "  desinstalar:  Remove-Item -Recurse -Force $Prefixo" -ForegroundColor DarkGray
Write-Host ""
