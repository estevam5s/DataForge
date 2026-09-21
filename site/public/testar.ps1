# Bateria de teste do DataForge no Windows — e ela RELATA de volta.
#
# Roda as formas de instalacao uma por uma, grava tudo, e manda o
# relatorio para o host. Nada aqui pede senha nem administrador.

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }
$HOST_LOCAL = 'http://10.0.2.2:8799'
$linhas = New-Object System.Collections.ArrayList

function Nota($texto) {
    [void]$linhas.Add($texto)
    Write-Host $texto
}
function Enviar($texto) {
    # Manda a cada passo, e nao so no fim: um passo que travar deixa o
    # rastro do que JA rodou. A primeira versao mandava uma vez, no
    # final, e quando ela parou no meio nao havia como saber onde.
    try {
        Invoke-WebRequest "$HOST_LOCAL/relatorio" -Method Post `
            -Body ([Text.Encoding]::UTF8.GetBytes($texto)) `
            -ContentType 'text/plain; charset=utf-8' `
            -UseBasicParsing -TimeoutSec 10 | Out-Null
    } catch { }
}

function Passo($nome, $bloco) {
    Nota ""
    Nota "===== $nome ====="
    Enviar "===== $nome ===== (comecou $(Get-Date -Format HH:mm:ss))"
    try {
        $saida = & $bloco 2>&1 | Out-String
        Nota $saida.TrimEnd()
        Nota "[codigo de saida: $LASTEXITCODE]"
        Enviar ($saida.TrimEnd() + "`r`n[codigo: $LASTEXITCODE]")
    } catch {
        Nota "[EXCECAO] $($_.Exception.Message)"
        Enviar "[EXCECAO] $($_.Exception.Message)"
    }
}

Nota "DataForge - teste no Windows"
Nota "data: $(Get-Date -Format s)"
Nota "PowerShell: $($PSVersionTable.PSVersion) ($($PSVersionTable.PSEdition))"
Nota "SO: $((Get-CimInstance Win32_OperatingSystem).Caption)"
Nota "arquitetura: $env:PROCESSOR_ARCHITECTURE"
Nota "TLS antes de tudo: $([Net.ServicePointManager]::SecurityProtocol)"
Nota "politica de execucao: $(Get-ExecutionPolicy)"
Enviar ($linhas -join "`r`n")

# ── 1. O diagnostico, pela forma que a PAGINA manda ─────────
#
# 'irm ... | iex' e o comando que a pagina publica, e ele so funciona se
# a edge servir o script como TEXTO: com application/octet-stream o
# 'irm' devolve bytes, o 'iex' nao tem o que executar, e NAO da erro —
# o prompt volta como se tivesse rodado. Era o estado do
# 'diagnostico.ps1' publicado, e este passo prova a correcao.
Passo "1. diagnostico.ps1 do site, por 'irm | iex'" {
    [Net.ServicePointManager]::SecurityProtocol = 3072
    $u = 'https://dataforge-lang.vercel.app/diagnostico.ps1'
    $tipo = (Invoke-WebRequest $u -Method Head -UseBasicParsing).Headers['Content-Type']
    "Content-Type: $tipo"
    $texto = Invoke-RestMethod $u
    "o que o irm devolveu: $($texto.GetType().Name)"
    Invoke-Expression $texto
}

Passo "1b. diagnostico.ps1 do host, por arquivo" {
    $d = "$env:TEMP\df-diagnostico.ps1"
    Invoke-WebRequest "$HOST_LOCAL/diagnostico.ps1" -OutFile $d -UseBasicParsing
    powershell -NoProfile -ExecutionPolicy Bypass -File $d
}

# ── 2. O TLS, provado nos dois sentidos ─────────────────────
Passo "2. o site do projeto exige TLS 1.2?" {
    foreach ($p in @('Tls', 'Tls12')) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::$p
            $r = Invoke-WebRequest 'https://dataforge-lang.vercel.app/instalar.ps1' `
                 -Method Head -UseBasicParsing -TimeoutSec 20
            "com $p -> HTTP $($r.StatusCode)"
        } catch {
            "com $p -> FALHOU: $($_.Exception.Message.Split([char]10)[0])"
        }
    }
    [Net.ServicePointManager]::SecurityProtocol = 3072
}

# ── 3a. O tarball PUBLICADO (a correcao, no ar) ─────────────
#
# O 'pyproject.toml' mapeia 'dataforge.editor' para a pasta 'editor/', e
# o tarball do site nao a incluia: o 'pip install' morria com "package
# directory 'editor' does not exist" — em TODA maquina, por curl e por
# irm. A correcao esta publicada; este passo cobra que ela funcione pela
# forma que a pagina manda, e nao so no meu host.
Passo "3a. o tarball que o site serve (tem de INSTALAR)" {
    [Net.ServicePointManager]::SecurityProtocol = 3072
    $i = "$env:TEMP\df-instalar-pub.ps1"
    Invoke-WebRequest "$HOST_LOCAL/instalar.ps1" -OutFile $i -UseBasicParsing
    $env:DATAFORGE_SITE = 'https://dataforge-lang.vercel.app'
    $env:DATAFORGE_PREFIX = "$env:TEMP\df-publicado"
    powershell -NoProfile -ExecutionPolicy Bypass -File $i
}

# ── 3b. O tarball CORRIGIDO (servido do host) ───────────────
Passo "3b. o mesmo tarball, servido do host (controle)" {
    [Net.ServicePointManager]::SecurityProtocol = 3072
    $i = "$env:TEMP\df-instalar.ps1"
    Invoke-WebRequest "$HOST_LOCAL/instalar.ps1" -OutFile $i -UseBasicParsing
    $env:DATAFORGE_SITE = $HOST_LOCAL
    $env:DATAFORGE_PREFIX = "$env:USERPROFILE\.dataforge"
    powershell -NoProfile -ExecutionPolicy Bypass -File $i
}

# ── 4. Instalou mesmo? ──────────────────────────────────────
Passo "4. o comando responde" {
    $exe = "$env:USERPROFILE\.dataforge\bin\dataforge.cmd"
    if (Test-Path $exe) {
        & $exe version
    } else {
        $alt = Get-ChildItem "$env:USERPROFILE\.dataforge" -Recurse -Filter 'dataforge*' `
               -ErrorAction SilentlyContinue | Select-Object -First 5
        "nao achei $exe"
        "o que existe: " + ($alt.FullName -join '; ')
    }
}

Passo "5. um programa .df roda" {
    $exe = "$env:USERPROFILE\.dataforge\bin\dataforge.cmd"
    $t = "$env:TEMP\t.df"
    Set-Content $t 'preco := 19.99d
out $"exato: {preco + 0.01d}"
out "acento: coracao, informacao"' -Encoding UTF8
    if (Test-Path $exe) { & $exe run $t } else { "sem o comando" }
}

Passo "6. o PATH do usuario" {
    $u = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($u -like '*dataforge*') { "o PATH do usuario tem o dataforge" }
    else { "o PATH do usuario NAO tem o dataforge" }
}

Passo "7. o .zip portatil (nao precisa de Python)" {
    [Net.ServicePointManager]::SecurityProtocol = 3072
    $zip = "$env:TEMP\df.zip"
    $alvo = "$env:TEMP\df-portatil"
    try {
        Invoke-WebRequest "$HOST_LOCAL/dist/dataforge-windows-x64.zip" `
            -OutFile $zip -UseBasicParsing -TimeoutSec 60
        Remove-Item $alvo -Recurse -Force -ErrorAction SilentlyContinue
        Expand-Archive $zip -DestinationPath $alvo
        $exe = Get-ChildItem $alvo -Recurse -Filter 'dataforge.exe' |
               Select-Object -First 1
        if ($exe) { & $exe.FullName version } else { "o zip nao tem dataforge.exe" }
    } catch {
        "o .zip nao esta no host (ele vem do release): $($_.Exception.Message.Split([char]10)[0])"
    }
}

Passo "8. a forma do cmd.exe" {
    cmd /c "`"$env:USERPROFILE\.dataforge\bin\dataforge.cmd`" version"
}

# ── Manda o relatorio de volta ──────────────────────────────
$texto = ($linhas -join "`r`n")
try {
    Invoke-WebRequest "$HOST_LOCAL/relatorio" -Method Post `
        -Body ([Text.Encoding]::UTF8.GetBytes($texto)) `
        -ContentType 'text/plain; charset=utf-8' -UseBasicParsing | Out-Null
    Write-Host ""
    Write-Host "  relatorio enviado ao host." -ForegroundColor Green
} catch {
    Write-Host "  nao consegui enviar: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  copie a saida acima." -ForegroundColor DarkGray
}
