"""O registro da comunidade, falado pelo terminal.

    dataforge login                 guarda o token
    dataforge publish --remoto      empacota e envia
    dataforge add <nome>            baixa, confere o hash, instala

O que muda em relação ao `publish` local
----------------------------------------
`dataforge publish --registry=<pasta>` escreve num índice estático e
espera um PR. Serve para um registro interno de empresa, e não serve
para a comunidade: ninguém abre um PR para publicar um pacote.

Aqui a publicação é uma chamada de rede autenticada por **token**, e o
pacote entra na fila de revisão. O `add` continua lendo o índice
estático — ele é gerado a partir do que foi aprovado, e um índice
estático é o que permite instalar sem depender de um serviço de pé.

Três decisões
-------------
1. **O token fica em `~/.dataforge/credenciais.json`, com modo 600.**
   Num arquivo do projeto ele acabaria commitado — é a forma mais comum
   de vazar credencial de registro de pacote que existe.

2. **`login` CONFERE o token antes de gravar.** Sem isso o erro só
   apareceria no primeiro `publish`, longe do comando que o causou.

3. **O tarball não sobe por aqui.** O que se envia é o ENDEREÇO dele e
   o sha256. Hospedar binário exige um serviço com cota, expiração e
   política de abuso; um release do GitHub já faz isso melhor, e o
   hash é o que torna a origem irrelevante — se o conteúdo mudar, o
   `add` recusa.
"""

import json
import os
import ssl
import urllib.error
import urllib.request

from .errors import RuntimeError_

#: O serviço que guarda o registro da comunidade.
#:
#: Sobrescritível para quem roda o próprio: a linguagem não pode
#: obrigar ninguém a publicar num lugar só.
API_PADRAO = os.environ.get("DATAFORGE_API", "https://teimsogvbhllhzkvioam.supabase.co")

#: A chave PÚBLICA do projeto.
#:
#: Ela já vai no bundle do site (`NEXT_PUBLIC_…`), e o navegador de
#: qualquer visitante a enxerga. Embuti-la aqui não expõe nada novo: o
#: que protege os dados é a RLS, e não o segredo desta chave. A chave
#: `service_role`, que ignora RLS, nunca entra em lugar nenhum que seja
#: distribuído.
CHAVE_PADRAO = os.environ.get(
    "DATAFORGE_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlaW1zb2d2YmhsbGh6a3Zpb2FtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg4MTM5OTIsImV4cCI6MjEwNDM4OTk5Mn0.0_ZtGzWaYXkRrijJubIodeAJpVSiIC5Mz48mHCjfsmM")


class ErroDeRegistro(RuntimeError_):
    CODIGO = "DF1301"


def _pasta_de_credenciais():
    return os.path.join(os.path.expanduser("~"), ".dataforge")


def caminho_das_credenciais():
    return os.path.join(_pasta_de_credenciais(), "credenciais.json")


def ler_token():
    """O token guardado, ou None.

    A variável de ambiente vence o arquivo: é como a CI passa a
    credencial sem escrever nada em disco.
    """
    do_ambiente = os.environ.get("DATAFORGE_TOKEN")
    if do_ambiente:
        return do_ambiente.strip()

    caminho = caminho_das_credenciais()
    if not os.path.isfile(caminho):
        return None
    try:
        with open(caminho, encoding="utf-8") as f:
            return (json.load(f) or {}).get("token")
    except (OSError, ValueError):
        return None


def gravar_token(token):
    """Guarda o token, só para o dono ler."""
    pasta = _pasta_de_credenciais()
    os.makedirs(pasta, exist_ok=True)
    caminho = caminho_das_credenciais()

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"token": token}, f)

    # 600: um arquivo de credencial legível por outros usuários da
    # máquina é uma credencial compartilhada sem que ninguém tenha
    # decidido isso.
    _so_para_o_dono(caminho)
    return caminho


def _so_para_o_dono(caminho):
    """Tira o arquivo do alcance dos outros usuários da máquina.

    No Unix isso é o modo 600. **No Windows, `os.chmod` não faz isso**:
    ele liga e desliga o atributo de somente-leitura, e mais nada — o
    arquivo continua legível por qualquer conta da máquina. A promessa
    ficava escrita no comentário e não valia no sistema em que mais
    gente compartilha o computador.

    A restrição de verdade ali é a ACL, e quem a escreve é o `icacls`
    que vem com o sistema: `/inheritance:r` corta o que a pasta
    concedia, e `/grant:r <usuário>:F` deixa só o dono. O Python não
    expõe isso na biblioteca padrão.

    Devolve `True` quando conseguiu restringir — quem chama não
    precisa saber por qual dos dois caminhos.
    """
    if os.name != "nt":
        try:
            os.chmod(caminho, 0o600)
            return True
        except OSError:
            return False

    import subprocess

    dono = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if not dono:
        return False
    try:
        r = subprocess.run(
            ["icacls", caminho, "/inheritance:r", "/grant:r", f"{dono}:F"],
            capture_output=True, text=True, timeout=20,
            # O 'icacls' escreve na pagina de codigo do console, e nao
            # em UTF-8: sem dizer a codificacao, o Python leria cp1252 e
            # um nome de usuario com acento estouraria a leitura.
            encoding="utf-8", errors="replace")
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def esquecer_token():
    caminho = caminho_das_credenciais()
    if os.path.isfile(caminho):
        os.remove(caminho)
        return True
    return False


def _chamar(funcao, corpo, prazo=30):
    """Uma função do registro, por HTTP."""
    if not CHAVE_PADRAO:
        raise ErroDeRegistro(
            "the registry key is not configured.",
            nota="DATAFORGE_API_KEY carrega a chave pública do serviço",
            dica="ela vem junto na instalação oficial; num ambiente "
                 "próprio, aponte DATAFORGE_API e DATAFORGE_API_KEY para "
                 "o seu",
            doc="pacotes/publicar")

    dados = json.dumps(corpo).encode("utf-8")
    req = urllib.request.Request(
        f"{API_PADRAO.rstrip('/')}/rest/v1/rpc/{funcao}",
        data=dados,
        headers={
            "apikey": CHAVE_PADRAO,
            "Authorization": f"Bearer {CHAVE_PADRAO}",
            "Content-Type": "application/json",
        },
    )
    contexto = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=prazo,
                                    context=contexto) as r:
            texto = r.read().decode("utf-8")
            return json.loads(texto) if texto.strip() else None
    except urllib.error.HTTPError as e:
        corpo_erro = e.read().decode("utf-8", "replace")
        try:
            detalhe = json.loads(corpo_erro)
            mensagem = detalhe.get("message") or corpo_erro
            dica = detalhe.get("hint") or ""
        except ValueError:
            mensagem, dica = corpo_erro[:200], ""
        raise ErroDeRegistro(mensagem, dica=dica,
                             doc="pacotes/publicar") from None
    except urllib.error.URLError as e:
        raise ErroDeRegistro(
            f"could not reach the registry: {e.reason}",
            nota="o registro fica fora da sua máquina",
            dica="confira a rede, ou aponte DATAFORGE_API para outro",
            doc="pacotes/publicar") from None


def conferir(token):
    """O token vale? Devolve vault com 'valido' e o que ele alcança."""
    return _chamar("conferir_token", {"p_token": token}) or {"valido": False}


def publicar(token, metadados):
    """Envia o pacote para a fila de revisão."""
    return _chamar("publicar_com_token", {
        "p_token": token,
        "p_nome": metadados["nome"],
        "p_versao": metadados["versao"],
        "p_descricao": metadados["descricao"],
        "p_tarball": metadados["tarball"],
        "p_sha256": metadados["sha256"],
        "p_licenca": metadados.get("licenca", "MIT"),
        "p_repositorio": metadados.get("repositorio"),
        "p_documentacao": metadados.get("documentacao"),
        "p_palavras": metadados.get("palavras", []),
    })


def registro_publico():
    """O que já foi aprovado — o mesmo que o site serve."""
    return _chamar("registro_publico", {}) or []
