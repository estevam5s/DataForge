# Diagnostico da instalacao do DataForge no Windows.
#
#   [Net.ServicePointManager]::SecurityProtocol = 3072
#   irm https://dataforge-lang.vercel.app/diagnostico.ps1 | iex
#
# Ele NAO instala nada. Ele olha as seis coisas que quebram uma
# instalacao no Windows e diz qual delas esta errada — porque
# "a instalacao falhou" nao e uma informacao.
#
# Por que um script separado, e nao uma flag do instalador: quem precisa
# do diagnostico e justamente quem nao conseguiu rodar o instalador.

$ErrorActionPreference = 'Continue'
$VERSAO = '1.1.0'
$SITE   = 'https://dataforge-lang.vercel.app'

# A saida do PowerShell 5.1 e cp1252 por padrao, e um acento basta para
# estourar. Sem esta linha o diagnostico morre ao imprimir o proprio
# relatorio — que e o pior lugar possivel para morrer.
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }

$problemas = @()
$avisos    = @()

function Titulo($texto) {
    Write-Host ""
    Write-Host "  $texto" -ForegroundColor Cyan
}
function Bom($texto)  { Write-Host "   [ok]   $texto" -ForegroundColor Green }
function Mau($texto, $comoResolver) {
    Write-Host "   [ERRO] $texto" -ForegroundColor Red
    if ($comoResolver) { Write-Host "          $comoResolver" -ForegroundColor DarkGray }
    $script:problemas += $texto
}
function Talvez($texto, $nota) {
    Write-Host "   [ !  ] $texto" -ForegroundColor Yellow
    if ($nota) { Write-Host "          $nota" -ForegroundColor DarkGray }
    $script:avisos += $texto
}

Write-Host ""
Write-Host "  DataForge $VERSAO — diagnostico do Windows" -ForegroundColor White

# ── 1. A versao do PowerShell ───────────────────────────────
#
# O 5.1 e o que vem no Windows 10 e 11 como 'powershell.exe'. Ele
# funciona, e tem duas armadilhas que o 7 nao tem: TLS 1.0 por padrao e
# cp1252 na saida. Saber qual esta rodando muda o resto do diagnostico.
Titulo "1. PowerShell"
$v = $PSVersionTable.PSVersion
Write-Host "          versao $v ($($PSVersionTable.PSEdition))"
if ($v.Major -ge 7) {
    Bom "PowerShell 7+: TLS e codificacao ja vem certos"
} elseif ($v.Major -eq 5) {
    Bom "Windows PowerShell 5.1 — suportado"
    Talvez "o 5.1 negocia TLS 1.0 por padrao" `
           "e por isso toda linha de instalacao comeca com '[Net.ServicePointManager]::SecurityProtocol = 3072'"
} else {
    Mau "PowerShell $v e antigo demais" `
        "instale o PowerShell 7: winget install Microsoft.PowerShell"
}

# ── 2. O TLS que ele negocia ────────────────────────────────
#
# Esta e a causa numero um: o host do site recusa TLS abaixo de 1.2, e o
# 5.1 oferece 1.0. O erro que aparece — "Could not create SSL/TLS secure
# channel" — nao menciona TLS versao nenhuma.
Titulo "2. TLS"
$protocolo = [Net.ServicePointManager]::SecurityProtocol
Write-Host "          negociando: $protocolo"
if ($protocolo -band [Net.SecurityProtocolType]::Tls12) {
    Bom "TLS 1.2 esta habilitado nesta sessao"
} else {
    Mau "TLS 1.2 NAO esta habilitado nesta sessao" `
        "rode antes: [Net.ServicePointManager]::SecurityProtocol = 3072"
}

# ── 3. A politica de execucao ───────────────────────────────
Titulo "3. Politica de execucao"
$politica = Get-ExecutionPolicy
Write-Host "          $politica"
if ($politica -in @('Restricted', 'AllSigned')) {
    Talvez "'$politica' recusa script baixado" `
           "use 'irm ... | iex' (que nao passa por arquivo), ou rode: powershell -ExecutionPolicy Bypass -File .\instalar.ps1"
} else {
    Bom "'$politica' permite rodar o instalador"
}

# ── 4. O site responde? ─────────────────────────────────────
#
# Separado do TLS de proposito: uma coisa e o protocolo, outra e a rede.
# Um proxy de empresa falha aqui com TLS 1.2 perfeitamente habilitado.
Titulo "4. Rede"
foreach ($alvo in @("$SITE/instalar.ps1", "$SITE/dist/dataforge-$VERSAO.tar.gz")) {
    try {
        $r = Invoke-WebRequest -Uri $alvo -Method Head -UseBasicParsing -TimeoutSec 20
        Bom "$alvo -> HTTP $($r.StatusCode)"
    } catch {
        Mau "nao alcancei $alvo" `
            "$($_.Exception.Message)"
    }
}

# ── 5. Python ───────────────────────────────────────────────
#
# O instalador .ps1 cria um venv, e por isso precisa de Python. O .exe e
# o .zip NAO precisam — eles embutem o runtime. Se falta Python, o
# caminho certo e o instalador grafico, e nao 'instale Python primeiro'.
Titulo "5. Python (so o instalador .ps1 precisa)"
$python = $null
foreach ($nome in @('python', 'python3', 'py')) {
    $achado = Get-Command $nome -ErrorAction SilentlyContinue
    if ($achado) { $python = $achado; break }
}
if (-not $python) {
    Talvez "nao ha Python no PATH" `
           "nao e um problema: baixe o instalador grafico (.exe) ou o .zip — os dois embutem o runtime. $SITE/download"
} else {
    $versao = & $python.Source -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
    if ($versao -and [version]"$versao" -ge [version]'3.10') {
        Bom "Python $versao em $($python.Source)"
    } else {
        Talvez "Python $versao e antigo (o minimo e 3.10)" `
               "use o instalador grafico, ou atualize o Python"
    }
    # A armadilha da Microsoft Store: um 'python.exe' que so abre a loja.
    if ($python.Source -like '*WindowsApps*') {
        Talvez "este 'python' e o atalho da Microsoft Store" `
               "ele abre a loja em vez de rodar; instale o Python de python.org, ou use o .exe do DataForge"
    }
}

# ── 6. Ja esta instalado? ───────────────────────────────────
Titulo "6. DataForge nesta maquina"
$df = Get-Command dataforge -ErrorAction SilentlyContinue
if ($df) {
    $saida = & $df.Source version 2>&1 | Select-Object -First 1
    Bom "$saida  ($($df.Source))"
} else {
    $provavel = Join-Path $env:USERPROFILE '.dataforge\bin\dataforge.cmd'
    if (Test-Path $provavel) {
        Talvez "esta instalado em $provavel, e NAO esta no PATH" `
               "abra um terminal NOVO — o PATH so vale para sessoes abertas depois da instalacao"
    } else {
        Write-Host "          nao instalado (era o esperado, se voce esta diagnosticando)"
    }
}

# ── O veredito ──────────────────────────────────────────────
Write-Host ""
if ($problemas.Count -eq 0 -and $avisos.Count -eq 0) {
    Write-Host "  Nada a corrigir: a instalacao deve funcionar." -ForegroundColor Green
} elseif ($problemas.Count -eq 0) {
    Write-Host "  Nenhum impedimento. $($avisos.Count) aviso(s) acima." -ForegroundColor Yellow
} else {
    Write-Host "  $($problemas.Count) problema(s) impedem a instalacao:" -ForegroundColor Red
    foreach ($p in $problemas) { Write-Host "    - $p" -ForegroundColor Red }
}
Write-Host ""
Write-Host "  Formas de instalar, com o que cada uma exige:" -ForegroundColor Cyan
Write-Host "    $SITE/download" -ForegroundColor DarkGray
Write-Host ""

# O codigo de saida serve a quem chama de um script: 0 quando nada
# impede, 1 quando algo impede.
if ($problemas.Count -gt 0) { exit 1 } else { exit 0 }
