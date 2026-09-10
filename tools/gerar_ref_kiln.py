#!/usr/bin/env python3
"""
Gera a pagina de referencia do Kiln a partir do proprio modulo.

    python3 tools/gerar_ref_kiln.py

A lista de funcoes e as assinaturas saem de dataforge/stdlib/kiln.py.
Escrever isso a mao garantiria que, um dia, a doc listaria uma funcao
que nao existe mais — ou esconderia uma que existe.
"""

import inspect
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module                        # noqa: E402
from dataforge.stdlib.kiln import RAZOES                       # noqa: E402
from dataforge.tokens import CONTEXTUAIS_KILN                  # noqa: E402

DESTINO = os.path.join(RAIZ, "site", "app", "docs", "kiln",
                       "referencia", "page.tsx")

#: Como agrupar. A ordem aqui e a ordem da pagina.
GRUPOS = [
    ("Aplicação", ["forge", "app", "config", "stats"]),
    ("Rotas", ["route", "get", "post", "put", "patch", "delete", "options",
               "head", "any", "resource", "mount", "group", "routes"]),
    ("Middleware", ["use", "after", "on_error", "cors", "logger",
                    "rate_limit", "auth", "guard"]),
    ("Segurança", ["secure_headers", "cabecalhos_seguros", "csrf",
                   "csrf_token", "limite_de_corpo", "body_limit"]),
    ("Validação", ["validar", "validate", "conferir"]),
    ("Listagem", ["paginar", "ordenar", "buscar"]),
    ("Transferência", ["cache", "comprimir", "idempotente"]),
    ("Observabilidade", ["request_id", "audit", "auditoria"]),
    ("Respostas", ["json", "html", "text", "status", "redirect", "file",
                   "header", "cookie"]),
    ("Sessão", ["session_start", "session_end", "sign", "unsign"]),
    ("Views", ["templates", "render", "render_string", "static", "escape"]),
    ("Ciclo de vida", ["listen", "serve", "stop", "test"]),
]

#: O que cada funcao faz, em uma linha. A docstring do Python e escrita
#: para quem le o runtime; isto e para quem escreve DataForge.
RESUMOS = {
    "forge": "Cria uma aplicação. `Kiln.app` é o mesmo.",
    "app": "Apelido de `forge`.",
    "config": "Ajusta uma opção: `debug`, `limite_corpo`.",
    "stats": "Pedidos, erros, rotas e tempo no ar.",
    "route": "Registra uma rota com o verbo dado.",
    "get": "Registra uma rota GET.",
    "post": "Registra uma rota POST.",
    "put": "Registra uma rota PUT.",
    "patch": "Registra uma rota PATCH.",
    "delete": "Registra uma rota DELETE.",
    "options": "Registra uma rota OPTIONS.",
    "head": "Registra uma rota HEAD.",
    "any": "Registra uma rota que casa qualquer verbo.",
    "resource": "Sete rotas RESTful de uma vez, a partir de um vault "
                "com `index`, `show`, `create`, `update`, `patch` e "
                "`destroy` — só as que existirem.",
    "mount": "Junta as rotas de outro server sob um prefixo.",
    "group": "Sub-app cujas rotas herdam prefixo e middleware.",
    "routes": "Lista as rotas registradas.",
    "use": "Acrescenta um middleware.",
    "after": "Roda com a resposta já pronta.",
    "on_error": "Troca a resposta de um status (404, 500…).",
    "cors": "Libera origens e responde o preflight.",
    "logger": "Uma linha por pedido no terminal.",
    "rate_limit": "429 + `Retry-After` ao estourar o teto por IP.",
    "auth": "401 sem credencial; põe o usuário em `req[\"state\"][\"user\"]`.",
    "guard": "Middleware a partir de uma condição qualquer.",
    "secure_headers": ("Middleware de saída com nosniff, X-Frame-Options, CSP, "
                       "Referrer-Policy e Permissions-Policy. HSTS opcional — "
                       "ligue só com o certificado de pé."),
    "cabecalhos_seguros": "O mesmo que `secure_headers`, em português.",
    "csrf": ("Recusa POST/PUT/PATCH/DELETE sem um token que você assinou. "
             "Métodos seguros passam."),
    "csrf_token": "Um token para pôr no formulário ou no fetch.",
    "limite_de_corpo": ("Recusa corpo acima do teto, com 413. Sem ele, um POST "
                        "de 2 GB derruba o processo sem exploit nenhum."),
    "body_limit": "O mesmo que `limite_de_corpo`, em inglês.",
    "validar": ("Middleware que recusa com 422 o que não casa com o esquema — "
                "e relata **todos** os campos errados de uma vez."),
    "validate": "O mesmo que `validar`, em inglês.",
    "conferir": ("Os problemas do vault, sem responder nada. Para quando o "
                 "campo errado não é 422, e sim um padrão ou uma pergunta."),
    "paginar": ("Uma fatia da lista com `pagina`, `total`, `paginas` e "
                "`tem_proxima`. `por_pagina` tem teto — ele vem de fora."),
    "ordenar": ("Ordena por `?ordenar=campo` ou `-campo`. A lista de campos "
                "permitidos não é conforto: ordenar por um campo que você "
                "nunca expôs revela a ordem dele."),
    "buscar": "Filtra por `?q=` nos campos que você indicar.",
    "cache": "Cache-Control e ETag, com 304 quando o cliente já tem a versão.",
    "comprimir": ("gzip quando o cliente aceita e o corpo compensa. Não toca "
                  "em imagem, vídeo nem zip — já comprimidos."),
    "idempotente": ("Repetir com a mesma `Idempotency-Key` devolve o mesmo "
                    "resultado, em vez de cobrar duas vezes."),
    "request_id": ("Um id por pedido, no estado e na resposta. Mantém o que "
                   "veio do proxy — trocar quebra a corrente."),
    "audit": ("Registra quem mudou o quê. Só métodos que mudam estado, e "
              "**sem o corpo**: ele carrega senha, cartão e token."),
    "auditoria": "O mesmo que `audit`, em português.",
    "json": "Resposta JSON.",
    "html": "Resposta HTML.",
    "text": "Resposta em texto puro.",
    "status": "Só um status, com a frase padrão dele.",
    "redirect": "302 (ou o status que você passar) com `Location`.",
    "file": "Serve um arquivo do disco; `baixar` força o download.",
    "header": "Acrescenta um cabeçalho a uma resposta.",
    "cookie": "Acrescenta um `Set-Cookie`. Já marca `HttpOnly` e `SameSite`.",
    "session_start": "Cria a sessão e devolve a resposta com o cookie.",
    "session_end": "Apaga a sessão e o cookie.",
    "sign": "Token assinado com HMAC-SHA256.",
    "unsign": "Lê um token assinado; `void` se foi adulterado.",
    "templates": "Define a pasta dos templates (o mesmo que `views`).",
    "render": "Renderiza um template e devolve a resposta.",
    "render_string": "Preenche um texto em vez de um arquivo.",
    "static": "Serve uma pasta (o mesmo que `assets`).",
    "escape": "Escapa HTML manualmente.",
    "listen": "Sobe e bloqueia até Ctrl-C (o mesmo que `ignite`).",
    "serve": "Sobe em segundo plano e devolve a porta.",
    "stop": "Desliga um servidor que está no ar.",
    "test": "Executa um pedido direto na aplicação, sem socket.",
}


def assinatura(funcao):
    """A assinatura como quem escreve DataForge a chama."""
    try:
        texto = str(inspect.signature(funcao))
    except (TypeError, ValueError):
        return "(…)"
    # Os parametros internos nao aparecem para quem usa a linguagem.
    return texto.replace("**config", "…")


def conferir_cobertura(modulo):
    listadas = {n for _, nomes in GRUPOS for n in nomes}
    reais = {n for n in modulo if n != "__name__"}
    faltando = reais - listadas
    if faltando:
        raise SystemExit(
            f"funcoes do Kiln fora da referencia: {sorted(faltando)}\n"
            f"acrescente cada uma a GRUPOS e a RESUMOS em "
            f"tools/gerar_ref_kiln.py")
    inventadas = listadas - reais
    if inventadas:
        raise SystemExit(f"a referencia lista o que nao existe: "
                         f"{sorted(inventadas)}")
    sem_resumo = reais - set(RESUMOS)
    if sem_resumo:
        raise SystemExit(f"sem resumo em RESUMOS: {sorted(sem_resumo)}")


def construir():
    modulo = get_module("Kiln")
    conferir_cobertura(modulo)

    blocos = [
        {"p": "Esta página é gerada a partir de `dataforge/stdlib/kiln.py`. "
              f"São **{len(modulo) - 1} funções** — a sintaxe da linguagem "
              "(`server`, `route`, `respond`…) chama estas mesmas."},
        {"h2": "As palavras da linguagem"},
        {"table": {"head": ["Palavra", "Equivale a"], "rows": [
            ["`server nome on porta:`", "`Kiln.forge(nome)`"],
            ["`route GET \"/x\":`", "`Kiln.get(app, \"/x\", handler)`"],
            ["`respond json d`", "`yield Kiln.json(d)`"],
            ["`render \"x\" with d`", "`yield Kiln.render(app, \"x\", d)`"],
            ["`redirect \"/x\"`", "`yield Kiln.redirect(\"/x\")`"],
            ["`middleware m`", "`Kiln.use(app, m)`"],
            ["`mount o at \"/p\"`", "`Kiln.mount(app, \"/p\", o)`"],
            ["`assets \"/p\" from \"d\"`", "`Kiln.static(app, \"/p\", \"d\")`"],
            ["`views \"d\"`", "`Kiln.templates(app, \"d\")`"],
            ["`ignite app on 8080`", "`Kiln.listen(app, 8080)`"],
        ]}},
        {"p": "As dez são **contextuais**: só valem dentro de um bloco "
              "`server`. Fora dali continuam sendo nomes livres."},
    ]

    for titulo, nomes in GRUPOS:
        blocos.append({"h2": titulo})
        linhas = []
        for nome in nomes:
            linhas.append([f"`Kiln.{nome}{assinatura(modulo[nome])}`",
                           RESUMOS[nome]])
        blocos.append({"table": {"head": ["Função", "Faz"], "rows": linhas}})

    blocos.append({"h2": "A requisição"})
    blocos.append({"table": {"head": ["Campo", "É"], "rows": [
        ["`method`", "o verbo, em maiúsculas"],
        ["`path`", "o caminho, já decodificado"],
        ["`params`", "os parâmetros do caminho"],
        ["`query`", "a query string"],
        ["`body`", "o corpo interpretado pelo Content-Type"],
        ["`raw_body`", "o corpo em bytes"],
        ["`headers`", "os cabeçalhos, em minúsculas"],
        ["`cookies`", "os cookies do pedido"],
        ["`session`", "a sessão do visitante"],
        ["`state`", "espaço livre para o middleware"],
        ["`ip`", "o endereço de quem pediu"],
    ]}})

    blocos.append({"h2": "Os status com frase pronta"})
    blocos.append({"p": "`Kiln.status(codigo)` conhece "
                        f"{len(RAZOES)} códigos: " +
                        ", ".join(f"`{c}`" for c in sorted(RAZOES)) + "."})

    corpo = json.dumps(blocos, ensure_ascii=False, indent=2)

    # O sumario lateral sai dos proprios h2, como nas paginas geradas.
    def slug(texto):
        import re
        import unicodedata
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto
                        if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9\s-]", "",
                      texto.lower()).strip().replace(" ", "-")

    titulos = [b["h2"] for b in blocos if "h2" in b]
    cabecalhos = ", ".join(
        "{ id: '%s', text: %s, level: 2 as const }"
        % (slug(t), json.dumps(t, ensure_ascii=False)) for t in titulos)

    return f'''import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

// Gerado por tools/gerar_ref_kiln.py — não edite à mão.

export const metadata: Metadata = {{
  title: "Referência do Kiln",
  description: "As {len(modulo) - 1} funções do módulo e as dez palavras da linguagem.",
}};

const blocos: Bloco[] = {corpo};

const headings = [{cabecalhos}];

export default function Page() {{
  return (
    <DocPage
      title="Referência do Kiln"
      description="As {len(modulo) - 1} funções do módulo e as dez palavras da linguagem."
      href="/docs/kiln/referencia"
      headings={{headings}}
    >
      <Renderer blocos={{blocos}} />
    </DocPage>
  );
}}
'''


def main():
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(construir())
    modulo = get_module("Kiln")
    print(f"referencia gerada: {os.path.relpath(DESTINO, RAIZ)}")
    print(f"  {len(modulo) - 1} funcoes em {len(GRUPOS)} grupos")
    print(f"  {len(CONTEXTUAIS_KILN)} palavras da linguagem")


if __name__ == "__main__":
    main()
